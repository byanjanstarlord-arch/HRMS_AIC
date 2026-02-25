"""
Accounts URLs - URL routing for accounts app
"""

from django.urls import path
from . import views

urlpatterns = [
    # Landing page
    path('', views.landing_page, name='landing_page'),
    
    # Authentication
    path('register/', views.employee_register, name='register'),
    path('login/', views.user_login, name='login'),
    path('logout/', views.user_logout, name='logout'),
    
    # Employee routes
    path('dashboard/', views.employee_dashboard, name='employee_dashboard'),
    path('about/', views.employee_about, name='employee_about'),
    
    # Admin routes
    path('admin-dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('admin-employees/', views.employees_list, name='employees_list'),
    
    # AJAX API endpoints
    path('api/user-stats/', views.get_user_stats, name='user_stats'),
]
