#This file is under construction
# it is intended to start up the environment 
import os
import sys
import django
from django.core.management import call_command
import sqlite3  # Change this to your database connector, e.g., psycopg2 for PostgreSQL

# Set up Django environment
def setup_django():
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'your_project.settings')  # Replace 'your_project' with your Django project name
    django.setup()

# Run Django management commands
def run_django_command(command, *args, **kwargs):
    try:
        call_command(command, *args, **kwargs)
        print(f"Successfully ran Django command: {command}")
    except Exception as e:
        print(f"Error running Django command {command}: {e}")

# Execute SQL script
def run_sql_script(sql_file, database='db.sqlite3'):  # Change the default database if needed
    try:
        with sqlite3.connect(database) as conn:  # Change to a different connector for non-SQLite databases
            cursor = conn.cursor()
            with open(sql_file, 'r') as f:
                sql_script = f.read()
            cursor.executescript(sql_script)
            conn.commit()
            print(f"Successfully executed SQL script: {sql_file}")
    except Exception as e:
        print(f"Error executing SQL script {sql_file}: {e}")

# Main function
def main():
    setup_django()
    
    # Example Django commands
    run_django_command('makemigrations')
    run_django_command('migrate')
    
    # Run SQL scripts
    sql_scripts = ['script1.sql', 'script2.sql']  # List your SQL script file names here
    for script in sql_scripts:
        run_sql_script(script)

if __name__ == '__main__':
    main()