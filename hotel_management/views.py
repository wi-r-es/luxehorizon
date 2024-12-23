from django.shortcuts import render, get_object_or_404, redirect
from .models import Hotel, Room
from django.db.models import Q, Count, Sum, OuterRef, Subquery
from .forms import HotelForm, RoomForm
from django.contrib import messages
from reservation.models import RoomReservation, Reservation
from django.http import Http404
import json
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

# View para adicionar ou editar um hotel
def hotel_form(request, hotel_id=None):
    if hotel_id:
        # busca o hotel pelo id
        hotel = get_object_or_404(Hotel, id=hotel_id)
        heading = "Editar Hotel"
    else:
        #cria um novo hotel
        hotel = Hotel()
        heading = "Adicionar Hotel"

    if request.method == 'POST':
        form = HotelForm(request.POST, instance=hotel)
        if form.is_valid():
            form.save()
            return redirect('hotel_list')
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
    hotel = get_object_or_404(Hotel, id=hotel_id)  

    if request.method == 'POST':
        form = RoomForm(request.POST)
        if form.is_valid():
            new_room = form.save(commit=False)
            new_room.hotel = hotel 
            new_room.save()
            return redirect('room_list', hotel_id=hotel.id)  
    else:
        form = RoomForm()

    return render(request, 'hotel_management/room_form.html', {
        'form': form,
        'hotel': hotel,
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
        
def import_rooms(request, hotel_id):
    hotel = get_object_or_404(Hotel, id=hotel_id)

    if request.method == 'POST':
        rooms_file = request.FILES.get('rooms_file')
        if rooms_file:
            try:
                # Load JSON from uploaded file
                rooms_json = json.load(rooms_file)
                rooms_json_str = json.dumps(rooms_json)

                # Call the stored procedure
                with connection.cursor() as cursor:
                    cursor.execute(
                        "CALL ROOM_MANAGEMENT.import_rooms(%s, %s::jsonb);",
                        [hotel_id, rooms_json_str]
                    )

                messages.success(request, f"Rooms imported successfully for hotel {hotel.h_name}!")
                return redirect('room_list', hotel_id=hotel_id)
            except Exception as e:
                messages.error(request, f"Error importing rooms: {e}")
        else:
            messages.error(request, "No file uploaded. Please upload a valid JSON file.")
    
    return render(request, 'hotel_management/import_rooms.html', {'hotel': hotel})

def search_results(request):
    # Obtendo o parâmetro de busca
    city = request.GET.get('city', '').strip()
    # Se o usuário não forneceu uma cidade, retornamos uma mensagem
    if not city:
        return render(request, 'hotel_management/list_hotels_rooms.html', {
            'error': 'Please provide a city to search for available rooms.'
        })
    # Consulta SQL segura para obter os quartos disponíveis em hotéis da cidade fornecida
    query = """
        SELECT 
            r.id AS room_id, r.room_number, r.base_price, r."condition", 
            r.capacity, r.hotel_id, h.h_name AS hotel_name, r.type_id
        FROM 
            public."ROOM_MANAGEMENT.room" r
        INNER JOIN 
            public."MANAGEMENT.hotel" h ON r.hotel_id = h.id
        WHERE 
            h.city ILIKE %(city)s
    """
    params = {'city': f"%{city}%"}
    # Executando a consulta no banco de dados
    with connection.cursor() as cursor:
        cursor.execute(query, params)
        rooms = cursor.fetchall()
    # Preparando os dados para exibição no template
    rooms_list = [
        {
            'room_id': room[0],
            'room_number': room[1],
            'base_price': room[2],
            'condition': room[3],
            'capacity': room[4],
            'hotel_id': room[5],
            'hotel_name': room[6],
            'type_id': room[7],
        }
        for room in rooms
    ]
    # Renderizando o template com os resultados
    return render(request, 'hotel_management/list_hotels_rooms.html', {
        'rooms': rooms_list,
        'city': city,
    })

