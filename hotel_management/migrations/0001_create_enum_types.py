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
                        'POOL',
                        'MOUNTAIN',
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

                IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'room_capacity_type') THEN
                    CREATE TYPE room_capacity_type AS ENUM (
                        'SINGLE',
                        'DOUBLE',
                        'TRIPLE',
                        'QUAD',
                        'KING',
                        'FAMILY',
                        'PENTHOUSE'
                    );
                END IF;
            END
            $$;
            """,
            # Reverse migration
            """
            DROP TYPE IF EXISTS room_quality_type;
            DROP TYPE IF EXISTS room_view_type;
            DROP TYPE IF EXISTS room_capacity_type;
            """
        ),
    ]
