from utils.funcs import hash_password

def create_super_admin(cursor, self):
    hashed_password = hash_password('root')
    cursor.execute(f"""
        CALL sp_register_user(
        'Allseeing',
        'Admin',
        'god@luxehorizon.com',
        '{hashed_password}',
        '000000000',
        '000000000',
        'ThyHeaven',
        '0000-000',
        'CloudCity',
        'F',
        {000000000}
        );
    """)
    cursor.execute(f"""
        SELECT id FROM "hr.users"
        WHERE email = 'god@luxehorizon.com';
    """)
    new_user_id = cursor.fetchone()[0]
                
    # Update the Role to Manager Level
    cursor.execute(f"CALL sp_update_employee_role({new_user_id}, 1);") 
                
    self.stdout.write(f"General Admin for luxehorizon chain hotels added with user ID {new_user_id}.")