# urls.py
from django.urls import path
from . import views
from .views import CustomLoginView, CustomLogoutView, profile_view, update_profile, login_required

urlpatterns = [
    path('', views.users_list, name='users_list'),
    path('user/add/', views.users_form, name='users_add'),
    path('user/edit/<int:user_id>/', views.users_form, name='users_edit'),
    path('user/delete/<int:user_id>/', views.delete_user, name='delete_user'),
    path('login/', CustomLoginView.as_view(), name='login'),
    path('change-password/', views.change_password, name='change_password'),
    path('register/', views.register_user, name='register'),
    path('logout/', CustomLogoutView.as_view(), name='logout'),
    path('profile/', profile_view, name='profile'),
    path('profile/edit/', update_profile, name='update_profile')
]
