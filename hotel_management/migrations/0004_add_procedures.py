from django.db import migrations
import os

def load_sql_from_file(apps, schema_editor):
    # Caminho para os ficheiros SQL
    base_path = os.path.join(os.path.dirname(__file__), '../../db-init/')
    file_names = [
        'd_dashboard_logic_objects.sql',
        # 'a_security_logic_objects.sql',
        'b_accounts_logic_objects.sql',
        'b_hotel_rooms_logic_objects.sql',
        'b_reservation_logic_objects.sql',
        'c_finance&payment_logic_objects.sql',
    ]
    file_paths = [os.path.join(base_path, name) for name in file_names]

    for file_path in file_paths:
        print(f"Carregando SQL de: {file_path}")
        if not os.path.exists(file_path):
            print(f"Arquivo não encontrado: {file_path}")
            continue
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                sql_content = file.read()
            schema_editor.execute(sql_content)
        except Exception as e:
            print(f"Erro ao carregar {file_path}: {str(e)}")


def reverse_sql(apps, schema_editor):
    pass

class Migration(migrations.Migration):

    dependencies = [
        ('hotel_management', '0003_commodity_hotel_alter_roomtype_table_room_and_more'),  # Substitua pelos valores corretos
    ]

    operations = [
        migrations.RunPython(load_sql_from_file, reverse_sql),
    ]