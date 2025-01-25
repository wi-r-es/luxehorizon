# Generated by Django 4.2.17 on 2025-01-25 21:20

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('reservation', '0002_initial'),
    ]

    operations = [
        migrations.AddIndex(
            model_name='guest',
            index=models.Index(fields=['reservation', 'cc_pass'], name='idx_guest_res_cc'),
        ),
        migrations.AddIndex(
            model_name='guest',
            index=models.Index(fields=['full_name'], name='idx_guest_name'),
        ),
        migrations.AddIndex(
            model_name='reservation',
            index=models.Index(fields=['begin_date', 'end_date'], name='idx_reservation_dates'),
        ),
        migrations.AddIndex(
            model_name='reservation',
            index=models.Index(fields=['status', 'client'], name='idx_reservation_status_client'),
        ),
        migrations.AddIndex(
            model_name='reservation',
            index=models.Index(fields=['season', 'status'], name='idx_reservation_season_status'),
        ),
        migrations.AddIndex(
            model_name='roomreservation',
            index=models.Index(fields=['room', 'reservation'], name='idx_roomres_room_res'),
        ),
    ]
