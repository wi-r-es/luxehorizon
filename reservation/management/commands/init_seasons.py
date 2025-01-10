from django.core.management.base import BaseCommand
from reservation.models import Season

class Command(BaseCommand):
    help = 'Initialize the database with default season data'

    def handle(self, *args, **options):
        self.stdout.write('Initializing database with seasons...')
        
        try:

            seasons_data = [
                {
                    'descriptive': Season.HIGH,
                    'begin_month': 6,
                    'begin_day': 1,
                    'end_month': 8,
                    'end_day': 31,
                    'rate': 150.00
                },
                {
                    'descriptive': Season.LOW,
                    'begin_month': 1,
                    'begin_day': 1,
                    'end_month': 3,
                    'end_day': 31,
                    'rate': 75.00
                },
                {
                    'descriptive': Season.FESTIVAL,
                    'begin_month': 12,
                    'begin_day': 20,
                    'end_month': 12,
                    'end_day': 31,
                    'rate': 200.00
                }
            ]

            created_seasons = []
            for season_data in seasons_data:
                # Use get_or_create to avoid duplicates
                season, created = Season.objects.get_or_create(
                    descriptive=season_data['descriptive'],
                    begin_month=season_data['begin_month'],
                    begin_day=season_data['begin_day'],
                    end_month=season_data['end_month'],
                    end_day=season_data['end_day'],
                    defaults={'rate': season_data['rate']}
                )
                if created:
                    created_seasons.append(
                        f"{season.get_descriptive_display()} ({season.begin_month}/{season.begin_day} to {season.end_month}/{season.end_day})"
                    )

            if created_seasons:
                self.stdout.write(
                    self.style.SUCCESS(f'Created seasons: {", ".join(created_seasons)}')
                )
            else:
                self.stdout.write('Seasons already exist')

            self.stdout.write(self.style.SUCCESS('Database initialization completed successfully'))

        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'Error initializing database: {str(e)}')
            )
