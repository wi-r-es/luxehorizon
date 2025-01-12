from django.shortcuts import render, redirect
from main.mongo_utils import get_hotel_reviews, get_average_rating, insert_review, get_review_by_reservation_id, update_review, delete_review
from users.models import User
from hotel_management.models import Hotel
from .forms import ReviewForm
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from reservation.models import Reservation
from django.db import connection

def get_client_and_hotel_ids(reservation_id):
    query = """
    SELECT rr.client_id, rmr.hotel_id
    FROM "reserves.reservation" rr
    JOIN "reserves.room_reservation" rrr ON rrr.reservation_id = rr.id
    JOIN "room_management.room" rmr ON rmr.id = rrr.room_id
    WHERE rr.id = %s
    """
    
    with connection.cursor() as cursor:
        cursor.execute(query, [reservation_id])
        result = cursor.fetchone()
    
    return result

def hotel_reviews(request, hotel_id):
    hotel = Hotel.objects.get(id=hotel_id)

    reviews = get_hotel_reviews(hotel_id)
    if reviews is not None:
        for review in reviews:
            user_id = review['userId']
            
            try:
                user = User.objects.get(id=user_id)
                review['nome'] = user.first_name + ' ' + user.last_name
            except User.DoesNotExist:
                review['nome'] = None
        media = get_average_rating(hotel_id)
    else:
        reviews = []
        media = 0
            
    return render(request, 'lista-reviews.html', {'reviews': reviews,'hotel_nome': hotel.h_name, 'media': media})

@login_required
def add_edit_review(request, reservation_id):
    reviewdb = get_review_by_reservation_id(reservation_id)
    
    if request.method == 'POST':
        form = ReviewForm(request.POST)
        if form.is_valid():
            resultado = get_client_and_hotel_ids(11)
            client_id = resultado[0]
            hotel_id = resultado[1]
            review = form.cleaned_data['review']
            rating = int(form.cleaned_data['rating'])
            if reviewdb:
                result = update_review(reviewdb['_id'], rating, review)
            else:
                result = insert_review(client_id, hotel_id, reservation_id, rating,review)

            if result:
                return redirect('my_reservations')
            else:
                return HttpResponse("Error while saving the review.", status=500)

    else:
        form = ReviewForm(initial=reviewdb)

    return render(request, 'adicionar-review.html', {'form': form, 'reservation_id': reservation_id, 'review': reviewdb})

@login_required
def delete_review_be(id):
    result = delete_review(id)
    if result:
        return redirect('my_reservations')
    else:
        return HttpResponse("Error while deleting the review.", status=500)