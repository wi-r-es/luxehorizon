from django.db import models
from django.utils import timezone
from users.models import User
from reservation.models import Reservation


class PaymentMethod(models.Model):
    descriptive = models.CharField(max_length=100, unique=True)

    class Meta:
        db_table = 'payment_method'

    def __str__(self):
        return self.descriptive


class Invoice(models.Model):
    reservation = models.ForeignKey('reservation.Reservation', on_delete=models.CASCADE, related_name='invoices')
    client = models.ForeignKey('users.User', on_delete=models.CASCADE, related_name='invoices')
    final_value = models.DecimalField(max_digits=10, decimal_places=2)
    emission_date = models.DateField(default=timezone.now)
    billing_date = models.DateField()
    invoice_status = models.BooleanField() 
    payment_method = models.ForeignKey(PaymentMethod, on_delete=models.CASCADE, related_name='invoices')

    class Meta:
        db_table = 'invoice'
        constraints = [
            models.CheckConstraint(
                check=models.Q(invoice_status__in=[True, False]),
                name="ck_invoice_status",
            ),
        ]

    def __str__(self):
        return f"Invoice {self.id} - {self.client}"
