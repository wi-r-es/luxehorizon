from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from .models import Reservation, RoomReservation, Guest, Season
from hotel_management.models import Room
from datetime import datetime
from decimal import Decimal

def my_reservations(request):
    # Fetch reservations for the logged-in user
    reservations = Reservation.objects.filter(client=request.user).prefetch_related('room_reservations__room__hotel')
    reservation_list = []
    for reservation in reservations:
        refundable = False #reservation.is_refundable()   Check if the reservation is refundable
        room_details = ", ".join(
            [f"Room {rr.room.room_number} at {rr.room.hotel.h_name}" for rr in reservation.room_reservations.all()]
        )

        # Buscar o hotel associado ao quarto
        hotel = reservation.room_reservations.first().room.hotel
        
        # Obter o rating do hotel (campo `stars`)
        hotel_rating = hotel.stars
        # Calcular o número de noites
        night = reservation.end_date - reservation.begin_date

        reservation_list.append({
            'title': room_details,
            'check_in': reservation.begin_date,
            'check_out': reservation.end_date,
            'nights': night.days,
            'price': reservation.total_value,
            'tax_inclusive': True,  # Assuming tax inclusion for all reservations
            'non_refundable': not refundable,
            'hotel_rating': hotel_rating, 
        })

    return render(request, 'reservations/my_reservations.html', {'reservations': reservation_list})

def reservation_page(request, room_id):

    hotel_id = request.GET.get('hotel_id')
    checkin = request.GET.get('checkin')
    checkout = request.GET.get('checkout')
    guests = request.GET.get('guests')
    
    # Busca os dados do quarto pelo room_id
    room = get_object_or_404(Room, id=room_id)
    
    # Adicionar user_id no contexto
    user_id = request.user.id
    user_name = request.user.first_name
    user_last_name = request.user.last_name
    user_email = request.user.email
    user_nif = request.user.nif
    user_phone = request.user.phone
    user_address = request.user.full_address
    user_postal_code = request.user.postal_code
    user_city = request.user.city

    context = {
        'room': room,
        'hotel_id': hotel_id,
        'hotel_name': room.hotel,
        'checkin': checkin,
        'checkout': checkout,
        'guests': guests,
        'user_id': user_id,  
        'user_name': user_name,
        'user_last_name': user_last_name,
        'user_email': user_email,
        'user_nif': user_nif,
        'user_phone': user_phone,
        'user_address': user_address,
        'user_postal_code': user_postal_code,
        'user_city': user_city
    }
    return render(request, 'reservations/reservation_page.html', context)

def confirm_reservation(request):
    if request.method == "POST":
        try:
            # Coletar dados do formulário
            user_id = request.POST.get('user_id')
            room_id = request.POST.get('room_id')
            checkin_str = request.POST.get('checkin')
            checkout_str = request.POST.get('checkout')
            guests = request.POST.get('guests')

            print("Início da validação")

            # Validar campos obrigatórios
            if not all([user_id, room_id, checkin_str, checkout_str, guests]):
                messages.error(request, "Todos os campos são obrigatórios.")
                return redirect('reservation_page', room_id=room_id)

            # Conversão de datas
            try:
                checkin = datetime.strptime(checkin_str, '%Y-%m-%d').date()
                checkout = datetime.strptime(checkout_str, '%Y-%m-%d').date()
            except ValueError:
                messages.error(request, "Formato de data inválido. Use AAAA-MM-DD.")
                return redirect('reservation_page', room_id=room_id)

            # Validar datas
            if checkin >= checkout:
                messages.error(request, "A data de check-in deve ser antes da data de check-out.")
                return redirect('reservation_page', room_id=room_id)

            print("Datas validadas com sucesso")

            # Buscar o quarto
            room = get_object_or_404(Room, id=room_id)

            print(f"Quarto encontrado: {room}")

            # Determinar a temporada
            season = Season.objects.filter(
                begin_date__lte=checkin,
                end_date__gte=checkout
            ).first()

            if not season:
                messages.error(request, "Não há temporada válida para as datas selecionadas.")
                return redirect('reservation_page', room_id=room_id)

            print(f"Temporada encontrada: {season}")

            # Calcular valor total da reserva
            difference = checkout - checkin
            nights = difference.days

            if nights <= 0:
                messages.error(request, "A reserva precisa ter pelo menos uma noite.")
                return redirect('reservation_page', room_id=room_id)

            print(f"Número de noites: {nights}")

            # Validar o preço do quarto
            if not hasattr(room, 'base_price') or room.base_price is None:
                messages.error(request, "O quarto selecionado não tem um preço base definido.")
                return redirect('reservation_page', room_id=room_id)

            print(f"Preço base do quarto: {room.base_price}")

            # Calcular total com impostos (exemplo de 23%)
            room_price = room.base_price
            tax_rate = Decimal('1.23')
            total_value = room_price * nights * tax_rate

            print(f"Valor total calculado: {total_value}")

            # Criar a reserva
            reservation = Reservation.objects.create(
                client_id=user_id,
                begin_date=checkin,
                end_date=checkout,
                status=Reservation.PENDING,
                season=season,
                total_value=total_value
            )

            print("Reserva criada com sucesso")

            # Relacionar o quarto com a reserva
            RoomReservation.objects.create(
                reservation=reservation,
                room=room,
                price_reservation=total_value
            )

            print("Reserva do quarto criada com sucesso")

            # Mensagem de sucesso
            messages.success(request, "Reserva criada com sucesso!")
            return redirect('my_reservations')

        except Exception as e:
            print(f"Erro: {str(e)}")
            messages.error(request, f"Ocorreu um erro ao criar a reserva: {str(e)}")
            return redirect('reservation_page', room_id=request.POST.get('room_id'))
    else:
        return redirect('home')