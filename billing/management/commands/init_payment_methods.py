from django.core.management.base import BaseCommand
from billing.models import PaymentMethod

class Command(BaseCommand):
    help = 'Initialize the PaymentMethod model with base payment methods'

    def handle(self, *args, **kwargs):
        payment_methods = [
            {'descriptive': 'Credit Card'},
            {'descriptive': 'Debit Card'},
            {'descriptive': 'PayPal'},
            {'descriptive': 'Bank Transfer'},
            {'descriptive': 'Cash'},
            {'descriptive': 'Bitcoin'}
        ]

        created_methods = []
        for method in payment_methods:
            obj, created = PaymentMethod.objects.get_or_create(
                descriptive=method['descriptive']
            )
            if created:
                created_methods.append(method['descriptive'])

        if created_methods:
            self.stdout.write(
                self.style.SUCCESS(f'Successfully added: {", ".join(created_methods)}')
            )
        else:
            self.stdout.write('No new payment methods added (already exist).')
