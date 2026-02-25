"""
Leaves URLs - URL routing for leaves app
"""

from django.urls import path
from . import views

urlpatterns = [
    # Employee routes
    path('apply-leave/', views.apply_leave, name='apply_leave'),
    path('leave-status/', views.leave_status, name='leave_status'),
    path('leave/<int:leave_id>/', views.leave_detail, name='leave_detail'),
    
    # Admin routes
    path('leave-requests/', views.leave_requests, name='leave_requests'),
    path('leave/<int:leave_id>/approve/', views.approve_leave, name='approve_leave'),
    path('leave/<int:leave_id>/reject/', views.reject_leave, name='reject_leave'),
    
    # AJAX API endpoints
    path('api/leave-requests/', views.get_leave_requests_ajax, name='leave_requests_ajax'),
    path('api/check-new-requests/', views.check_new_requests, name='check_new_requests'),
]
