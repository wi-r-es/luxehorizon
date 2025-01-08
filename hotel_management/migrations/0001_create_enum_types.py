from django.db import migrations

class Migration(migrations.Migration):
    initial = True

    dependencies = [
    ]
#-- P - Piscina, M - Mar, S - Serra, N - Nenhuma       #
# -- B - Baixa, S - Superior
    operations = [
        migrations.RunSQL(
            # Forward migration
            """
            DO $$
            BEGIN
                IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'room_view_type') THEN
                    CREATE TYPE room_view_type AS ENUM (
                        'CITY',
                        'OCEAN',
                        'GARDEN',
                        'NONE'
                    );
                END IF;

                IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'room_quality_type') THEN
                    CREATE TYPE room_quality_type AS ENUM (
                        'STANDARD',
                        'DELUXE',
                        'PREMIUM'
                    );
                END IF;
            END
            $$;
            """,
            # Reverse migration
            """
            DROP TYPE IF EXISTS room_quality_type;
            DROP TYPE IF EXISTS room_view_type;
            """
        ),
    ]
