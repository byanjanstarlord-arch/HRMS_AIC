"""
Leaves Admin - Django Admin configuration for LeaveRequest model
"""

from django.contrib import admin
from .models import LeaveRequest


@admin.register(LeaveRequest)
class LeaveRequestAdmin(admin.ModelAdmin):
    """
    Leave Request Admin configuration
    """
    
    # Fields to display in the list view
    list_display = [
        'id', 'user', 'leave_type', 'start_date', 'end_date', 
        'status', 'created_at', 'action_date'
    ]
    
    # Filters for the list view
    list_filter = ['status', 'leave_type', 'created_at', 'start_date']
    
    # Fields to search
    search_fields = ['user__username', 'user__full_name', 'reason', 'admin_remarks']
    
    # Ordering of records
    ordering = ['-created_at']
    
    # Read-only fields
    readonly_fields = ['created_at', 'updated_at', 'action_date']
    
    # Fieldsets for the detail view
    fieldsets = (
        ('Leave Details', {
            'fields': ('user', 'leave_type', 'start_date', 'end_date', 'reason')
        }),
        ('Status', {
            'fields': ('status', 'approved_by', 'admin_remarks', 'action_date')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def get_queryset(self, request):
        """Customize queryset"""
        return super().get_queryset(request).select_related('user', 'approved_by')
