from django.db import migrations
import os

def load_sql_from_file(apps, schema_editor):
    # Caminho para o ficheiro de procedures
    file_paths = [
        os.path.join(os.path.dirname(__file__), '..\..\db-init\d_dashboard_logic_objects.sql'),
        os.path.join(os.path.dirname(__file__), '..\..\db-init\a_security_logic_objects.sql'),
        os.path.join(os.path.dirname(__file__), '..\..\db-init\b_accounts_logic_objects.sql'),
        os.path.join(os.path.dirname(__file__), '..\..\db-init\b_hotel_rooms_logic_objects.sql'),
        os.path.join(os.path.dirname(__file__), '..\..\db-init\b_reservation_logic_objects.sql'),
        os.path.join(os.path.dirname(__file__), '..\..\db-init\c_finance&payment_logic_objects.sql'),
    ]
    
    # Iterate over each file path
    for file_path in file_paths:
        # Read the content of the SQL file
        with open(file_path, 'r') as file:
            sql_content = file.read()

        # Execute the SQL content
        schema_editor.execute(sql_content)

def reverse_sql(apps, schema_editor):
    # Add commands to revert the migration, like dropping procedures
    procedures_to_drop = [
        "DROP PROCEDURE IF EXISTS my_procedure;",
        "DROP PROCEDURE IF EXISTS another_procedure;",
        "DROP PROCEDURE IF EXISTS yet_another_procedure;",
    ]

class Migration(migrations.Migration):

    dependencies = [
        ('hotel_management', '0003_commodity_hotel_alter_roomtype_table_room_and_more'),  # Substitua pelos valores corretos
    ]

    operations = [
        migrations.RunPython(load_sql_from_file, reverse_sql),
    ]
