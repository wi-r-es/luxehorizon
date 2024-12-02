# urls.py
from django.urls import path
from . import views
from .views import CustomLoginView, register, CustomLogoutView, profile_view, update_profile

urlpatterns = [
     path('', views.users_list, name='users_list'),
    path('user/add/', views.user_form, name='user_add'),
    path('user/edit/<int:hotel_id>/', views.user_form, name='user_edit'),
    path('user/delete/<int:hotel_id>/', views.delete_user, name='delete_user'),
    path('login/', CustomLoginView.as_view(), name='login'),
    path('register/', register, name='register'),
    path('logout/', CustomLogoutView.as_view(), name='logout'),
    path('profile/', profile_view, name='profile'),
    path('profile/edit/', update_profile, name='update_profile')
]
