# Generated by Django 4.2.17 on 2025-01-11 21:32

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('hotel_management', '0002_create_room_types'),
    ]

    operations = [
        migrations.CreateModel(
            name='Commodity',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('details', models.CharField(max_length=100)),
            ],
            options={
                'db_table': 'room_management.commodity',
            },
        ),
        migrations.CreateModel(
            name='Hotel',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('h_name', models.CharField(max_length=100)),
                ('full_address', models.CharField(max_length=160)),
                ('postal_code', models.CharField(max_length=8)),
                ('city', models.CharField(max_length=100)),
                ('email', models.EmailField(max_length=100)),
                ('telephone', models.CharField(max_length=20)),
                ('details', models.CharField(max_length=200)),
                ('stars', models.IntegerField()),
            ],
            options={
                'db_table': 'management.hotel',
            },
        ),
        migrations.CreateModel(
            name='HotelEmployees',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
            ],
            options={
                'db_table': 'management.hotel_employee',
            },
        ),
        migrations.CreateModel(
            name='Room',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('room_number', models.IntegerField()),
                ('base_price', models.DecimalField(decimal_places=2, max_digits=10)),
                ('condition', models.IntegerField()),
                ('hotel', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='hotel_management.hotel')),
            ],
            options={
                'db_table': 'room_management.room',
            },
        ),
        migrations.AlterModelTable(
            name='roomtype',
            table='room_management.room_types',
        ),
        migrations.CreateModel(
            name='RoomCommodity',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('commodity', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='hotel_management.commodity')),
                ('room', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='hotel_management.room')),
            ],
            options={
                'db_table': 'room_management.room_commodity',
            },
        ),
        migrations.AddField(
            model_name='room',
            name='room_type',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='hotel_management.roomtype'),
        ),
    ]
