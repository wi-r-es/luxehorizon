from django.urls import path
from . import views

urlpatterns = [
    path('', views.hotel_list, name='hotel_list'),
    path('hotel/add/', views.hotel_form, name='hotel_add'),
    path('hotel/edit/<int:hotel_id>/', views.hotel_form, name='hotel_edit'),
    path('hotel/delete/<int:hotel_id>/', views.delete_hotel, name='delete_hotel'),
    path('rooms/', views.all_room_list, name='all_room_list'),
    path('rooms/<int:hotel_id>/', views.room_list, name='room_list'),
    path('hotel/<int:hotel_id>/room/add/', views.create_room, name='create_room'),
    path('hotel/<int:hotel_id>/room/<int:room_id>/edit/', views.edit_room, name='room_edit'),
    path('hotel/<int:hotel_id>/room/<int:room_id>/delete/', views.delete_room, name='delete_room'),
    path('search/', views.search_results, name='search_results'),
    path('search/rooms/', views.search_rooms, name='search_rooms'),
    path('search/rooms/results/', views.filter_rooms_guests, name='filter_rooms_guests'),
    path('commodities/', views.commodity_list, name='commodities_list'),
    path('commodities/add/', views.commodity_form, name='commodities_add'),
    path('commodities/edit/<int:commodity_id>/', views.commodity_form, name='commodities_edit'),
    path('commodities/<int:commodity_id>/delete/', views.commodity_delete, name='commodities_delete'), 
    path('image/<str:file_id>/', views.serve_image, name='serve_image')
]