# models.py

from django.db import models
from django.utils import timezone


class AccPermission(models.Model):
    PERMISSION_LEVELS = (
        (1, 'Admin'),
        (2, 'Manager'),
        (3, 'Funcionário'),
    )

    perm_description = models.CharField(max_length=100)
    perm_level = models.IntegerField(choices=PERMISSION_LEVELS)

    class Meta:
        db_table = "acc_permission"

    def __str__(self):
        return f"{self.perm_description} (Level {self.perm_level})"


class User(models.Model):
    CLIENT = 'C'
    EMPLOYEE = 'F'

    USER_TYPES = [
        (CLIENT, 'Client'),
        (EMPLOYEE, 'Employee'),
    ]

    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    hashed_password = models.CharField(max_length=255)
    inactive = models.BooleanField(default=False)
    nif = models.CharField(max_length=20, unique=True, verbose_name="NIF")
    phone = models.CharField(max_length=20, unique=True)
    full_address = models.CharField(max_length=160)
    postal_code = models.CharField(max_length=8)
    city = models.CharField(max_length=100)
    utp = models.CharField(max_length=1, choices=USER_TYPES, default=CLIENT)

    class Meta:
        db_table = "u_user"
        constraints = [
            models.CheckConstraint(check=models.Q(utp__in=['C', 'F']), name="ck_utp"),
        ]

    def __str__(self):
        return f"{self.first_name} {self.last_name} ({self.get_utp_display()})"


class Client(User):
    class Meta:
        db_table = "u_client"


class Employee(User):
    role = models.ForeignKey(AccPermission, on_delete=models.CASCADE)
    social_security = models.IntegerField()

    class Meta:
        db_table = "u_employee"


class UserPasswordsDictionary(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, primary_key=True, related_name="password_history")
    hashed_password = models.CharField(max_length=255)
    valid_from = models.DateTimeField(default=timezone.now)
    valid_to = models.DateTimeField()

    class Meta:
        db_table = "u_user_passwords_dictionary"

    def __str__(self):
        return f"Password history for {self.user.email}"
