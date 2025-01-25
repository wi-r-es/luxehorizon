from django.db import models
from users.models import User  
from hotel_management.models import Room

class Season(models.Model):
    HIGH = 'H'
    LOW = 'L'
    FESTIVAL = 'F'
    MIDLOW = 'M'

    SEASON_DESCRIPTIVE_CHOICES = [
        (HIGH, 'High'),
        (LOW, 'Low'),
        (MIDLOW, 'MidLow'),
        (FESTIVAL, 'Festival')
    ]

    descriptive = models.TextField(choices=SEASON_DESCRIPTIVE_CHOICES)
    begin_month = models.IntegerField()
    begin_day = models.IntegerField()
    end_month = models.IntegerField()
    end_day = models.IntegerField()
    rate = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=0.00,
        verbose_name="Season Rate"
    )

    class Meta:
        db_table = 'finance.season'

    def __str__(self):
        return f"Season {self.get_descriptive_display()} ({self.begin_month}/{self.begin_day} to {self.end_month}/{self.end_day})"

    def is_date_in_season(self, date_to_check):
        """
        Check if a given date is within the season's range.
        """
        start = date_to_check.replace(month=self.begin_month, day=self.begin_day)
        end = date_to_check.replace(month=self.end_month, day=self.end_day)
        if self.begin_month > self.end_month:
            # Handle seasons that span across the year-end
            end = end.replace(year=end.year + 1)
        return start <= date_to_check <= end

class Reservation(models.Model):
    PENDING = 'P'
    CONFIRMED = 'C'
    REJECTED = 'R'
    CANCELED = 'CC'
    CHECK_IN = 'CI'
    CHECK_OUT = 'CO'
    
    RESERVATION_STATUS_CHOICES = [
        (PENDING, 'Pending'),
        (CONFIRMED, 'Confirmed'),
        (REJECTED, 'Rejected'),
        (CANCELED, 'Canceled'),
        (CHECK_IN, 'Checked In'),
        (CHECK_OUT, 'Checked Out'),
    ]

    client = models.ForeignKey(User, on_delete=models.CASCADE, related_name="reservations")
    begin_date = models.DateField()
    end_date = models.DateField()
    status = models.CharField(
        max_length=2,
        choices=RESERVATION_STATUS_CHOICES,
        default=PENDING,
        verbose_name="Reservation Status"
    )
    season = models.ForeignKey(Season, on_delete=models.CASCADE)
    total_value = models.DecimalField(max_digits=10, decimal_places=2)

    class Meta:
        db_table = 'reserves.reservation'
        indexes = [
            models.Index(fields=['begin_date', 'end_date'], name='idx_reservation_dates'),
            models.Index(fields=['status', 'client'], name='idx_reservation_status_client'),
            models.Index(fields=['season', 'status'], name='idx_reservation_season_status')
        ]

    def __str__(self):
        return f"Reservation {self.id} for {self.client} ({self.get_status_display()})"


class RoomReservation(models.Model):
    reservation = models.ForeignKey(Reservation, on_delete=models.CASCADE, related_name="room_reservations")
    room = models.ForeignKey(Room, on_delete=models.CASCADE, related_name="room_reservations")
    price_reservation = models.DecimalField(max_digits=10, decimal_places=2)

    class Meta:
        db_table = 'reserves.room_reservation'
        unique_together = ('reservation', 'room')
        indexes = [
            models.Index(fields=['room', 'reservation'], name='idx_roomres_room_res')
        ]

    def __str__(self):
        return f"Room {self.room.id} in Reservation {self.reservation.id}"

class Guest(models.Model):
    reservation = models.ForeignKey(Reservation, on_delete=models.CASCADE, related_name="guests")
    full_name = models.CharField(max_length=100)
    cc_pass = models.CharField(max_length=20, verbose_name="CC or Passport")
    phone = models.CharField(max_length=20)
    full_address = models.CharField(max_length=160, null=True)
    postal_code = models.CharField(max_length=8, null=True)
    city = models.CharField(max_length=100, null=True)

    class Meta:
        db_table = 'reserves.guest'
        indexes = [
            models.Index(fields=['reservation', 'cc_pass'], name='idx_guest_res_cc'),
            models.Index(fields=['full_name'], name='idx_guest_name')
        ]

    def __str__(self):
        return f"Guest {self.full_name} for Reservation {self.reservation.id}"

