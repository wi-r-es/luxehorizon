# users/management/commands/init_db.py
from django.core.management.base import BaseCommand
from django.db import connection
from users.models import AccPermission

class Command(BaseCommand):
    help = 'Initialize database with required data'

    def handle(self, *args, **options):
        self.stdout.write('Initializing database...')
        
        try:
            # Create initial permissions
            permissions_data = [
                {'perm_description': 'Administrator', 'perm_level': 1},
                {'perm_description': 'Manager', 'perm_level': 2},
                {'perm_description': 'Employee', 'perm_level': 3},
                {'perm_description': 'None', 'perm_level': 444},
            ]

            created_perms = []
            for perm_data in permissions_data:
                perm, created = AccPermission.objects.get_or_create(
                    perm_level=perm_data['perm_level'],
                    defaults={'perm_description': perm_data['perm_description']}
                )
                if created:
                    created_perms.append(perm_data['perm_description'])

            if created_perms:
                self.stdout.write(
                    self.style.SUCCESS(f'Created permissions: {", ".join(created_perms)}')
                )
            else:
                self.stdout.write('Permissions already exist')


            self.stdout.write(self.style.SUCCESS('Database initialization completed successfully'))

        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'Error initializing database: {str(e)}')
            )