from datetime import datetime, timedelta
from django.core.management.base import BaseCommand
from django.db import connection
from utils.funcs import hash_password
from hotel_management.models import HotelEmployees
from users.models import User
from utils.hotels import hotels, commodities, room_commodities
from utils.create_admin import create_super_admin
from utils.create_employees import create_employees
from utils.create_rooms import create_rooms
from utils.create_reservations import create_reservations
from utils.add_payments_or_cancel_reservs import add_payments_or_cancel_reservs
from utils.generate_invoices import generate_invoices



    



class Command(BaseCommand):
    help = "Perform a bulk insert of test data into the database."

    def handle(self, *args, **kwargs):
        with connection.cursor() as cursor:
            self.stdout.write("Starting bulk insert...")
            
            try:
                create_super_admin(cursor, self)
            except Exception as e:
                self.stdout.write(f"Error registering user: {e}")

            hashed_password = hash_password('password')
            # Add Users    - 1 Admin - 5 Managers (1 per hotel) - 3 employees por hotel - clients
            cursor.execute("""
            CALL sp_register_user(
                'John',
                'Doe',
                'john.doe@example.com',
                 %s,
                '123456789',
                '987654321',
                '123 Example Street',
                '3500-678',
                'Example City',
                'C'
            );
            """,[hashed_password])

            cursor.execute("""
            CALL sp_register_user(
                'John',
                'NotDoe',
                'john.notdoe@example.com',
                 %s,
                '123456799',
                '987654322',
                '123 Example Street',
                '3500-678',
                'Example City',
                'F',
                250250250
            );
            """,[hashed_password])

            # FICTIONAL CLIENTS
            for i in range(1, 10):
                cursor.execute(f"""
                CALL sp_register_user(
                    'Client{i}',
                    'Test',
                    'user{i}@example.com',
                    '{hashed_password}',
                    '999888777{i}',
                    '987654320{i}',
                    'Street {i}',
                    '1000-{i}',
                    'City{i}',
                    'C'
                );
                """)

            
            # Add Hotels
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
            ## MANAGERS
            hashed_password = hash_password('admin')
            for i, (hotel_name, _, _, city, _) in enumerate(hotels, start=1):
                cursor.execute(f"""
                    CALL sp_register_user(
                        'Manager',
                        '{hotel_name}',
                        'manager{i}@{hotel_name.lower().replace(" ", "")}.com',
                        '{hashed_password}',
                        '111222333{i}',
                        '999888777{i}',
                        '{hotel_name} HQ',
                        '4000-{i}',
                        '{city}',
                        'F',
                        {100000000 + i}
                    );
                """)
                cursor.execute(f"""
                    SELECT id FROM "hr.users"
                    WHERE email = 'manager{i}@{hotel_name.lower().replace(" ", "")}.com';
                """)
                new_user_id = cursor.fetchone()[0]
                new_user = User.objects.get(id=new_user_id)
                # Update the Role to Manager Level
                cursor.execute(f"CALL sp_update_employee_role({new_user_id}, 2);") 
                hotel_var = Hotel.objects.get(id=i)
                # Link the Manager to the Hotel
                HotelEmployees.objects.create(hotel=hotel_var, employee=new_user)
                
                self.stdout.write(f"Manager for {hotel_name} added with user ID {new_user_id} and linked to hotel ID {i}.")

            


            
            ## EMPLOYEES
            create_employees(cursor, self)
            


            
#here
            #Add Rooms
            create_rooms(cursor, self)

            # Add Commodities
            for commodity in commodities:
                cursor.execute(f"CALL sp_create_commodity('{commodity}');")
                self.stdout.write(f"Added Commodity: {commodity}")

            # Fetch all rooms and their type initials
            cursor.execute("SELECT id, room_type FROM room_management.room;")
            rooms = cursor.fetchall()

            # Link commodities to rooms based on type
            for room_id, room_type in rooms:
                room_key = room_type[:2] if room_type.startswith('PH') else room_type[0]  # Handle 'PH' for PENTHOUSE
                commodity_ids = room_commodities.get(room_key, [])  # Get commodities for the room type

                for commodity_id in commodity_ids:
                    cursor.execute(f"""
                    CALL sp_link_commodity_to_room({room_id}, {commodity_id});
                    """)
                    self.stdout.write(f"Linked Commodity ID {commodity_id} to Room ID {room_id} (Type {room_type})")

            # # Update Room Status
            # for room_id in range(1, 11):
            #     cursor.execute(f"CALL sp_update_room_status({room_id}, 1);")

            # Create Reservations
            create_reservations(cursor, self)

            # Add Payments or cancel
            add_payments_or_cancel_reservs(cursor, self)

            # Generate Invoices
            generate_invoices(cursor, self)

            self.stdout.write(self.style.SUCCESS("Bulk insert completed successfully."))

