from django.shortcuts import render, get_object_or_404, redirect
from .models import Hotel, Room, Commodity, RoomCommodity, RoomType
from django.db.models import Q, Count, Sum, OuterRef, Subquery
from .forms import HotelForm, RoomForm, CommodityForm
from reservation.models import RoomReservation, Reservation
from django.http import Http404
from django.db.models import Min
from django.db import connection
from hotel_management.models import HotelEmployees, Hotel
from main.mongo_utils import get_number_of_reviews, get_files_by_postgres_id, upload_file_with_metadata, get_cover_image
import sweetify

def hotel_list(request):
    query = request.GET.get('q', '')
    sort = request.GET.get('sort', 'h_name')  
    order = request.GET.get('order', 'asc')  

    # Determina o campo de ordenação e a ordem
    sort_field = sort if order == 'asc' else f'-{sort}'

    # Retorna o valor total das reservas associadas ao hotel
    reservation_total_value = Reservation.objects.filter(
        room_reservations__room__hotel=OuterRef('pk')
    ).annotate(
        total_value_sum=Sum('room_reservations__price_reservation')
    ).values('total_value_sum')

    # Agrega os resultados dos hotéis
    hotels = Hotel.objects.annotate(
        room_count=Count('room'),   
        total_value=Subquery(reservation_total_value[:1])   
    ).filter(
        Q(h_name__icontains=query) | Q(city__icontains=query)
    ) if query else Hotel.objects.annotate(
        room_count=Count('room'),
        total_value=Subquery(reservation_total_value[:1])
    )

    # Aplica a ordenação
    hotels = hotels.order_by(sort_field)
    hotel_employee = HotelEmployees.objects.filter(employee=request.user)

    # Filtra os hotéis associados ao funcionário logado
    if hotel_employee:
        hotels = hotels.filter(id=hotel_employee[0].hotel.id)

    return render(request, 'hotel_management/hotels.html', {
        'hotels': hotels,
        'sort': sort,
        'order': order,
    })

# View for adding or editing a hotel
def hotel_form(request, hotel_id=None):
    if hotel_id:
        # Fetch the hotel by ID for editing
        hotel = get_object_or_404(Hotel, id=hotel_id)
        files = get_files_by_postgres_id(hotel_id)
        for file in files:
            file.id_str = str(file._id)
        heading = "Editar Hotel"
    else:
        # Initialize a new hotel for addition
        hotel = None  # No instance for new entries
        heading = "Adicionar Hotel"

    if request.method == 'POST':
        # Include request.FILES to handle file uploads
        form = HotelForm(request.POST, request.FILES, instance=hotel)
        if form.is_valid():
            data = form.cleaned_data
            uploaded_file = request.FILES.get('file')  
            
            try:
                with connection.cursor() as cursor: 
                    cursor.execute("""
                        CALL sp_add_hotel(%s, %s, %s, %s, %s, %s, %s, %s)
                    """, [
                        data['h_name'], data['full_address'], data['postal_code'],
                        data['city'], data['email'], data['telephone'],
                        data.get('details', ''), data.get('stars', 0)
                    ])

                # Handle the uploaded file (Save to MongoDB or filesystem)
                if uploaded_file:
                    fileup = upload_file_with_metadata(uploaded_file, uploaded_file.name, hotel_id)
                    if not fileup:
                        sweetify.error(request, title='Error', text='Erro ao fazer upload do arquivo.', persistent='Ok')
                        return redirect('hotel_list')

                sweetify.success(request, title='Success', text='Hotel adicionado com sucesso!', persistent='Ok')
                return redirect('hotel_list')

            except Exception as e:
                sweetify.error(request, title='Error', text='Ocorreu um erro ao adicionar o hotel.', persistent='Ok')
        else:
            sweetify.error(request, title='Error', text='Ocorreu um erro ao adicionar o hotel.', persistent='Ok')
    else:
        form = HotelForm(instance=hotel)
 
    return render(request, 'hotel_management/hotel_form.html', {
        'form': form,
        'heading': heading, 
        'files': files if hotel_id else []
    })

def edit_hotel(request, hotel_id):
    hotel = get_object_or_404(Hotel, id=hotel_id)
    heading = "Editar Hotel"
    files = get_files_by_postgres_id(hotel_id)
    for file in files:
        file.id_str = str(file._id)

    if request.method == 'POST':
        form = HotelForm(request.POST, instance=hotel)
        if form.is_valid():
            uploaded_file = request.FILES.get('file')
            form.save()  # Salva os dados diretamente no banco de dados
            if uploaded_file:
                fileup = upload_file_with_metadata(uploaded_file, uploaded_file.name, hotel_id)
                if not fileup:
                    messages.error(request, "Erro ao fazer upload do arquivo.")
                    return redirect('hotel_list')
            sweetify.success(request, title='Success', text='Hotel editado com sucesso!', persistent='Ok')
            return redirect('hotel_list')
        else:
            sweetify.error(request, title='Error', text='Ocorreu um erro ao editar o hotel.', persistent='Ok')
    else:
        form = HotelForm(instance=hotel)

    return render(request, 'hotel_management/hotel_form.html', {
        'form': form,
        'heading': heading, 
        'files':  files
    })

# View para apagar um hotel
def delete_hotel(request, hotel_id):
    # obtem o hotel pelo id ou retorna um erro 404 caso não exista
    hotel = get_object_or_404(Hotel, id=hotel_id)

    # Verifica se existem reservas associadas ao hotel
    reservations_exist = RoomReservation.objects.filter(room__hotel=hotel).exists()

    if reservations_exist:
        # Mensagem de erro caso existam reservas associadas ao hotel
        sweetify.error(request, title='Error', text='Não é possível apagar este hotel, pois existem reservas associadas aos quartos.', persistent='Ok')
        return redirect('hotel_list')   
    else:
        # Se nao existirem reservas associadas ao hotel, apaga o hotel
        if request.method == 'POST':
            hotel.delete()
            sweetify.success(request, title='Success', text='Hotel apagado com sucesso!', persistent='Ok')
            return redirect('hotel_list')
        else:
            # Mensagem de confirmação de apagar hotel
            return render(request, 'hotel_management/confirm_delete.html', {'hotel': hotel})
        
def room_list(request, hotel_id):
    hotel = get_object_or_404(Hotel, id=hotel_id)
    type_name = request.GET.get('type_initials', '')
    sort = request.GET.get('sort', 'room_number')  # Define a ordenação inicial por número do quarto
    order = request.GET.get('order', 'asc')  # Define a direção de ordenação

    rooms = Room.objects.filter(hotel=hotel)

    if type_name:
        rooms = rooms.filter(type__type_initials__icontains=type_name)

    # Determina o campo de ordenação e a ordem
    sort_field = sort if order == 'asc' else f'-{sort}'

    # Ordena os quartos com base no campo e direção
    rooms = rooms.order_by(sort_field)

    return render(request, 'hotel_management/hotel_rooms.html', {
        'hotel': hotel,
        'rooms': rooms,
        'sort': sort,
        'order': order,
    })

def all_room_list(request):
    # Recupera o hotel associado ao funcionário logado
    hotel_employee = get_object_or_404(HotelEmployees, employee=request.user)
    hotel = hotel_employee.hotel  # Hotel associado ao usuário logado

    type_name = request.GET.get('type_initials', '')  # Filtro por tipo de quarto
    sort = request.GET.get('sort', 'room_number')  # Define a ordenação inicial por número do quarto
    order = request.GET.get('order', 'asc')  # Define a direção de ordenação

    # Filtra os quartos com base no hotel associado ao usuário logado
    rooms = Room.objects.filter(hotel=hotel)

    if type_name:
        rooms = rooms.filter(type__type_initials__icontains=type_name)

    # Determina o campo de ordenação e a ordem
    sort_field = sort if order == 'asc' else f'-{sort}'

    # Ordena os quartos com base no campo e direção
    rooms = rooms.order_by(sort_field)

    return render(request, 'hotel_management/hotel_rooms.html', {
        'hotel': hotel,
        'rooms': rooms,
        'sort': sort,
        'order': order,
    })

def create_room(request, hotel_id):
    # Obtém o hotel ou retorna 404 se não existir
    hotel = get_object_or_404(Hotel, id=hotel_id)
    commodities = Commodity.objects.all()

    if request.method == 'POST':
        form = RoomForm(request.POST)
        selected_commodities = request.POST.getlist('commodities')

        if form.is_valid():
            room_type_id = request.POST.get('room_type')
            room_type = RoomType.objects.get(id=room_type_id).type_initials or ''   #TODO
            room_number = form.cleaned_data.get('room_number')
            base_price = form.cleaned_data.get('base_price')
            condition = form.cleaned_data.get('condition')

            # Creating a new commodity
            with connection.cursor() as cursor:
                cursor.execute("""
                    CALL sp_add_room(%s,%s,%s,%s,%s);
                """, [hotel_id, room_type, room_number, base_price, condition])
            sweetify.success(request, title='Success', text='Quarto adicionado com sucesso!', persistent='Ok')

            with connection.cursor() as cursor:
                cursor.execute('SELECT MAX(id) FROM "room_management.room";')
                room_id = cursor.fetchone()[0]

                print('room_id')
                print(room_id)
            
            with connection.cursor() as cursor:
                for commodity_id in selected_commodities:
                    cursor.execute("""
                        CALL sp_link_commodity_to_room(%s, %s);
                    """, [room_id, commodity_id])

            return redirect('room_list', hotel_id=hotel.id)  # Redireciona para a lista de quartos
    else:
        form = RoomForm()

    return render(request, 'hotel_management/room_form.html', {
        'commodities': commodities,
        'selected_commodities': [],
        'form': form,
        'hotel': hotel,
        'room': None,  # Define como None, já que o quarto ainda não existe
    })

def edit_room(request, hotel_id, room_id):
    room = get_object_or_404(Room, id=room_id, hotel_id=hotel_id)
    commodities = Commodity.objects.all()
    selected_commodities = list(RoomCommodity.objects.filter(room_id=room_id).values_list('commodity_id', flat=True)) or []

    if request.method == 'POST':
        form = RoomForm(request.POST, instance=room)
        selected_commodities = request.POST.getlist('commodities')

        if form.is_valid():
            updated_room = form.save()

            RoomCommodity.objects.filter(room_id=updated_room.id).delete()

            room_id = updated_room.id
            with connection.cursor() as cursor:
                for commodity_id in selected_commodities:
                    cursor.execute("""
                        CALL sp_link_commodity_to_room(%s, %s);
                    """, [room_id, commodity_id])
            return redirect('room_list', hotel_id=hotel_id)
    else:
        form = RoomForm(instance=room)

    return render(request, 'hotel_management/room_form.html', {
        'commodities': commodities,
        'selected_commodities': selected_commodities,
        'form': form,
        'hotel': room.hotel,  
        'room': room,
    })

def delete_room(request, hotel_id, room_id):
    # Get the room or return a 404 error if it doesn't exist
    room = get_object_or_404(Room, id=room_id, hotel_id=hotel_id)

    # Check if there are any reservations associated with the room
    reservations_exist = RoomReservation.objects.filter(room=room).exists()

    if reservations_exist:
        # If there are reservations, show an error message
        sweetify.error(request, title='Error', text='Não é possível apagar este quarto, pois existem reservas associadas.', persistent='Ok')
        return redirect('room_list', hotel_id=hotel_id)  # Redirect back to room list for the hotel
    else:
        # If there are no reservations, proceed with deletion
        if request.method == 'POST':
            room.delete()
            sweetify.success(request, title='Success', text='Quarto apagado com sucesso!', persistent='Ok')
            return redirect('room_list', hotel_id=hotel_id)  # Redirect to room list for the hotel
        else:
            # Render confirmation page
            return render(request, 'hotel_management/confirm_delete_room.html', {'room': room, 'hotel': room.hotel})

def search_results(request):
    print("Query Params search:", request.GET)
    # Parâmetros do filtro
    city = request.GET.get('city', '').strip()
    budget_ranges = request.GET.getlist('budget_range')
    min_budget = request.GET.get('min_budget', '').strip()
    max_budget = request.GET.get('max_budget', '').strip()
    ratings = request.GET.getlist('ratings')

    if not city:
        return render(request, 'hotel_management/list_hotels_rooms.html', {
            'error': 'Please provide a city to search for available hotels.'
        })

    # Filtro inicial para a cidade
    filters = Q(city__icontains=city)

    # Filtros para orçamento
    budget_queries = Q()
    if budget_ranges:
        for range_ in budget_ranges:
            try:
                min_b, max_b = map(int, range_.split('-'))
                print("Range:", min_b, max_b)
                budget_queries |= Q(hotelroom__base_price__gte=min_b, hotelroom__base_price__lte=max_b)
            except ValueError:
                continue  # Ignorar ranges inválidos

    if min_budget:
        try:
            budget_queries &= Q(hotelroom__base_price__gte=int(min_budget))
        except ValueError:
            pass

    if max_budget:
        try:
            budget_queries &= Q(hotelroom__base_price__lte=int(max_budget))
        except ValueError:
            pass

    filters &= budget_queries

    # Filtros para avaliações
    if ratings:
        filters &= Q(stars__in=[int(rating) for rating in ratings])

    # Consultar usando os filtros acumulados
    hotels = Hotel.objects.filter(filters).distinct().annotate(min_price=Min('room__base_price'))

    # Debugging
    print("Query ORM:", hotels.query)

    for hotel in hotels:
        num_rev = get_number_of_reviews(hotel.id)
        file = get_cover_image(hotel.id)

        if file is not None:
            # Convert the GridFS file ID to a string
            file.id_str = str(file._id)
            hotel.cover_picture = file
        else:
            hotel.cover_picture = None
        hotel.num_reviews = num_rev

    return render(request, 'hotel_management/search_hotel.html', {
        'hotels': hotels,
        'city': city,
    })

def search_results(request):
    print("Query Params search:", request.GET)
    # Parâmetros do filtro
    city = request.GET.get('city', '').strip()
    budget_ranges = request.GET.getlist('budget_range')
    min_budget = request.GET.get('min_budget', '').strip()
    max_budget = request.GET.get('max_budget', '').strip()
    ratings = request.GET.getlist('ratings')

    if not city:
        return render(request, 'hotel_management/list_hotels_rooms.html', {
            'error': 'Please provide a city to search for available hotels.'
        })

    # Filtro inicial para a cidade
    filters = Q(city__icontains=city)

    # Filtros para orçamento
    budget_queries = Q()
    if budget_ranges:
        for range_ in budget_ranges:
            try:
                min_b, max_b = map(int, range_.split('-'))
                print("Range:", min_b, max_b)
                budget_queries |= Q(hotelroom__base_price__gte=min_b, hotelroom__base_price__lte=max_b)
            except ValueError:
                continue  # Ignorar ranges inválidos

    if min_budget:
        try:
            budget_queries &= Q(hotelroom__base_price__gte=int(min_budget))
        except ValueError:
            pass

    if max_budget:
        try:
            budget_queries &= Q(hotelroom__base_price__lte=int(max_budget))
        except ValueError:
            pass

    filters &= budget_queries

    # Filtros para avaliações
    if ratings:
        filters &= Q(stars__in=[int(rating) for rating in ratings])

    # Consultar usando os filtros acumulados
    hotels = Hotel.objects.filter(filters).distinct().annotate(min_price=Min('room__base_price'))

    # Debugging
    print("Query ORM:", hotels.query)

    for hotel in hotels:
        num_rev = get_number_of_reviews(hotel.id)
        file = get_cover_image(hotel.id)

        if file is not None:
            # Convert the GridFS file ID to a string
            file.id_str = str(file._id)
            hotel.cover_picture = file
        else:
            hotel.cover_picture = None
        hotel.num_reviews = num_rev

    return render(request, 'hotel_management/search_hotel.html', {
        'hotels': hotels,
        'city': city,
    })
    
def all_hotels(request):
    hotels = Hotel.objects.all()
    for hotel in hotels:
        file = get_cover_image(hotel.id)
        if file is not None:
            # Convert the GridFS file ID to a string
            file.id_str = str(file._id)
            hotel.cover_picture = file
        else:
            hotel.cover_picture = None

    return render(request, 'hotel_management/all_hotels.html', {
        'hotels': hotels,
    })

def search_rooms(request):
    print("Query Params:", request.GET)

    hotel_id = request.GET.get('hotel_id')  # Obtém o ID do hotel passado na URL
    checkin = request.GET.get('checkin')
    checkout = request.GET.get('checkout')
    guests = request.GET.get('guests')
    
    # Verificar se todos os parâmetros necessários foram fornecidos
    if not hotel_id or not checkin or not checkout or not guests:
        return render(request, 'hotel_management/view_hotel_rooms.html', {
            'error': 'Parâmetros inválidos ou ausentes.',
        })
    
    # Filtra os quartos disponíveis para o hotel especificado
    rooms = Room.objects.filter(hotel_id=hotel_id, condition=0).select_related('hotel')

    # Validar o número de hóspedes
    try:
        guests = int(guests)
    except (ValueError, TypeError):
        return render(request, 'hotel_management/view_hotel_rooms.html', {
            'error': 'Número de hóspedes inválido.',
        })

    # Mapeamento de capacidades permitidas de acordo com o número de hóspedes
    capacity_mapping = {
        1: ['SINGLE', 'DOUBLE'],
        2: ['SINGLE', 'DOUBLE'],
        3: ['SINGLE', 'DOUBLE', 'TRIPLE'],
        4: ['SINGLE', 'DOUBLE', 'TRIPLE', 'QUAD'],
        5: ['SINGLE', 'DOUBLE', 'TRIPLE', 'QUAD', 'KING'],
        6: ['SINGLE', 'DOUBLE', 'TRIPLE', 'QUAD', 'KING', 'FAMILY'],
    }

    # Obter as capacidades permitidas com base no número de hóspedes
    allowed_capacities = capacity_mapping.get(guests, ['SINGLE', 'DOUBLE', 'TRIPLE', 'QUAD', 'KING', 'FAMILY'])

    # Filtra os quartos disponíveis de acordo com a capacidade compatível com o número de hóspedes
    rooms = rooms.filter(room_type__room_capacity__in=allowed_capacities)

    # Debugging opcional
    print("Query ORM:", rooms.query)
    print("Checkin:", checkin, "Checkout:", checkout, "Guests:", guests)
    
    # Renderiza a página com os quartos encontrados
    return render(request, 'hotel_management/view_hotel_rooms.html', {
        'hotel_id': hotel_id,
        'rooms': rooms,
        'checkin': checkin,
        'checkout': checkout,
        'guests': guests,
    })

def filter_rooms_guests(request):
    # Captura os parâmetros da URL
    hotel_id = request.GET.get('hotel_id')
    checkin = request.GET.get('checkin')
    checkout = request.GET.get('checkout')
    guests = request.GET.get('guests')

    # Se algum parâmetro estiver ausente, não aplicar filtros
    if not hotel_id or not checkin or not checkout or not guests:
        rooms = Room.objects.none()  # Se não houver parâmetros, não mostrar nenhum quarto
    else:
        # Validar o número de hóspedes
        try:
            guests = int(guests)
        except (ValueError, TypeError):
            return render(request, 'hotel_management/view_hotel_rooms.html', {
                'error': 'Número de hóspedes inválido.',
            })

        # Mapeamento de capacidades permitidas
        capacity_mapping = {
            1: ['SINGLE', 'DOUBLE'],
            2: ['SINGLE', 'DOUBLE'],
            3: ['SINGLE', 'DOUBLE', 'TRIPLE'],
            4: ['SINGLE', 'DOUBLE', 'TRIPLE', 'QUAD'],
            5: ['SINGLE', 'DOUBLE', 'TRIPLE', 'QUAD', 'KING'],
            6: ['SINGLE', 'DOUBLE', 'TRIPLE', 'QUAD', 'KING', 'FAMILY'],
        }

        # Obter as capacidades permitidas
        allowed_capacities = capacity_mapping.get(guests, ['SINGLE', 'DOUBLE', 'TRIPLE', 'QUAD', 'KING', 'FAMILY'])

        # Filtrar os quartos disponíveis
        rooms = Room.objects.filter(
            hotel_id=hotel_id,
            condition=0,  # Apenas quartos disponíveis
            room_type__room_capacity__in=allowed_capacities,  # Capacidade compatível
        ).select_related('room_type', 'hotel')

    # Renderizar os quartos na página com os filtros aplicados
    return render(request, 'hotel_management/view_hotel_rooms.html', {
        'rooms': rooms,
        'checkin': checkin,
        'checkout': checkout,
        'guests': guests,
    })

def commodity_list(request):
    # Sorting and searching logic
    sort = request.GET.get('sort', 'details')
    order = request.GET.get('order', 'asc')
    query = request.GET.get('q', '')

    # Filter commodities based on search query
    commodities = Commodity.objects.filter(details__icontains=query)

    # Sorting commodities based on selected field
    if sort == 'details':
        commodities = commodities.order_by(f"{'' if order == 'asc' else '-'}details")

    context = {
        'commodities': commodities,
        'sort': sort,
        'order': order,
        'query': query,
    }
    return render(request, 'commodities/commodities_list.html', context)

def commodity_form(request, commodity_id=None):
    if commodity_id:
        commodity = get_object_or_404(Commodity, id=commodity_id)
        operation = "editar"
    else:
        commodity = None
        operation = "adicionar"

    if request.method == 'POST':
        form = CommodityForm(request.POST, instance=commodity)
        if form.is_valid():
            details = form.cleaned_data.get('details')

            if commodity is None:
                # Creating a new commodity
                with connection.cursor() as cursor:
                    cursor.execute("""
                        CALL sp_create_commodity(%s);
                    """, [details])
                sweetify.success(request, title='Success', text='Comodidade adicionada com sucesso!', persistent='Ok')
            else:
                # Update the existing commodity
                with connection.cursor() as cursor:
                    cursor.execute("""
                        CALL sp_update_commodity(%s,%s);
                    """, [commodity_id, details])
                sweetify.success(request, title='Success', text='Comodidade atualizada com sucesso!', persistent='Ok')

            return redirect('commodities_list')
        else:
            sweetify.error(request, title='Error', text='Ocorreu um erro ao adicionar a comodidade.', persistent='Ok')
    else:
        form = CommodityForm(instance=commodity)

    return render(request, 'commodities/commodities_form.html', {
        'form': form,
        'operation': operation,
        'commodity': commodity or {},
    })

def commodity_delete(request, commodity_id):
    with connection.cursor() as cursor:
        cursor.execute("""
            CALL sp_delete_commodity(%s);
        """, [commodity_id])
    sweetify.success(request, title='Success', text='Comodidade removida com sucesso!', persistent='Ok')
    return redirect('commodities_list')