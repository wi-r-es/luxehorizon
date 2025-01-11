from pymongo import MongoClient
from django.conf import settings

def initialize_mongo_db():
    # Connect to MongoDB
    client = MongoClient(settings.MONGO_DB_URI)
    db = client[settings.MONGO_DB_NAME]

    # Check and create collections if they don't exist
    required_collections = ["reviews"]  
    existing_collections = db.list_collection_names()

    for collection in required_collections:
        if collection not in existing_collections:
            db.create_collection(collection)
            print(f"Collection '{collection}' created.")

    print(f"MongoDB database '{settings.MONGO_DB_NAME}' is initialized.")
    client.close()
