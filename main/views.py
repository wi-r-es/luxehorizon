from django.shortcuts import render
from django.http import HttpResponse
from bson import ObjectId
from luxehorizon.db_mongo import db
import gridfs


def index(request):
    return render(request, 'index.html')

def serve_image(request, file_id):
    # Get the file object from MongoDB using GridFS
    fs = gridfs.GridFS(db)  # Make sure 'db' is your MongoDB connection
    file = fs.get(ObjectId(file_id))  # Get the file by its ObjectId

    # Set appropriate content type for images
    response = HttpResponse(file.read(), content_type="image/jpeg")  # Adjust content type if necessary
    return response
