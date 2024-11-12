# urls.py
from django.urls import path
from .views import CustomLoginView, register, CustomLogoutView

urlpatterns = [
    path('login/', CustomLoginView.as_view(), name='login'),
    path('register/', register, name='register'),
    path('logout/', CustomLogoutView.as_view(), name='logout'),
]
