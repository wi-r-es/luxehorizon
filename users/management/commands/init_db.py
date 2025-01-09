# users/management/commands/init_db.py
from django.core.management.base import BaseCommand
from django.db import connection
from users.models import Employee, Client, AccPermission

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

            # Add any additional initialization here
            # For example, create an admin employee if needed:
            """
            if not Employee.objects.filter(email='admin@example.com').exists():
                admin_employee = Employee.objects.create(
                    email='admin@example.com',
                    first_name='Admin',
                    last_name='User',
                    role=AccPermission.objects.get(perm_level=1),
                    social_security=12345678,
                    nif='123456789',
                    phone='123456789',
                    full_address='Admin Street 1',
                    postal_code='12345',
                    city='Admin City'
                )
                admin_employee.set_password('admin123')
                admin_employee.save()
                self.stdout.write(self.style.SUCCESS('Created admin employee'))
            """

            self.stdout.write(self.style.SUCCESS('Database initialization completed successfully'))

        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'Error initializing database: {str(e)}')
            )