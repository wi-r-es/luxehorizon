from datetime import datetime, timedelta
from django.core.management.base import BaseCommand
from django.db import connection
from utils.funcs import hash_password, safe_execute
from hotel_management.models import HotelEmployees, Hotel
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
            safe_execute(cursor, """
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
            """,[hashed_password],
                success_message="User John Doe added.",
                error_message="Error adding user John Doe")

            safe_execute(cursor, """
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
            """,[hashed_password],
                success_message="User John NotDoe added.",
                error_message="Error adding user John NotDoe")

            # FICTIONAL CLIENTS
            for i in range(1, 10):
                safe_execute(cursor, f"""
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
                        """,
                        success_message=f"Client {i} added.",
                        error_message=f"Error adding client {i}"
                    )

            
            # Add Hotels
            for name, address, postal_code, city, stars in hotels:
                # Check if the hotel already exists
                cursor.execute("""
                    SELECT 1
                    FROM "management.hotel"
                    WHERE h_name = %s
                """, [name])
                
                if cursor.fetchone():
                    self.stdout.write(f"Hotel {name} already exists. Skipping.")
                else:
                    # Add the hotel if it does not exist
                    safe_execute(
                        cursor,
                        f"""
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
                        """,
                        success_message=f"Hotel {name} added.",
                        error_message=f"Error adding hotel {name}"
                    )

                #self.stdout.write(f"Hotel---> {name} added .")
            ## MANAGERS
            hashed_password = hash_password('admin')
            for i, (hotel_name, _, _, city, _) in enumerate(hotels, start=1):
                safe_execute(cursor, f"""
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
                    """,
                    success_message=f"Manager for {hotel_name} added.",
                    error_message=f"Error adding manager for {hotel_name}")
                
                try:
                    cursor.execute(f"""
                        SELECT id FROM "hr.users"
                        WHERE email = 'manager{i}@{hotel_name.lower().replace(" ", "")}.com';
                    """)
                    new_user_id = cursor.fetchone()[0]
                    new_user = User.objects.get(id=new_user_id)
                    hotel_var = Hotel.objects.get(id=i)
                    HotelEmployees.objects.create(hotel=hotel_var, employee=new_user)

                    # Update Role
                    safe_execute(
                        cursor,
                        f"CALL sp_update_employee_role({new_user_id}, 2);",
                        success_message=f"Role updated for manager of {hotel_name}.",
                        error_message=f"Error updating role for manager of {hotel_name}"
                    )
                except Exception as e:
                    self.stdout.write(f"Error linking manager for {hotel_name}: {e}")
            


            
            ## EMPLOYEES
            create_employees(cursor, self)
            


            

            #Add Rooms
            create_rooms(cursor, self)

            # Add Commodities
            for commodity in commodities:
                safe_execute(
                    cursor,
                    f"CALL sp_create_commodity('{commodity}');",
                    success_message=f"Commodity {commodity} added.",
                    error_message=f"Error adding commodity {commodity}"
                )

            # Fetch all rooms and their type initials
            cursor.execute('SELECT id, room_type_id FROM "room_management.room";')
            rooms = cursor.fetchall()

            # Fetch all room types for mapping initials
            cursor.execute('SELECT id, type_initials FROM "room_management.room_types";')
            room_types = {row[0]: row[1] for row in cursor.fetchall()}  # {room_type_id: type_initials}

            # Link commodities to rooms based on type
            for room_id, room_type_id in rooms:
                # Get the type initials for the room
                room_type_initials = room_types.get(room_type_id)

                # Determine the room key for commodity mapping
                room_key = room_type_initials[:2] if room_type_initials.startswith('PH') else room_type_initials[0]  # Handle "P" for Penthouse
                commodity_ids = room_commodities.get(room_key, [])  # Get commodities for the room type

                for commodity_id in commodity_ids:
                    # Use the stored procedure to link the commodity to the room
                    safe_execute(
                        cursor,
                        f"CALL sp_link_commodity_to_room({room_id}, {commodity_id});",
                        success_message=f"Linked commodity {commodity_id} to room {room_id}.",
                        error_message=f"Error linking commodity {commodity_id} to room {room_id}"
                    )

            # # Update Room Status
            # for room_id in range(1, 11):
            #     cursor.execute(f"CALL sp_update_room_status({room_id}, 1);")

            # Create Reservations
            create_reservations(cursor, self)

            # Generate Invoices
            generate_invoices(cursor, self)

            # Add Payments or cancel
            add_payments_or_cancel_reservs(cursor, self)

            

            self.stdout.write(self.style.SUCCESS("Bulk insert completed successfully."))

