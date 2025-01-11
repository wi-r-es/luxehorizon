import random
from datetime import datetime, timedelta
from django.core.management.base import BaseCommand
from django.db import connection

class Command(BaseCommand):
    help = "Perform a bulk insert of test data into the database."

    def handle(self, *args, **kwargs):
        with connection.cursor() as cursor:
            self.stdout.write("Starting bulk insert...")

            # Add Users    - 1 Admin - 5 Managers (1 per hotel) - 3 employees por hotel - clients
            cursor.execute("""
            CALL sp_register_user(
                'John',
                'Doe',
                'john.doe@example.com',
                'hashed_password_example',
                '123456789',
                '987654321',
                '123 Example Street',
                '3500-678',
                'Example City',
                'C'
            );
            """)

            cursor.execute("""
            CALL sp_register_user(
                'John',
                'NotDoe',
                'john.notdoe@example.com',
                'hashed_password_example',
                '123456799',
                '987654322',
                '123 Example Street',
                '3500-678',
                'Example City',
                'F',
                250250250
            );
            """)

            # Add additional users
            for i in range(1, 5):
                cursor.execute(f"""
                CALL sp_register_user(
                    'Client{i}',
                    'Test',
                    'user{i}@example.com',
                    'hashed_password_{i}',
                    '999888777{i}',
                    '987654320{i}',
                    'Street {i}',
                    '1000-{i}',
                    'City{i}',
                    {'F' if i % 2 == 0 else 'C'}
                );
                """)

                

            # Update Employee Role
            cursor.execute("CALL sp_update_employee_role(2, 2);")

            # Update User Status
            cursor.execute("CALL sp_update_user_status(2, FALSE);")

            # Add Hotels
            hotels = [
                ('Grand Luxe Hotel', '123 Elm Street', '1234-678', 'Viseu', 5),
                ('Lisboa Premium Suites', '456 Maple Ave', '5678-123', 'Lisboa', 4),
                ('Porto Comfort', '789 Oak Lane', '6789-456', 'Porto', 3),
                ('Algarve Sun Resort', '321 Palm Beach Rd', '8765-432', 'Algarve', 5),
                ('Douro Valley Retreat', '987 Wine St', '3456-789', 'Douro', 5)
            ]
            for name, address, postal_code, city, stars in hotels:
                cursor.execute(f"""
                CALL sp_add_hotel(
                    '{name}',
                    '{address}',
                    '{postal_code}',
                    '{city}',
                    'info@{name.lower().replace(" ", "")}.com',
                    '123456789',
                    'Description for {name}',
                    {stars}
                );
                """)

            # Add Rooms
            for hotel_id in range(1, 6):
                for room_number in range(1, 13):
                    cursor.execute(f"""
                    CALL sp_add_room(
                        {hotel_id},
                        'TYPE{room_number}',
                        {100 + room_number},
                        {room_number * 100.00},
                        0
                    );
                    """)

            # Add Commodities
            for i in range(1, 11):
                cursor.execute(f"CALL sp_create_commodity('Commodity {i}');")

            # Link Commodities to Rooms
            for room_id in range(1, 21):
                cursor.execute(f"CALL sp_link_commodity_to_room({room_id}, {(room_id % 10) + 1});")

            # Update Room Status
            for room_id in range(1, 11):
                cursor.execute(f"CALL sp_update_room_status({room_id}, 1);")

            # Create Reservations
            start_date = datetime.now().date()
            for i in range(1, 6):
                cursor.execute(f"""
                CALL sp_create_reservation(
                    {i},
                    {i},
                    '{start_date + timedelta(days=i)}',
                    '{start_date + timedelta(days=i+5)}',
                    2
                );
                """)

            # Add Payments
            for i in range(1, 6):
                cursor.execute(f"CALL sp_add_payment({i}, {500.00 * i}, 1);")

            # Generate Invoices
            for i in range(1, 6):
                cursor.execute(f"CALL sp_generate_invoice({i}, 1);")

            self.stdout.write(self.style.SUCCESS("Bulk insert completed successfully."))

