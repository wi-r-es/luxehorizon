from django.urls import path
from . import views

urlpatterns = [
    path('', views.my_reservations, name='my_reservations'),
]
