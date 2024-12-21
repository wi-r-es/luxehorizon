from django.shortcuts import render
from .models import Reservation, RoomReservation

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
