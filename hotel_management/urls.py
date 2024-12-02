from django.urls import path
from . import views

urlpatterns = [
    path('', views.hotel_list, name='hotel_list'),
    path('hotel/add/', views.hotel_form, name='hotel_add'),
    path('hotel/edit/<int:hotel_id>/', views.hotel_form, name='hotel_edit'),
    path('hotel/delete/<int:hotel_id>/', views.delete_hotel, name='delete_hotel'),
    path('rooms/<int:hotel_id>/', views.room_list, name='room_list'),
]