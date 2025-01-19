from datetime import datetime
from luxehorizon.db_mongo import db
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django.conf import settings
import gridfs

# Insere uma review na vase de dados
def insert_review(user_id, hotel_id, reservation_id, rating, review_text):
    collection = db['reviews']

    review_document = {
        "userId": user_id,
        "hotelId": hotel_id,
        "reservationId": reservation_id,
        "date": datetime.utcnow(),
        "rating": rating,
        "review": review_text
    }

    result = collection.insert_one(review_document)

    return result.inserted_id

def get_review_by_reservation_id(reservation_id):
    collection = db['reviews']
    review = collection.find_one({"reservationId": reservation_id})
    return review

# Atualiza uma review na base de dados
def update_review(review_id, rating, review_text):
    collection = db['reviews']
    review = collection.find_one({"_id": review_id})

    if review is None:
        return False
    
    review['rating'] = rating
    review['review'] = review_text

    result = collection.update_one({"_id": review_id}, {"$set": review})
    
    return result.modified_count > 0

# Apaga uma review da base de dados
def delete_review(review_id):
    collection = db['reviews']
    result = collection.delete_one({"_id": review_id})
    
    return result.deleted_count > 0

# retorna as reviews de um determinado hotel
def get_hotel_reviews(hotel_id):
    collection = db['reviews']
    reviews = list(collection.find({"hotelId": hotel_id}))
    return reviews

# devolve a review feita por um utilizador a uma reserva
def get_reservation_review(reservation_id):
    collection = db['reviews']
    review = collection.find_one({"reservationId": reservation_id})
    return review

# calcula a média de reviews de um hotel
def get_average_rating(hotel_id):
    collection = db['reviews']
    
    pipeline = [
        {"$match": {"hotelId": hotel_id}},  
        {"$addFields": {
            "rating": {"$toDouble": "$rating"} 
        }},
        {"$group": {
            "_id": "$hotelId",
            "average_rating": {"$avg": "$rating"}  
        }}
    ]
    
    result = list(collection.aggregate(pipeline))
    
    if result:
        return result[0].get('average_rating', 0)
    else:
        return 0
    
# retorna o número de reviews de um hotel
def get_number_of_reviews(hotel_id):
    collection = db['reviews']
    
    pipeline = [
        {"$match": {"hotelId": hotel_id}},  
        {"$count": "number_of_reviews"}
    ]
    
    result = list(collection.aggregate(pipeline))
    
    if result:
        return result[0].get('number_of_reviews', 0)
    else:
        return 0
    
def upload_file_with_metadata(file, filename, postgres_id):
    #collection = db['ficheiros']
    fs = gridfs.GridFS(db)
    metadata = {
        "postgres_id": postgres_id
    }
    file_id = fs.put(file, filename=filename, metadata=metadata)
    return file_id

def get_files_by_postgres_id(postgres_id):
    fs = gridfs.GridFS(db)  # Initialize GridFS
    files = []
    try:
        # Query GridFS for files matching the given Postgres ID in metadata
        for grid_out in fs.find({"metadata.postgres_id": postgres_id}):
            files.append(grid_out)
    except Exception as e:
        print(f"Error retrieving files for Postgres ID {postgres_id}: {e}")
    return files