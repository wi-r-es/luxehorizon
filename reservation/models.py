from django.db import models
from users.models import User  
from hotel_management.models import Room

class Season(models.Model):
    HIGH = 'A'
    LOW = 'B'
    FESTIVAL = 'F'
    
    SEASON_DESCRIPTIVE_CHOICES = [
        (HIGH, 'High'),
        (LOW, 'Low'),
        (FESTIVAL, 'Festival')
    ]

    descriptive = models.TextField()
    begin_date = models.DateField()
    end_date = models.DateField()
    rate = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=0.00, 
        verbose_name="Season Rate"
    )

    class Meta:
        db_table = 'FINANCE.season'
        unique_together = ('descriptive', 'begin_date', 'end_date', 'rate')

    def __str__(self):
        return f"Season {self.get_descriptive_display()} ({self.begin_date} to {self.end_date})"


class Reservation(models.Model):
    PENDING = 'P'
    CONFIRMED = 'C'
    REJECTED = 'R'
    
    RESERVATION_STATUS_CHOICES = [
        (PENDING, 'Pending'),
        (CONFIRMED, 'Confirmed'),
        (REJECTED, 'Rejected'),
    ]

    client = models.ForeignKey(User, on_delete=models.CASCADE, related_name="reservations")
    begin_date = models.DateField()
    end_date = models.DateField()
    status = models.CharField(
        max_length=1,
        choices=RESERVATION_STATUS_CHOICES,
        default=PENDING,
        verbose_name="Reservation Status"
    )
    season = models.ForeignKey(Season, on_delete=models.CASCADE)
    total_value = models.DecimalField(max_digits=10, decimal_places=2)

    class Meta:
        db_table = 'RESERVES.reservation'

    def __str__(self):
        return f"Reservation {self.id} for {self.client} ({self.get_status_display()})"


class RoomReservation(models.Model):
    reservation = models.ForeignKey(Reservation, on_delete=models.CASCADE, related_name="room_reservations")
    room = models.ForeignKey(Room, on_delete=models.CASCADE, related_name="room_reservations")
    price_reservation = models.DecimalField(max_digits=10, decimal_places=2)

    class Meta:
        db_table = 'RESERVES.room_reservation'
        unique_together = ('reservation', 'room')

    def __str__(self):
        return f"Room {self.room.id} in Reservation {self.reservation.id}"

class Guest(models.Model):
    reservation = models.ForeignKey(Reservation, on_delete=models.CASCADE, related_name="guests")
    full_name = models.CharField(max_length=100)
    cc_pass = models.CharField(max_length=20, verbose_name="CC or Passport")
    phone = models.CharField(max_length=20)
    full_address = models.CharField(max_length=160)
    postal_code = models.CharField(max_length=8)
    city = models.CharField(max_length=100)

    class Meta:
        db_table = 'RESERVES.guest'

    def __str__(self):
        return f"Guest {self.full_name} for Reservation {self.reservation.id}"

