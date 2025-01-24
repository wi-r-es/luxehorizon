from django.shortcuts import render
from django.http import HttpResponse
from bson import ObjectId
from luxehorizon.db_mongo import db
import gridfs
from django.db.models import Min
from hotel_management.models import Hotel
from main.mongo_utils import get_number_of_reviews, get_files_by_postgres_id, upload_file_with_metadata, get_cover_image

def index(request):
    # Busca os 3 hotéis com as maiores avaliações (número de estrelas)
    top_hotels = (
        Hotel.objects.annotate(min_price=Min('room__base_price'))  # Calcula o menor preço dos quartos
        .order_by('-stars')[:3]  # Ordena por estrelas em ordem decrescente e limita a 3 resultados
    )

    for hotel in top_hotels:
        num_rev = get_number_of_reviews(hotel.id)
        file = get_cover_image(hotel.id)

        if file is not None:
            # Converte o ID do arquivo em uma string
            file.id_str = str(file._id)
            hotel.cover_picture = file
        else:
            hotel.cover_picture = None
        hotel.num_reviews = num_rev

    return render(request, 'index.html', {
        'top_hotels': top_hotels,  # Passa os 3 melhores hotéis para o template
    })

def serve_image(request, file_id):
    # Get the file object from MongoDB using GridFS
    fs = gridfs.GridFS(db)  # Make sure 'db' is your MongoDB connection
    file = fs.get(ObjectId(file_id))  # Get the file by its ObjectId

    # Set appropriate content type for images
    response = HttpResponse(file.read(), content_type="image/jpeg")  # Adjust content type if necessary
    return response