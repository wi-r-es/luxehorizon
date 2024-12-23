from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from .models import Reservation, RoomReservation, Season, Guest
from hotel_management.models import Room
from django.db import transaction
from datetime import datetime

def my_reservations(request):
    # Fetch reservations for the logged-in user
    reservations = Reservation.objects.filter(client=request.user).prefetch_related('room_reservations__room__hotel')

    reservation_list = []
    for reservation in reservations:
        refundable = reservation.is_refundable()  # Check if the reservation is refundable
        room_details = ", ".join(
            [f"Room {rr.room.room_number} at {rr.room.hotel.h_name}" for rr in reservation.room_reservations.all()]
        )
        reservation_list.append({
            'title': room_details,
            'check_in': reservation.begin_date,
            'check_out': reservation.end_date,
            'nights': reservation.duration(),
            'price': reservation.total_value,
            'tax_inclusive': True,  # Assuming tax inclusion for all reservations
            'non_refundable': not refundable,
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
        # Captura os dados enviados pelo formulário
        room_id = request.POST.get('room_id')
        hotel_id = request.POST.get('hotel_id')
        checkin = request.POST.get('checkin')
        checkout = request.POST.get('checkout')
        guests = int(request.POST.get('guests'))

        # Valida o quarto
        room = get_object_or_404(Room, id=room_id)

        # Valida as datas de check-in e check-out
        try:
            begin_date = datetime.strptime(checkin, "%Y-%m-%d").date()
            end_date = datetime.strptime(checkout, "%Y-%m-%d").date()
            if begin_date >= end_date:
                messages.error(request, "A data de check-out deve ser posterior à data de check-in.")
                return redirect('reservation_page', room_id=room_id)
        except ValueError:
            messages.error(request, "Datas inválidas fornecidas.")
            return redirect('reservation_page', room_id=room_id)

        # Determina a temporada (Season) correspondente
        season = Season.objects.filter(
            begin_date__lte=begin_date,
            end_date__gte=end_date
        ).first()

        if not season:
            messages.error(request, "Não foi encontrada uma temporada válida para essas datas.")
            return redirect('reservation_page', room_id=room_id)

        # Calcula o valor total (exemplo simplificado)
        base_price = room.price  # Preço do quarto
        total_nights = (end_date - begin_date).days
        total_value = base_price * total_nights

        # Adiciona impostos (se houver)
        tax_rate = season.season_prices.first().tax if season.season_prices.exists() else 0
        total_value += total_value * (tax_rate / 100)

        # Salva a reserva e os dados associados
        try:
            with transaction.atomic():
                # Cria a reserva
                reservation = Reservation.objects.create(
                    client=request.user,
                    begin_date=begin_date,
                    end_date=end_date,
                    status=Reservation.PENDING,
                    season=season,
                    total_value=total_value
                )

                # Cria a associação do quarto à reserva
                RoomReservation.objects.create(
                    reservation=reservation,
                    room=room,
                    price_reservation=total_value
                )

                # (Opcional) Adiciona hóspedes fictícios
                for i in range(guests):
                    Guest.objects.create(
                        reservation=reservation,
                        full_name=f"Hóspede {i + 1}",
                        cc_pass="00000000",
                        phone="123456789",
                        full_address="Endereço fictício",
                        postal_code="0000-000",
                        city="Cidade fictícia"
                    )

                messages.success(request, "Reserva confirmada com sucesso!")
                return redirect('reservations/my_reservations.html')

        except Exception as e:
            messages.error(request, f"Erro ao salvar a reserva: {e}")
            print(e)
            return redirect('reservation_page', room_id=room_id)

    # Redireciona se a requisição não for POST
    return redirect('home')