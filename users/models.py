from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.contrib.auth.hashers import check_password, make_password
from django.utils import timezone

class AccPermission(models.Model):
    PERMISSION_LEVELS = (
        (0, 'None'),
        (1, 'Admin'),
        (2, 'Manager'),
        (3, 'Funcionário'),
    )

    perm_description = models.CharField(max_length=100)
    perm_level = models.IntegerField(choices=PERMISSION_LEVELS)

    class Meta:
        db_table = "sec.acc_permission"

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

    nif = models.CharField(max_length=20, unique=True, verbose_name="NIF")
    phone = models.CharField(max_length=20, unique=True)
    full_address = models.CharField(max_length=160)
    postal_code = models.CharField(max_length=8)
    city = models.CharField(max_length=100)
    utp = models.CharField(max_length=1, choices=USER_TYPES, default=CLIENT)

    role = models.ForeignKey(AccPermission, on_delete=models.CASCADE, default=0)
    social_security = models.IntegerField(null=True)

    # Add permissions and staff status fields
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)

    objects = UserManager()

    USERNAME_FIELD = 'email'  
    REQUIRED_FIELDS = ['first_name', 'last_name']  

    class Meta:
        db_table = "hr.users" 

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
        db_table = "hr.u_client"

class Employee(User):
   # role = models.ForeignKey(AccPermission, on_delete=models.CASCADE)
    #social_security = models.IntegerField()

    class Meta:
        db_table = "hr.u_employee"

class UserPasswordsDictionary(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, primary_key=True, related_name="password_history")
    hashed_password = models.CharField(max_length=255)
    valid_from = models.DateTimeField(default=timezone.now)
    valid_to = models.DateTimeField()

    class Meta:
        db_table = "sec.user_passwords_dictionary"

    def __str__(self):
        return f"Password history for {self.user.email}"
    

from django.db import models
from django.utils.timezone import now


class UserLoginAudit(models.Model):
    """
    Tracks user login timestamps for auditing purposes.
    """
    user_id = models.IntegerField()  # Reference to HR.USERS ID
    login_timestamp = models.DateTimeField(default=now)

    class Meta:
        db_table = "sec.user_login_audit"

    def __str__(self):
        return f"User {self.user_id} logged in at {self.login_timestamp}"


class ErrorLog(models.Model):
    """
    Logs application errors, including context and hints for debugging.
    """
    error_message = models.TextField()  # Detailed error message
    error_hint = models.CharField(max_length=400, blank=True, null=True)  # Optional hint
    error_context = models.CharField(max_length=400, blank=True, null=True)  # Context of the error
    error_timestamp = models.DateTimeField(auto_now_add=True)  # Timestamp of the error occurrence

    class Meta:
        db_table = "sec.error_log"

    def __str__(self):
        return f"Error {self.id} at {self.error_timestamp}"


class ChangeLog(models.Model):
    INSERT = 'INSERT'
    UPDATE = 'UPDATE'
    DELETE = 'DELETE'

    OPERATION_CHOICES = [
        (INSERT, 'Insert'),
        (UPDATE, 'Update'),
        (DELETE, 'Delete'),
    ]
    table_name = models.CharField(max_length=255)  # Name of the affected table
    operation_type = models.CharField(max_length=10, choices=OPERATION_CHOICES)  # Type of operation
    row_id = models.IntegerField()  # Primary key of the affected row
    changed_by = models.CharField(max_length=255, blank=True, null=True)  # User or system identifier
    change_timestamp = models.DateTimeField(default=now)  # Timestamp of the change

    class Meta:
        db_table = "sec.change_log"

    def __str__(self):
        return f"{self.operation_type} on {self.table_name} (Row ID {self.row_id}) by {self.changed_by}"


class AuditLog(models.Model):
    """
    Records user actions for security and monitoring purposes.
    """
    CREATE = 'CREATE'
    UPDATE = 'UPDATE'
    DELETE = 'DELETE'
    OTHER = 'OTHER'

    ACTION_CHOICES = [
        (CREATE, 'Create'),
        (UPDATE, 'Update'),
        (DELETE, 'Delete'),
        (OTHER, 'Other'),
    ]

    username = models.CharField(max_length=255)  # Username of the actor
    action_type = models.CharField(max_length=50, choices=ACTION_CHOICES)  # Action performed
    table_name = models.CharField(max_length=255, blank=True, null=True)  # Target table name
    row_id = models.IntegerField(blank=True, null=True)  # ID of the affected row
    action_timestamp = models.DateTimeField(default=now)  # Timestamp of the action

    class Meta:
        db_table = "sec.audit_log"

    def __str__(self):
        return f"{self.action_type} action by {self.username} on {self.table_name} at {self.action_timestamp}"


