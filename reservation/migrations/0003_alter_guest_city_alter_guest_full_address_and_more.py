# Generated by Django 4.2.17 on 2025-01-11 15:52

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('reservation', '0002_alter_reservation_status'),
    ]

    operations = [
        migrations.AlterField(
            model_name='guest',
            name='city',
            field=models.CharField(max_length=100, null=True),
        ),
        migrations.AlterField(
            model_name='guest',
            name='full_address',
            field=models.CharField(max_length=160, null=True),
        ),
        migrations.AlterField(
            model_name='guest',
            name='postal_code',
            field=models.CharField(max_length=8, null=True),
        ),
    ]
