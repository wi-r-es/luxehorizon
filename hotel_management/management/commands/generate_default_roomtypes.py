from django.core.management.base import BaseCommand
from hotel_management.models import RoomType
from django.db import transaction
from itertools import product

class Command(BaseCommand):
    help = 'Generates default room types with all possible combinations'

    def add_arguments(self, parser):
        parser.add_argument(
            '--skip-existing',
            action='store_true',
            help='Skip creation if room type already exists'
        )

    def handle(self, *args, **options):
        # Define all possible values for each attribute
        room_configs = {
            'views': {
                'CITY': 'C',
                'OCEAN': 'O',
                'GARDEN': 'G',
                'POOL': 'P',
                'MOUNTAIN': 'M',
            },
            'qualities': {
                'STANDARD': 'S',
                'DELUXE': 'D',
                'PREMIUM': 'P',
            },
            'capacity': {
                'SINGLE': 'S',
                'DOUBLE': 'D',
                'TRIPLE': 'T',
                'QUAD': 'Q',
                'KING': 'K',
                'FAMILY': 'F',
                'PENTHOUSE': 'P',
            },
        }

        try:
            with transaction.atomic():
                created_count = 0
                skipped_count = 0

                # Generate all possible combinations
                for view, quality, capacity in product(room_configs['views'].items(), room_configs['qualities'].items(), room_configs['capacity'].items()):
                    view_name, view_code = view
                    quality_name, quality_code = quality
                    capacity_name, capacity_code = capacity
                    
                    # Generate type initials (e.g., 'CS' for City Standard)
                    type_initials = f"{view_code}{quality_code}{capacity_code}"
                    
                    # Check if this type already exists
                    if options['skip_existing'] and RoomType.objects.filter(type_initials=type_initials).exists():
                        self.stdout.write(
                            self.style.WARNING(
                                f'Skipping existing room type: {type_initials} ({view_name} {quality_name} {capacity_name})'
                            )
                        )
                        skipped_count += 1
                        continue

                    # Create the room type
                    room_type = RoomType.objects.create(
                        type_initials=type_initials,
                        room_view=view_name,
                        room_quality=quality_name,
                        room_capacity=capacity_name
                    )
                    
                    self.stdout.write(
                        self.style.SUCCESS(
                            f'Created room type: {type_initials} ({view_name} {quality_name} {capacity_name})'
                        )
                    )
                    created_count += 1

                summary = f"""
                        Room Types Generation Summary:
                        ----------------------------
                        Created: {created_count}
                        Skipped: {skipped_count}
                        Total combinations: {created_count + skipped_count}
                        """
                self.stdout.write(self.style.SUCCESS(summary))

        except Exception as e:
            self.stdout.write(
                self.style.ERROR(
                    f'Error generating room types: {str(e)}'
                )
            )