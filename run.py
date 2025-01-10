import subprocess
import sys

def run_command(command):
    try:
        print(f"Running: {command}")
        result = subprocess.run(command, shell=True, check=True, text=True)
        if result.returncode == 0:
            print(f"Command '{command}' executed successfully.\n")
    except subprocess.CalledProcessError as e:
        print(f"Error: Command '{command}' failed with exit code {e.returncode}.")
        sys.exit(e.returncode)

def main():
    commands = [
        "python manage.py makemigrations",
        "python manage.py migrate users",
        "python manage.py migrate --noinput",
        "python manage.py collectstatic --noinput",
        "python manage.py generate_default_roomtypes",
        "python manage.py init_db",
        "python manage.py load_sql_logic_objs",
        "python manage.py init_seasons",
        "python manage.py init_payment_methods",
        "python manage.py runserver 127.0.0.1:8000"
    ]

    for command in commands:
        run_command(command)

if __name__ == "__main__":
    main()