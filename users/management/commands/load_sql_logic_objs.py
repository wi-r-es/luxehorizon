from django.core.management.base import BaseCommand
from django.db import connection
from pathlib import Path
import os

def clean_sql_content(sql_content):
    # Remove ASCII art comments
    lines = sql_content.split('\n')
    cleaned_lines = []
    skip_ascii = False
    
    for line in lines:
        # Skip ASCII art comment blocks
        if '/*' in line and '██' in line:
            skip_ascii = True
            continue
        if skip_ascii and '*/' in line:
            skip_ascii = False
            continue
        if not skip_ascii:
            cleaned_lines.append(line)
    
    return '\n'.join(cleaned_lines)

class Command(BaseCommand):
    def handle(self, *args, **options):

        # Get the path to the SQL files directory (next to management commands)
        base_dir = Path(__file__).resolve().parent.parent.parent.parent
        self.stdout.write(self.style.SUCCESS(f'BASE DIR {base_dir}'))
        sql_dir = base_dir / 'db-init'
        sql_dir.mkdir(exist_ok=True)
        
        with connection.cursor() as cursor:
            for sql_file in sorted(sql_dir.glob('*.sql')):
                try:
                    sql_content = sql_file.read_text()
                    cleaned_sql = clean_sql_content(sql_content)
                    
                    # Split and execute statements
                    in_function = False
                    current_statement = []
                    statements = []
                    
                    for line in cleaned_sql.split('\n'):
                        if any(s in line for s in ['CREATE OR REPLACE FUNCTION', 'CREATE FUNCTION', 'CREATE OR REPLACE PROCEDURE']):
                            in_function = True
                        
                        current_statement.append(line)
                        
                        if ';' in line and not in_function:
                            statements.append('\n'.join(current_statement))
                            current_statement = []
                        elif 'LANGUAGE' in line and ';' in line and in_function:
                            in_function = False
                            statements.append('\n'.join(current_statement))
                            current_statement = []
                    
                    for statement in statements:
                        if statement.strip():
                            cursor.execute(statement)
                    
                except Exception as e:
                    self.stdout.write(self.style.ERROR(f'Error processing {sql_file.name}: {str(e)}'))
                    raise e

    