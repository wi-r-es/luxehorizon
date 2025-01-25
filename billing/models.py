from django.db import models
from django.utils import timezone
from users.models import User
from reservation.models import Reservation

class PaymentMethod(models.Model):
    descriptive = models.CharField(max_length=100, unique=True)

    class Meta:
        db_table = 'finance.payment_method'

    def __str__(self):
        return self.descriptive


class Invoice(models.Model):
    reservation = models.ForeignKey('reservation.Reservation', on_delete=models.CASCADE, related_name='invoices')
    client = models.ForeignKey(User, on_delete=models.CASCADE, related_name='invoices')
    final_value = models.DecimalField(max_digits=10, decimal_places=2)
    emission_date = models.DateField(default=timezone.now)
    billing_date = models.DateField(null=True)
    invoice_status = models.BooleanField() 
    payment_method = models.ForeignKey(PaymentMethod, on_delete=models.CASCADE, related_name='invoices')

    class Meta:
        db_table = 'finance.invoice'
        constraints = [
            models.CheckConstraint(
                check=models.Q(invoice_status__in=[True, False]),
                name="ck_invoice_status",
            ),
        ]
        indexes = [
            models.Index(fields=['emission_date', 'billing_date'], name='idx_invoice_dates'),
            models.Index(fields=['invoice_status', 'payment_method'], name='idx_invoice_status_method'),
            models.Index(fields=['client', 'emission_date'], name='idx_invoice_client_date'),
            models.Index(fields=['reservation', 'invoice_status'], name='idx_invoice_res_status')
        ]

    def __str__(self):
        return f"Invoice {self.id} - {self.client}"

class Payment(models.Model):
    invoice = models.ForeignKey(
        'Invoice', 
        on_delete=models.CASCADE, 
        related_name='payments', 
        db_column='invoice_id'
    )
    payment_amount = models.DecimalField(max_digits=10, decimal_places=2)
    payment_date = models.DateField(default=timezone.now)
    payment_method = models.ForeignKey(
        'PaymentMethod', 
        on_delete=models.CASCADE, 
        related_name='payments', 
        db_column='payment_method_id'
    )

    class Meta:
        db_table = 'finance.payments'
        constraints = [
            models.CheckConstraint(
                check=models.Q(payment_amount__gt=0),
                name='ck_payment_amount_positive',
            ),
        ]
        indexes = [
            models.Index(fields=['payment_date', 'payment_method'], name='idx_payment_date_method'),
            models.Index(fields=['invoice', 'payment_date'], name='idx_payment_invoice_date')
        ]

    def __str__(self):
        return f"Payment {self.id} - Invoice {self.invoice.id}"

