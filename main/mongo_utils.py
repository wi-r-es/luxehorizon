from datetime import datetime
from luxehorizon.db_mongo import db

# Insere uma review na vase de dados
def insert_review(user_id, hotel_id, reservation_id, rating, review_text):
    collection = db['review']

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

# Atualiza uma review na base de dados
def update_review(review_id, rating, review_text):
    collection = db['review']
    review = collection.find_one({"_id": review_id})

    if review is None:
        return False
    
    review['rating'] = rating
    review['review'] = review_text

    result = collection.update_one({"_id": review_id}, {"$set": review})
    
    return result.modified_count > 0

# Apaga uma review da base de dados
def delete_review(review_id):
    collection = db['review']
    result = collection.delete_one({"_id": review_id})
    
    return result.deleted_count > 0

# retorna as reviews de um determinado hotel
def get_hotel_reviews(hotel_id):
    collection = db['review']
    reviews = collection.find({"hotelId": hotel_id})
    return reviews

# devolve a review feita por um utilizador a uma reserva
def get_reservation_review(reservation_id):
    collection = db['review']
    review = collection.find_one({"reservationId": reservation_id})
    return review

# calcula a média de reviews de um hotel
def get_average_rating(hotel_id):
    collection = db['review']
    reviews = collection.find({"hotelId": hotel_id})
    total_rating = 0
    count = 0
    for review in reviews:
        total_rating += review['rating']
        count += 1

    if count == 0:
        return 0

    return total_rating / count
