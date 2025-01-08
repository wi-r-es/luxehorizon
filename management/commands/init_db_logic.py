from django.core.management.base import BaseCommand
from django.db import connection
from pathlib import Path

class Command(BaseCommand):
    help = 'Initialize database logic after migrations'

    def handle(self, *args, **options):
        try:
            # Path to your SQL files
            sql_dir = Path('/app/init-scripts')
            
            # Get all .sql files except schema creation
            sql_files = sorted([f for f in sql_dir.glob('*.sql')])
            
            with connection.cursor() as cursor:
                for sql_file in sql_files:
                    if sql_file.name.startswith('logic_'):
                        self.stdout.write(f'Executing {sql_file.name}...')
                        sql = sql_file.read_text()
                        cursor.execute(sql)
                        self.stdout.write(self.style.SUCCESS(f'Successfully executed {sql_file.name}'))

        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'Error initializing database logic: {str(e)}')
            )
