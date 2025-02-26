from utils.hotels import hotels
from utils.funcs import hash_password, safe_execute
from hotel_management.models import HotelEmployees, Hotel
from users.models import User

def create_employees(cursor, self):
    hashed_password = hash_password('12345')
    # HOTEL 1
    safe_execute(cursor, """
        CALL sp_register_user(
            'Alice',
            'Sinclair',
            'alice.sinclair@example.com',
            %s,
            '111111111',
            '111111111',
            '123 Example Street',
            '3500-678',
            'Example City',
            'F',
            250250251
        );
    """, [hashed_password], 
        success_message="User Alice Sinclair added.",
        error_message="Error adding Alice Sinclair")
    cursor.execute(f"""
        SELECT id FROM "hr.users"
        WHERE email = 'alice.sinclair@example.com';
    """)
    new_user_id = cursor.fetchone()[0]
    # Update the Role to employee level
    safe_execute(
        cursor, 
        f"CALL sp_update_employee_role({new_user_id}, 3);",
        success_message=f"Role updated for Employee.",
        error_message=f"Error updating role for Employee")
    new_user = User.objects.get(id=new_user_id)
    hotel_var = Hotel.objects.get(id=1)
    # Link the employee to the Hotel
    HotelEmployees.objects.create(hotel=hotel_var, employee=new_user)
    self.stdout.write(f"Employee for {hotels[0]} added with user ID {new_user_id} and linked to hotel ID {1}.")

    safe_execute(
        cursor,
        """
            CALL sp_register_user(
                'Bob',
                'Johnson',
                'bob.johnson@example.com',
                %s,
                '111111112',
                '111111112',
                '123 Example Street',
                '3500-678',
                'Example City',
                'F',
                250250252
            );
        """, 
        [hashed_password],
        success_message="User Bob Johnson added.",
        error_message="Error adding Bob Johnson")
    cursor.execute(f"""
        SELECT id FROM "hr.users"
        WHERE email = 'bob.johnson@example.com';
    """)
    new_user_id = cursor.fetchone()[0]
    # Update the Role to employee Level
    safe_execute(
        cursor, 
        f"CALL sp_update_employee_role({new_user_id}, 3);",
        success_message=f"Role updated for Employee.",
        error_message=f"Error updating role for Employee")
    new_user = User.objects.get(id=new_user_id)
    # Link the employee to the Hotel
    HotelEmployees.objects.create(hotel=hotel_var, employee=new_user)
    self.stdout.write(f"Employee for {hotels[0]} added with user ID {new_user_id} and linked to hotel ID {1}.")

    safe_execute(
        cursor, 
        """
        CALL sp_register_user(
            'Mary',
            'Carrie',
            'mary.carrie@example.com',
            %s,
            '111111113',
            '111111113',
            '123 Example Street',
            '3500-678',
            'Example City',
            'F',
            250250253
        );
        """, 
        [hashed_password],
        success_message="User Mary Carrie added.",
        error_message="Error adding Mary Carrie")
    cursor.execute(f"""
        SELECT id FROM "hr.users"
        WHERE email = 'mary.carrie@example.com';
    """)
    new_user_id = cursor.fetchone()[0]
    # Update the Role to employee Level
    safe_execute(
        cursor, 
        f"CALL sp_update_employee_role({new_user_id}, 3);",
        success_message=f"Role updated for Employee.",
        error_message=f"Error updating role for Employee"
    )
    new_user = User.objects.get(id=new_user_id)
    # Link the employee to the Hotel
    HotelEmployees.objects.create(hotel=hotel_var, employee=new_user)
    self.stdout.write(f"Employee for {hotels[0]} added with user ID {new_user_id} and linked to hotel ID {1}.")

    # HOTEL 2
    safe_execute(
        cursor, 
        """
        CALL sp_register_user(
            'Snoop',
            'Dog',
            'snoop.dog@example.com',
            %s,
            '222222222',
            '222222222',
            '123 Example Street',
            '3500-678',
            'Example City',
            'F',
            250250254
        );
        """, 
        [hashed_password],
        success_message="User Snoop Dog added.",
        error_message="Error adding Snoop Dog")
    cursor.execute(f"""
        SELECT id FROM "hr.users"
        WHERE email = 'snoop.dog@example.com';
    """)
    new_user_id = cursor.fetchone()[0]
    # Update the Role to employee Level
    safe_execute(
        cursor, 
        f"CALL sp_update_employee_role({new_user_id}, 3);",
        success_message=f"Role updated for Employee.",
        error_message=f"Error updating role for Employee"
    )
    new_user = User.objects.get(id=new_user_id)
    hotel_var = Hotel.objects.get(id=2)
    # Link the employee to the Hotel
    HotelEmployees.objects.create(hotel=hotel_var, employee=new_user)
    self.stdout.write(f"Employee for {hotels[1]} added with user ID {new_user_id} and linked to hotel ID {2}.")

    safe_execute(
        cursor, 
        """
        CALL sp_register_user(
            'Fifty',
            'Cent',
            'fifty.cent@example.com',
            %s,
            '222222223',
            '222222223',
            '123 Example Street',
            '3500-678',
            'Example City',
            'F',
            250250255
        );
        """, 
        [hashed_password],
        success_message="User Fifty Cent added.",
        error_message="Error adding Fifty Cent")
    cursor.execute(f"""
        SELECT id FROM "hr.users"
        WHERE email = 'fifty.cent@example.com';
    """)
    new_user_id = cursor.fetchone()[0]
    # Update the Role to employee Level
    safe_execute(
        cursor, 
        f"CALL sp_update_employee_role({new_user_id}, 3);",
        success_message=f"Role updated for Employee.",
        error_message=f"Error updating role for Employee"
    )
    new_user = User.objects.get(id=new_user_id)
    # Link the employee to the Hotel
    HotelEmployees.objects.create(hotel=hotel_var, employee=new_user)
    self.stdout.write(f"Employee for {hotels[1]} added with user ID {new_user_id} and linked to hotel ID {2}.")

    # try: 
    #     cursor.execute("""
    #         CALL sp_register_user(
    #             'Mel',
    #             'Gibson',
    #             'mel.gibson@example.com',
    #             %s,
    #             '222222223',
    #             '222222223',
    #             '123 Example Street',
    #             '3500-678',
    #             'Example City',
    #             'F',
    #             250250256
    #         );
    #     """, [hashed_password])

    #     cursor.execute(f"""
    #     SELECT id FROM "hr.users"
    #     WHERE email = 'mel.gibson@example.com';
    #     """)
    #     result = cursor.fetchone()
    #     if result is None:
    #         raise ValueError("Failed to fetch user ID for Mel Gibson. Ensure the user was successfully registered.")
        
    #     new_user_id = result[0]
    #     # Update the Role to employee Level
    #     cursor.execute(f"CALL sp_update_employee_role({new_user_id}, 3);")
    #     #new_user = User.objects.get(id=new_user_id)
    #     # Link the employee to the Hotel
    #     HotelEmployees.objects.create(hotel=hotel_var, employee=new_user)
    #     self.stdout.write(f"Employee for {hotels[1]} added with user ID {new_user_id} and linked to hotel ID {2}.")
    # except Exception as e:
    #     self.stdout.write(f"Error during registration for Mel Gibson: {e}")
    #     raise

    

    # HOTEL 3
    safe_execute(
        cursor, 
        """
        CALL sp_register_user(
            'Ambrosio',
            'Gilberto',
            'ambrosio.gilberto@example.com',
            %s,
            '333333331',
            '333333331',
            '123 Example Street',
            '3500-678',
            'Example City',
            'F',
            250250257
        );
        """, 
        [hashed_password],
        success_message="User Ambrosio Gilberto added.",
        error_message="Error adding Ambrosio Gilberto")
    cursor.execute(f"""
        SELECT id FROM "hr.users"
        WHERE email = 'ambrosio.gilberto@example.com';
    """)
    new_user_id = cursor.fetchone()[0]
    # Update the Role to employee Level
    safe_execute(
        cursor, 
        f"CALL sp_update_employee_role({new_user_id}, 3);",
        success_message=f"Role updated for Employee.",
        error_message=f"Error updating role for Employee"
    )
    new_user = User.objects.get(id=new_user_id)
    hotel_var = Hotel.objects.get(id=3)
    # Link the employee to the Hotel
    HotelEmployees.objects.create(hotel=hotel_var, employee=new_user)
    self.stdout.write(f"Employee for {hotels[2]} added with user ID {new_user_id} and linked to hotel ID {3}.")

    safe_execute(
        cursor, 
        """
        CALL sp_register_user(
            'Simon',
            'Sixfinger',
            'simon.sixfinger@example.com',
            %s,
            '333333332',
            '333333332',
            '123 Example Street',
            '3500-678',
            'Example City',
            'F',
            250250258
        );
        """, 
        [hashed_password],
        success_message="User Simon Sixfinger added.",
        error_message="Error adding Simon Sixfinger")
    cursor.execute(f"""
        SELECT id FROM "hr.users"
        WHERE email = 'simon.sixfinger@example.com';
    """)
    new_user_id = cursor.fetchone()[0]
    # Update the Role to employee Level
    safe_execute(
        cursor, 
        f"CALL sp_update_employee_role({new_user_id}, 3);",
        success_message=f"Role updated for Employee.",
        error_message=f"Error updating role for Employee"
    )
    new_user = User.objects.get(id=new_user_id)
    # Link the employee to the Hotel
    HotelEmployees.objects.create(hotel=hotel_var, employee=new_user)
    self.stdout.write(f"Employee for {hotels[2]} added with user ID {new_user_id} and linked to hotel ID {3}.")

    safe_execute(
        cursor, 
        """
        CALL sp_register_user(
            'Robin',
            'Mamassita',
            'robin.mamassita@example.com',
            %s,
            '333333333',
            '333333333',
            '123 Example Street',
            '3500-678',
            'Example City',
            'F',
            250250259
        );
        """, 
        [hashed_password],
        success_message="User Robin Mamassita added.",
        error_message="Error adding Robin Mamassita")
    cursor.execute(f"""
        SELECT id FROM "hr.users"
        WHERE email = 'robin.mamassita@example.com';
    """)
    new_user_id = cursor.fetchone()[0]
    # Update the Role to employee Level
    safe_execute(
        cursor, 
        f"CALL sp_update_employee_role({new_user_id}, 3);",
        success_message=f"Role updated for Employee.",
        error_message=f"Error updating role for Employee"
    )
    new_user = User.objects.get(id=new_user_id)
    # Link the employee to the Hotel
    HotelEmployees.objects.create(hotel=hotel_var, employee=new_user)
    self.stdout.write(f"Employee for {hotels[2]} added with user ID {new_user_id} and linked to hotel ID {3}.")

    # HOTEL 4
    safe_execute(
        cursor, 
        """
        CALL sp_register_user(
            'Violet',
            'Green',
            'violet.green@example.com',
            %s,
            '444444441',
            '444444441',
            '123 Example Street',
            '3500-678',
            'Example City',
            'F',
            250250260
        );
        """, 
        [hashed_password],
        success_message="User Violet Green added.",
        error_message="Error adding Violet Green")
    cursor.execute(f"""
        SELECT id FROM "hr.users"
        WHERE email = 'violet.green@example.com';
    """)
    new_user_id = cursor.fetchone()[0]
    # Update the Role to employee Level
    safe_execute(
        cursor, 
        f"CALL sp_update_employee_role({new_user_id}, 3);",
        success_message=f"Role updated for Employee.",
        error_message=f"Error updating role for Employee"
    )
    hotel_var = Hotel.objects.get(id=4)
    new_user = User.objects.get(id=new_user_id)
    # Link the employee to the Hotel
    HotelEmployees.objects.create(hotel=hotel_var, employee=new_user)
    self.stdout.write(f"Employee for {hotels[3]} added with user ID {new_user_id} and linked to hotel ID {4}.")

    safe_execute(
        cursor, 
        """
        CALL sp_register_user(
            'Clover',
            'Morgan',
            'clover.morgan@example.com',
            %s,
            '444444442',
            '444444442',
            '123 Example Street',
            '3500-678',
            'Example City',
            'F',
            250250261
        );
        """, 
        [hashed_password],
        success_message="User Clover Morgan added.",
        error_message="Error adding Clover Morgan")
    cursor.execute(f"""
        SELECT id FROM "hr.users"
        WHERE email = 'clover.morgan@example.com';
    """)
    new_user_id = cursor.fetchone()[0]
    # Update the Role to employee Level
    safe_execute(
        cursor, 
        f"CALL sp_update_employee_role({new_user_id}, 3);",
        success_message=f"Role updated for Employee.",
        error_message=f"Error updating role for Employee"
    )
    new_user = User.objects.get(id=new_user_id)
    # Link the employee to the Hotel
    HotelEmployees.objects.create(hotel=hotel_var, employee=new_user)
    self.stdout.write(f"Employee for {hotels[3]} added with user ID {new_user_id} and linked to hotel ID {4}.")

    safe_execute(
        cursor, 
        """
        CALL sp_register_user(
            'Goosey',
            'Maclain',
            'goosey.maclain@example.com',
            %s,
            '444444443',
            '444444443',
            '123 Example Street',
            '3500-678',
            'Example City',
            'F',
            250250262
        );
        """, 
        [hashed_password],
        success_message="User Goosey Maclain added.",
        error_message="Error adding Goosey Maclain")
    cursor.execute(f"""
        SELECT id FROM "hr.users"
        WHERE email = 'goosey.maclain@example.com';
    """)
    new_user_id = cursor.fetchone()[0]
    # Update the Role to employee Level
    safe_execute(
        cursor, 
        f"CALL sp_update_employee_role({new_user_id}, 3);",
        success_message=f"Role updated for Employee.",
        error_message=f"Error updating role for Employee"
    )
    new_user = User.objects.get(id=new_user_id)
    # Link the employee to the Hotel
    HotelEmployees.objects.create(hotel=hotel_var, employee=new_user)
    self.stdout.write(f"Employee for {hotels[3]} added with user ID {new_user_id} and linked to hotel ID {4}.")

    # HOTEL 5
    safe_execute(
        cursor, 
        """
            CALL sp_register_user(
                'Deliah',
                'Ishere',
                'delilah.ishere@example.com',
                %s,
                '444444444',
                '444444444',
                '123 Example Street',
                '3500-678',
                'Example City',
                'F',
                250250263
            );
        """, 
        [hashed_password],
        success_message="User Deliah Ishere added.",
        error_message="Error adding Deliah Ishere")
    cursor.execute(f"""
        SELECT id FROM "hr.users"
        WHERE email = 'delilah.ishere@example.com';
    """)
    new_user_id = cursor.fetchone()[0]
    # Update the Role to employee Level
    safe_execute(
        cursor, 
        f"CALL sp_update_employee_role({new_user_id}, 3);",
        success_message=f"Role updated for Employee.",
        error_message=f"Error updating role for Employee"
    )
    new_user = User.objects.get(id=new_user_id)
    hotel_var = Hotel.objects.get(id=5)
    # Link the employee to the Hotel
    HotelEmployees.objects.create(hotel=hotel_var, employee=new_user)
    self.stdout.write(f"Employee for {hotels[4]} added with user ID {new_user_id} and linked to hotel ID {5}.")

    safe_execute(
        cursor, 
        """
        CALL sp_register_user(
            'Harper',
            'Ferrari',
            'harper.ferrarit@example.com',
            %s,
            '444444445',
            '444444445',
            '123 Example Street',
            '3500-678',
            'Example City',
            'F',
            250250264
        );
        """, 
        [hashed_password],
        success_message="User Harper Ferrari added.",
        error_message="Error adding Harper Ferrari")
    cursor.execute(f"""
        SELECT id FROM "hr.users"
        WHERE email = 'harper.ferrarit@example.com';
    """)
    new_user_id = cursor.fetchone()[0]
    # Update the Role to employee Level
    safe_execute(
        cursor, 
        f"CALL sp_update_employee_role({new_user_id}, 3);",
        success_message=f"Role updated for Employee.",
        error_message=f"Error updating role for Employee")
    new_user = User.objects.get(id=new_user_id)
    # Link the employee to the Hotel
    HotelEmployees.objects.create(hotel=hotel_var, employee=new_user)
    self.stdout.write(f"Employee for {hotels[4]} added with user ID {new_user_id} and linked to hotel ID {5}.")

    safe_execute(
        cursor, 
        """
        CALL sp_register_user(
            'Austin',
            'Elliot',
            'austin.elliot@example.com',
            %s,
            '444444446',
            '444444446',
            '123 Example Street',
            '3500-678',
            'Example City',
            'F',
            250250265
        );
        """, 
        [hashed_password],
        success_message="User Austin Elliot added.",
        error_message="Error adding Austin Elliot")
    cursor.execute(f"""
        SELECT id FROM "hr.users"
        WHERE email = 'austin.elliot@example.com';
    """)
    new_user_id = cursor.fetchone()[0]
    # Update the Role to employee Level
    safe_execute(
        cursor, 
        f"CALL sp_update_employee_role({new_user_id}, 3);",
        success_message=f"Role updated for Employee.",
        error_message=f"Error updating role for Employee")
    new_user = User.objects.get(id=new_user_id)
    # Link the employee to the Hotel
    HotelEmployees.objects.create(hotel=hotel_var, employee=new_user)
    self.stdout.write(f"Employee for {hotels[4]} added with user ID {new_user_id} and linked to hotel ID {5}.")

    safe_execute(
        cursor, 
        """
        CALL sp_register_user(
            'Dominic',
            'Bennet',
            'dominic.bennet@example.com',
            %s,
            '444444447',
            '444444447',
            '123 Example Street',
            '3500-678',
            'Example City',
            'F',
            250250266
        );
        """, 
        [hashed_password],
        success_message="User Dominic Bennet added.",
        error_message="Error adding Dominic Bennet")
    cursor.execute(f"""
        SELECT id FROM "hr.users"
        WHERE email = 'dominic.bennet@example.com';
    """)
    new_user_id = cursor.fetchone()[0]
    # Update the Role to employee Level
    safe_execute(
        cursor, 
        f"CALL sp_update_employee_role({new_user_id}, 3);",
        success_message=f"Role updated for Employee.",
        error_message=f"Error updating role for Employee"
    )
    new_user = User.objects.get(id=new_user_id)
    # Link the employee to the Hotel
    HotelEmployees.objects.create(hotel=hotel_var, employee=new_user)
    self.stdout.write(f"Employee for {hotels[4]} added with user ID {new_user_id} and linked to hotel ID {5}.")
