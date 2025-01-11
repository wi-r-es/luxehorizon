from django.apps import AppConfig
from .mongo_init import initialize_mongo_db


class MainConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'main'

    def ready(self):
        initialize_mongo_db()