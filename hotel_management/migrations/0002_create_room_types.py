from django.db import migrations, models
from ..fields import PostgreSQLEnumField

class Migration(migrations.Migration):
    dependencies = [
        ('hotel_management', '0001_create_enum_types'),
    ]

    operations = [
        migrations.CreateModel(
            name='RoomType',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('type_initials', models.CharField(max_length=100)),
                ('room_view', PostgreSQLEnumField('room_view_type')),
                ('room_quality', PostgreSQLEnumField('room_quality_type')),
            ],
            options={
                'db_table': 'room_management_room_types',
            },
        ),
    ]