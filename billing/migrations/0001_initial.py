# Generated by Django 5.1.1 on 2024-12-23 19:26

import django.db.models.deletion
import django.utils.timezone
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('reservation', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='PaymentMethod',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('descriptive', models.CharField(max_length=100, unique=True)),
            ],
            options={
                'db_table': 'FINANCE.payment_method',
            },
        ),
        migrations.CreateModel(
            name='Invoice',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('final_value', models.DecimalField(decimal_places=2, max_digits=10)),
                ('emission_date', models.DateField(default=django.utils.timezone.now)),
                ('billing_date', models.DateField()),
                ('invoice_status', models.BooleanField()),
                ('client', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='invoices', to=settings.AUTH_USER_MODEL)),
                ('reservation', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='invoices', to='reservation.reservation')),
                ('payment_method', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='invoices', to='billing.paymentmethod')),
            ],
            options={
                'db_table': 'FINANCE.invoice',
            },
        ),
        migrations.CreateModel(
            name='Payment',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('payment_amount', models.DecimalField(decimal_places=2, max_digits=10)),
                ('payment_date', models.DateField(default=django.utils.timezone.now)),
                ('invoice', models.ForeignKey(db_column='invoice_id', on_delete=django.db.models.deletion.CASCADE, related_name='payments', to='billing.invoice')),
                ('payment_method', models.ForeignKey(db_column='payment_method_id', on_delete=django.db.models.deletion.CASCADE, related_name='payments', to='billing.paymentmethod')),
            ],
            options={
                'db_table': 'FINANCE.payments',
                'constraints': [models.CheckConstraint(condition=models.Q(('payment_amount__gt', 0)), name='ck_payment_amount_positive')],
            },
        ),
        migrations.AddConstraint(
            model_name='invoice',
            constraint=models.CheckConstraint(condition=models.Q(('invoice_status__in', [True, False])), name='ck_invoice_status'),
        ),
    ]
