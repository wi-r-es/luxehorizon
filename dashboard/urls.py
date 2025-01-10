from django.urls import path
from . import views

urlpatterns = [
    path('', views.AdminEmployeeDashboardView.as_view(), name='admin_dashboard'),
    path('employee/', views.employee_dashboard, name='employee_dash'),
]
