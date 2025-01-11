from pymongo import MongoClient
from django.conf import settings

client = MongoClient(settings.MONGO_DB_URI)
db = client['luxehorizon']
