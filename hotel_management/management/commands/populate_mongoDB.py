import os
import random
from django.conf import settings
from django.core.management.base import BaseCommand
from hotel_management.models import Hotel
from main.mongo_utils import upload_file_init

def list_files_in_root_folder(folder_path):
    if os.path.exists(folder_path) and os.path.isdir(folder_path):
        files = [f for f in os.listdir(folder_path) if os.path.isfile(os.path.join(folder_path, f))]
        return files
    else:
        print(f"Folder {folder_path} does not exist or is not a directory.")
        return []

class Command(BaseCommand):
    help = 'Populate MongoDB with hotel data'

    def handle(self, *args, **options):
        folder_path = os.path.join(settings.BASE_DIR, 'stockPictures')
        hotels = Hotel.objects.all()
        files = list_files_in_root_folder(folder_path)

        if not files:
            print(f"No files found in the folder: {folder_path}")
            return

        for hotel in hotels:
            try:
                filename = random.choice(files)
                file_path = os.path.join(folder_path, filename)
                
                file_id = upload_file_init(file_path, filename, hotel.id)
                
                print(f"Uploaded {filename} to MongoDB with metadata {hotel.id}. File ID: {file_id}")
            except Exception as e:
                print(f"Error uploading file for hotel {hotel.id}: {e}")

        print("Finished uploading files to MongoDB.")
