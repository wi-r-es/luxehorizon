# Generated by Django 4.2.17 on 2025-01-11 21:32

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('reservation', '0001_initial'),
        ('billing', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='invoice',
            name='client',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='invoices', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='invoice',
            name='payment_method',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='invoices', to='billing.paymentmethod'),
        ),
        migrations.AddField(
            model_name='invoice',
            name='reservation',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='invoices', to='reservation.reservation'),
        ),
        migrations.AddConstraint(
            model_name='payment',
            constraint=models.CheckConstraint(check=models.Q(('payment_amount__gt', 0)), name='ck_payment_amount_positive'),
        ),
        migrations.AddConstraint(
            model_name='invoice',
            constraint=models.CheckConstraint(check=models.Q(('invoice_status__in', [True, False])), name='ck_invoice_status'),
        ),
    ]
