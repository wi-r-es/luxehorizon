# Generated by Django 4.2.17 on 2025-01-11 21:32

from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Invoice',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('final_value', models.DecimalField(decimal_places=2, max_digits=10)),
                ('emission_date', models.DateField(default=django.utils.timezone.now)),
                ('billing_date', models.DateField(null=True)),
                ('invoice_status', models.BooleanField()),
            ],
            options={
                'db_table': 'finance.invoice',
            },
        ),
        migrations.CreateModel(
            name='PaymentMethod',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('descriptive', models.CharField(max_length=100, unique=True)),
            ],
            options={
                'db_table': 'finance.payment_method',
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
                'db_table': 'finance.payments',
            },
        ),
    ]
