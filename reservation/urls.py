from django.urls import path
from . import views

urlpatterns = [
    path('', views.my_reservations, name='my_reservations'),
    path('reservation/<int:room_id>/', views.reservation_page, name='reservation_page'),
     path('confirm-reservation/', views.confirm_reservation, name='confirm_reservation'),
]
