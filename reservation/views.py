from django.shortcuts import render, redirect, get_object_or_404
from django.db import connection
from django.http import JsonResponse
from .models import Reservation, RoomReservation, Guest, Season
from hotel_management.models import Room

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
            # Receber os parâmetros do corpo da requisição
            user_id = int(request.POST.get("user_id"))
            room_id = int(request.POST.get("room_id"))
            checkin = request.POST.get("checkin")  # Formato: YYYY-MM-DD
            checkout = request.POST.get("checkout")  # Formato: YYYY-MM-DD
            guests = int(request.POST.get("guests"))

            # Chamar o procedimento no banco de dados
            with connection.cursor() as cursor:
                cursor.execute("""
                    CALL create_reservation(%s, %s, %s, %s, %s);
                """, [user_id, room_id, checkin, checkout, guests])

            return render(request, 'reservations/my_reservations.html', {"success": True})
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=400)

    return JsonResponse({"error": "Método não suportado. Use POST."}, status=405)