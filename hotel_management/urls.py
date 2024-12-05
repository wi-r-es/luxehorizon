from django.urls import path
from . import views

urlpatterns = [
    path('', views.hotel_list, name='hotel_list'),
    path('hotel/add/', views.hotel_form, name='hotel_add'),
    path('hotel/edit/<int:hotel_id>/', views.hotel_form, name='hotel_edit'),
    path('hotel/delete/<int:hotel_id>/', views.delete_hotel, name='delete_hotel'),
    path('rooms/<int:hotel_id>/', views.room_list, name='room_list'),
    path('hotel/<int:hotel_id>/room/add/', views.create_room, name='create_room'),
    path('hotel/<int:hotel_id>/room/<int:room_id>/edit/', views.edit_room, name='room_edit'),
    path('hotel/<int:hotel_id>/room/<int:room_id>/delete/', views.delete_room, name='delete_room'),
]