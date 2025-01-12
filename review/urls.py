from django.urls import path
from . import views

app_name = 'review'

urlpatterns = [
    path('/hotel/<int:hotel_id>', views.hotel_reviews, name='hotel_reviews'),
    path("/reservation/<int:reservation_id>", views.add_edit_review, name='reservation_review'),
    path("/reservation/<int:id>/delete", views.delete_review_be, name='delete_review'),
]