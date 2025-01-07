from django.urls import path
from . import views

urlpatterns = [
    path('', views.my_reservations, name='my_reservations'),
    path('reservation/<int:room_id>/', views.reservation_page, name='reservation_page'),
    path('confirm_reservation/', views.confirm_reservation, name='confirm_reservation'),
    path('cancel_reservation/', views.cancel_reservation, name='cancel_reservation'),
    path('seasons/', views.season_list, name='seasons_list'),
    path('seasons/add/', views.season_form, name='seasons_add'),
    path('seasons/edit/<int:season_id>/', views.season_form, name='seasons_edit')
]
