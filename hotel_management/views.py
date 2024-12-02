from django.shortcuts import render, get_object_or_404, redirect
from .models import Hotel, Room
from django.db.models import Q, Count, Sum, OuterRef, Subquery
from .forms import HotelForm
from django.contrib import messages
from reservation.models import RoomReservation, Reservation
from django.http import Http404

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
    hotel = Hotel.objects.get(id=hotel_id)  # Get the hotel by ID
    type_name = request.GET.get('type_name', '')  # Get filter parameter if provided

    rooms = Room.objects.filter(hotel=hotel)  # Start by filtering rooms for this hotel

    if type_name:   
        rooms = rooms.filter(type__name__icontains=type_name)  # Apply filter on RoomType's name

    return render(request, 'hotel_management/hotel_rooms.html', {
        'hotel': hotel,
        'rooms': rooms,
    })

