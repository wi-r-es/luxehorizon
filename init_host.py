import os
import django
from django.core.management import call_command
import psycopg2  # PostgreSQL database connector
from psycopg2 import sql
from decouple import config
import subprocess

# Set up Django environment
def setup_django():
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'luxehorizon.settings') 
    django.setup()

# Run Django management commands
def run_django_command(command, *args, **kwargs):
    try:
        call_command(command, *args, **kwargs)
        print(f"Successfully ran Django command: {command}")
    except Exception as e:
        print(f"Error running Django command {command}: {e}")

# Execute SQL script
def run_sql_script(sql_file):
    # Database configuration from settings.py or .env
    db_name = config('POSTGRES_DB', default='db_name')
    db_user = config('POSTGRES_USER', default='postgres')
    db_password = config('POSTGRES_PASSWORD', default='postgres')
    db_host = config('DB_HOST', default='localhost')
    db_port = config('DB_PORT', default='5432')
    
    try:
        # Connect to the PostgreSQL database
        connection = psycopg2.connect(
            dbname=db_name,
            user=db_user,
            password=db_password,
            host=db_host,
            port=db_port
        )
        cursor = connection.cursor()
        with open(sql_file, 'r') as f:
            sql_script = f.read()
        cursor.execute(sql.SQL(sql_script))
        connection.commit()
        print(f"Successfully executed SQL script: {sql_file}")
    except Exception as e:
        print(f"Error executing SQL script {sql_file}: {e}")
    finally:
        if cursor:
            cursor.close()
        if connection:
            connection.close()

# Start the Django development server
def start_django_server():
    try:
        subprocess.run(['python', 'manage.py', 'runserver'], check=True)
    except subprocess.CalledProcessError as e:
        print(f"Error starting the Django server: {e}")

# Main function
def main():
    setup_django()
    
    # Example Django commands
    run_django_command('makemigrations')
    run_django_command('migrate users')
    run_django_command('migrate')
    
    # Run SQL scripts
    # sql_scripts = ['script1.sql', 'script2.sql']  # List your SQL script file names here
    # for script in sql_scripts:
    #     run_sql_script(script)
    start_django_server()

if __name__ == '__main__':
    main()
