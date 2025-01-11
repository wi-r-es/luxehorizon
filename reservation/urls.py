from django.urls import path
from . import views

urlpatterns = [
    path('', views.my_reservations, name='my_reservations'),
    path('list_reservations/', views.all_reservations, name='list_reservations_employee'),
    path('list_reservations/<int:reservation_id>/', views.reservation_details, name='reservation_details'),
    path('list_reservations/check_in/<int:reservation_id>', views.check_in, name='check_in'),
    path('list_reservations/check_out/<int:reservation_id>', views.check_out, name='check_out'),
    path('list_reservations/payment/', views.payment, name='payment'),
    path('reservation/<int:room_id>/', views.reservation_page, name='reservation_page'),
    path('confirm_reservation/', views.confirm_reservation, name='confirm_reservation'),
    path('cancel_reservation/', views.cancel_reservation, name='cancel_reservation'),
    path('seasons/', views.season_list, name='seasons_list'),
    path('seasons/add/', views.season_form, name='seasons_add'),
    path('seasons/edit/<int:season_id>/', views.season_form, name='seasons_edit'),
]
