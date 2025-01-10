from django.shortcuts import render, get_object_or_404, redirect
from .models import Hotel, Room, Commodity
from django.db.models import Q, Count, Sum, OuterRef, Subquery
from .forms import HotelForm, RoomForm, CommodityForm
from django.contrib import messages
from reservation.models import RoomReservation, Reservation
from django.http import Http404
from django.db.models import Min
from django.db import connection

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

    # agrega os resultados
    hotels = Hotel.objects.annotate(
        room_count=Count('room'),   
        total_value=Subquery(reservation_total_value[:1])   
    ).filter(
        Q(h_name__icontains=query) | Q(city__icontains=query)
    ) if query else Hotel.objects.annotate(
        room_count=Count('room'),
        total_value=Subquery(reservation_total_value[:1])
    )

    # aplica a ordenação
    hotels = hotels.order_by(sort_field)

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
        heading = "Editar Hotel"
    else:
        # Initialize a new hotel for addition
        hotel = None  # No instance for new entries
        heading = "Adicionar Hotel"

    if request.method == 'POST':
        form = HotelForm(request.POST, instance=hotel)
        if form.is_valid():
            # Extract cleaned data from the form
            data = form.cleaned_data
            try:
                with connection.cursor() as cursor:
                    cursor.execute("""
                        CALL sp_add_hotel(%s, %s, %s, %s, %s, %s, %s, %s)
                    """, [
                        data['h_name'], data['full_address'], data['postal_code'],
                        data['city'], data['email'], data['telephone'],
                        data.get('details', ''), data.get('stars', 0)
                    ])
                messages.success(request, "Hotel added successfully!")
                return redirect('hotel_list')
            except Exception as e:
                messages.error(request, f"An error occurred: {str(e)}")
        else:
            messages.error(request, "Please correct the errors below.")
    else:
        form = HotelForm(instance=hotel)

    return render(request, 'hotel_management/hotel_form.html', {
        'form': form,
        'heading': heading
    })


# View para apagar um hotel
def delete_hotel(request, hotel_id):
    # obtem o hotel pelo id ou retorna um erro 404 caso não exista
    hotel = get_object_or_404(Hotel, id=hotel_id)

    # Verifica se existem reservas associadas ao hotel
    reservations_exist = RoomReservation.objects.filter(room__hotel=hotel).exists()

    if reservations_exist:
        # Mensagem de erro caso existam reservas associadas ao hotel
        messages.error(request, "Não é possível apagar este hotel, pois existem reservas associadas aos quartos.")
        return redirect('hotel_list')   
    else:
        # Se nao existirem reservas associadas ao hotel, apaga o hotel
        if request.method == 'POST':
            hotel.delete()
            messages.success(request, "Hotel Apagado com sucesso!")
            return redirect('hotel_list')
        else:
            # Mensagem de confirmação de apagar hotel
            return render(request, 'hotel_management/confirm_delete.html', {'hotel': hotel})
        
def room_list(request, hotel_id):
    hotel = get_object_or_404(Hotel, id=hotel_id)   
    type_name = request.GET.get('type_initials', '')   

    rooms = Room.objects.filter(hotel=hotel)   

    if type_name:   
        rooms = rooms.filter(type__type_initials__icontains=type_name)   

    return render(request, 'hotel_management/hotel_rooms.html', {
        'hotel': hotel,
        'rooms': rooms,
    })

def create_room(request, hotel_id):
    # Obtém o hotel ou retorna 404 se não existir
    hotel = get_object_or_404(Hotel, id=hotel_id)

    if request.method == 'POST':
        form = RoomForm(request.POST)
        if form.is_valid():
            # Cria um quarto sem salvar imediatamente no banco
            new_room = form.save(commit=False)
            # Associa o quarto ao hotel
            new_room.hotel = hotel
            new_room.save()
            return redirect('room_list', hotel_id=hotel.id)  # Redireciona para a lista de quartos
    else:
        form = RoomForm()

    return render(request, 'hotel_management/room_form.html', {
        'form': form,
        'hotel': hotel,
        'room': None,  # Define como None, já que o quarto ainda não existe
    })

def edit_room(request, hotel_id, room_id):
    room = get_object_or_404(Room, id=room_id, hotel_id=hotel_id)
    if request.method == 'POST':
        form = RoomForm(request.POST, instance=room)
        if form.is_valid():
            form.save()
            return redirect('room_list', hotel_id=hotel_id)
    else:
        form = RoomForm(instance=room)

    return render(request, 'hotel_management/room_form.html', {
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
        messages.error(request, "Não é possível apagar este quarto, pois existem reservas associadas.")
        return redirect('room_list', hotel_id=hotel_id)  # Redirect back to room list for the hotel
    else:
        # If there are no reservations, proceed with deletion
        if request.method == 'POST':
            room.delete()
            messages.success(request, "Quarto apagado com sucesso!")
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

    return render(request, 'hotel_management/search_hotel.html', {
        'hotels': hotels,
        'city': city,
    })

def search_rooms(request):
    print("Query Params:", request.GET)
    hotel_id = request.GET.get('hotel_id')  # Obtém o ID do hotel passado na URL
    checkin = request.GET.get('checkin')
    checkout = request.GET.get('checkout')
    guests = request.GET.get('guests')
    
    if not hotel_id:
        return render(request, 'hotel_management/view_hotel_rooms.html', {
            'error': 'ID do hotel não fornecido.',
        })

    # Filtra os quartos disponíveis para o hotel especificado
    rooms = Room.objects.filter(hotel_id=hotel_id, condition=0).select_related('hotel')

    # Debugging opcional
    print("Query ORM:", rooms.query)
    print(f"Checkin: {checkin}, Checkout: {checkout}, Guests: {guests}")

    # Renderiza a página com os quartos encontrados
    return render(request, 'hotel_management/view_hotel_rooms.html', {
        'hotel_id': hotel_id,
        'rooms': rooms,
        'checkin': checkin,
        'checkout': checkout,
        'guests': guests,
    })

def filter_rooms_guests(request):
    hotel_id = request.GET.get('hotel_id')
    checkin = request.GET.get('checkin')
    checkout = request.GET.get('checkout')
    guests = request.GET.get('guests')

    print("Query Params:", request.GET)  # Verifique todos os parâmetros recebidos
    print("Hotel ID recebido:", hotel_id)

    if not hotel_id:
        return render(request, 'hotel_management/view_hotel_rooms.html', {
            'error': 'ID do hotel não fornecido.',
        })

    try:
        guests = int(guests)  # Certifica-se de que o número de hóspedes é um inteiro
    except (ValueError, TypeError):
        return render(request, 'hotel_management/view_hotel_rooms.html', {
            'error': 'Número de hóspedes inválido.',
        })

    print("Número de hóspedes:", guests)

    # Definir os tipos de capacidade permitidos com base no número de hóspedes
    capacity_mapping = {
        1: ['S', 'D'],  # Permitir Single e Double para 1 hóspede
        2: ['S', 'D'],  # Single e Double para 2 hóspedes
        3: ['S', 'D', 'T'],  # Single, Double e Triple para 3 hóspedes
        4: ['S', 'D', 'T', 'Q'],  # Single, Double, Triple e Quad para 4 hóspedes
        5: ['S', 'D', 'T', 'Q', 'K'],  # Single, Double, Triple, Quad e King para 5 hóspedes
        6: ['S', 'D', 'T', 'Q', 'K', 'F'],  # Single, Double, Triple, Quad, King e Family para 6 hóspedes
    }

    # Obter os tipos permitidos para o número de hóspedes ou considerar todos os tipos para valores acima de 6
    allowed_capacities = capacity_mapping.get(guests, ['S', 'D', 'T', 'Q', 'K', 'F'])

    # Filtrar os quartos disponíveis para o hotel especificado e os tipos permitidos
    rooms = Room.objects.filter(
        hotel_id=hotel_id,
        condition=0,  # Disponível
        capacity__in=allowed_capacities
    ).select_related('hotel')

    print("capacidades permitidas:", allowed_capacities)

    # Renderiza a página com os quartos encontrados
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
                messages.success(request, "Comodidade adicionada com sucesso!")
            else:
                # Update the existing commodity
                with connection.cursor() as cursor:
                    cursor.execute("""
                        CALL sp_update_commodity(%s,%s);
                    """, [commodity_id, details])
                messages.success(request, "Comodidade atualizada com sucesso!")

            return redirect('commodities_list')
        else:
            messages.error(request, "Erro ao processar o formulário.")
    else:
        form = CommodityForm(instance=commodity)

    return render(request, 'commodities/commodities_form.html', {
        'form': form,
        'operation': operation,
        'commodity': commodity or {},
    })

def commodity_delete(request, commodity_id):
    commodity = get_object_or_404(Commodity, id=commodity_id)
    with connection.cursor() as cursor:
        cursor.execute("""
            CALL sp_delete_commodity(%s);
        """, [commodity_id])
    messages.success(request, "Comodidade removida com sucesso!")
    return redirect('commodities_list')