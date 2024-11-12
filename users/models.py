from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.contrib.auth.hashers import check_password, make_password
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

class UserManager(BaseUserManager):
    """Custom manager for User model"""
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError("The Email field must be set")
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        return self.create_user(email, password, **extra_fields)

class User(AbstractBaseUser, PermissionsMixin):
    CLIENT = 'C'
    EMPLOYEE = 'F'

    USER_TYPES = [
        (CLIENT, 'Client'),
        (EMPLOYEE, 'Employee'),
    ]

    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    hashed_password = models.CharField(max_length=255)  # This is the hashed password field
    inactive = models.BooleanField(default=False)
    nif = models.CharField(max_length=20, unique=True, verbose_name="NIF")
    phone = models.CharField(max_length=20, unique=True)
    full_address = models.CharField(max_length=160)
    postal_code = models.CharField(max_length=8)
    city = models.CharField(max_length=100)
    utp = models.CharField(max_length=1, choices=USER_TYPES, default=CLIENT)

    # Add permissions and staff status fields
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)

    objects = UserManager()

    USERNAME_FIELD = 'email'  
    REQUIRED_FIELDS = ['first_name', 'last_name']  

    class Meta:
        db_table = "u_user" 

    def __str__(self):
        return self.email

    def set_password(self, raw_password):
        """Set password and hash it."""
        self.hashed_password = make_password(raw_password)

    def check_password(self, raw_password):
        """Check if the raw password matches the hashed password."""
        return check_password(raw_password, self.hashed_password)
    

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
