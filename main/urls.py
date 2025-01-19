from django.urls import path
from . import views

app_name = 'main'

urlpatterns = [
    path('', views.index, name='index'),
    path('image/<str:file_id>/', views.serve_image, name='serve_image')
]
