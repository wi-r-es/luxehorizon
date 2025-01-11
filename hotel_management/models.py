from django.db import models
from django.db.models import Func
from hotel_management.fields import PostgreSQLEnumField
from users.models import User

class RoomViewType(models.TextChoices):
    POOL = 'P', 'Piscina'
    MOUNTAIN = 'M', 'MOUNTAIN'
    NONE = 'N', 'Nenhuma'
    CITY = 'C', 'CITY'
    OCEAN = 'O', 'OCEAN'
    GARDEN = 'G', 'GARDEN'

class RoomQualityType(models.TextChoices):
    STANDARD = 'S', 'STANDARD'
    DELUXE = 'D', 'DELUXE'
    PREMIUM = 'P', 'PREMIUM'

class CapacityType(models.TextChoices):
    SINGLE = 'S', 'Single'
    DOUBLE = 'D', 'Double'
    TRIPLE = 'T', 'Triple'
    QUAD = 'Q', 'Quad'
    KING = 'K', 'King'
    FAMILY = 'F', 'Family'

class Hotel(models.Model):
    h_name = models.CharField(max_length=100)
    full_address = models.CharField(max_length=160)
    postal_code = models.CharField(max_length=8)
    city = models.CharField(max_length=100)
    email = models.EmailField(max_length=100)
    telephone = models.CharField(max_length=20)
    details = models.CharField(max_length=200)
    stars = models.IntegerField()

    class Meta:
        db_table = 'management.hotel'

    def __str__(self):
        return self.h_name
    
class RoomType(models.Model):
    type_initials = models.CharField(max_length=100)
    room_view = PostgreSQLEnumField("room_view_type")
    room_quality = PostgreSQLEnumField("room_quality_type")
    room_capacity = PostgreSQLEnumField("room_capacity_type")

    class Meta:
        db_table = 'room_management.room_types'

    def __str__(self):
        return f"{self.type_initials} - {self.room_view} - {self.room_quality} - {self.room_capacity}"

# class RoomType(models.Model):
#     type_initials = models.CharField(max_length=100)
#     room_view = models.CharField(max_length=1, choices=RoomViewType.choices)
#     room_quality = models.CharField(max_length=1, choices=RoomQualityType.choices)

#     class Meta:
#         db_table = 'room_management.room_type'

#     def __str__(self):
#         return f"{self.type_initials} - {self.get_room_view_display()} - {self.get_room_quality_display()}"

class Commodity(models.Model):
    details = models.CharField(max_length=100)

    class Meta:
        db_table = 'room_management.commodity'

    def __str__(self):
        return self.details

class Room(models.Model):
    room_type = models.ForeignKey(RoomType, on_delete=models.CASCADE)
    hotel = models.ForeignKey(Hotel, on_delete=models.CASCADE)
    room_number = models.IntegerField()
    base_price = models.DecimalField(max_digits=10, decimal_places=2)
    condition = models.IntegerField()  # 0 - available, 1 - occuppied, 2 - dirty, 3- maintenance

    class Meta:
        db_table = 'room_management.room'
        unique_together = ('hotel', 'room_number')

    def __str__(self):
        return f"Room {self.room_number} in {self.hotel.h_name}"

class RoomCommodity(models.Model):
    room = models.ForeignKey(Room, on_delete=models.CASCADE)
    commodity = models.ForeignKey(Commodity, on_delete=models.CASCADE)

    class Meta:
        db_table = 'room_management.room_commodity'
        unique_together = ('room', 'commodity')

    def __str__(self):
        return f"{self.commodity} in Room {self.room.room_number} of {self.room.hotel.h_name}"
    

class HotelEmployees(models.Model):
    hotel = models.ForeignKey(Hotel, on_delete=models.CASCADE, related_name="employeeshotel")
    employee = models.ForeignKey(User, on_delete=models.CASCADE, related_name="hotelemployees")

    class Meta:
        db_table = 'management.hotel_employee'

    def __str__(self):
        return f"Employee ID {self.employee.id} works at {self.hotel.id} ID"
