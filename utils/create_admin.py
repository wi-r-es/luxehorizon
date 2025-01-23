from utils.funcs import hash_password, safe_execute

def create_super_admin(cursor, self):
    hashed_password = hash_password('root')
    safe_execute(cursor, 
        f"""
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
        """, 
        success_message="Super admin added.",
        error_message="Error adding Super admin")
    
    cursor.execute(f"""
        SELECT id FROM "hr.users"
        WHERE email = 'god@luxehorizon.com';
    """)
    new_user_id = cursor.fetchone()[0]
                
    # Update the Role to Manager Level
    safe_execute(
                    cursor,
                    f"CALL sp_update_employee_role({new_user_id}, 1);",
                    success_message=f"Role updated for Super admin.",
                    error_message=f"Error updating role for Super admin"
                )
                
    self.stdout.write(f"General Admin for luxehorizon chain hotels added with user ID {new_user_id}.")