# urls.py
from django.urls import path
from .views import CustomLoginView, register, CustomLogoutView, profile_view, update_profile

urlpatterns = [
    path('login/', CustomLoginView.as_view(), name='login'),
    path('register/', register, name='register'),
    path('logout/', CustomLogoutView.as_view(), name='logout'),
    path('profile/', profile_view, name='profile'),
    path('profile/edit/', update_profile, name='update_profile')
]
