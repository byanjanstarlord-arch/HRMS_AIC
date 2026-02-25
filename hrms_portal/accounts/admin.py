"""
Accounts Admin - Django Admin configuration for User model
"""

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    """
    Custom User Admin configuration
    Extends Django's default UserAdmin to include custom fields
    """
    
    # Fields to display in the list view
    list_display = [
        'username', 'full_name', 'email', 'role', 'employee_id', 
        'department', 'is_active', 'created_at'
    ]
    
    # Filters for the list view
    list_filter = ['role', 'is_active', 'department', 'created_at']
    
    # Fields to search
    search_fields = ['username', 'full_name', 'email', 'employee_id', 'department']
    
    # Ordering of records
    ordering = ['-created_at']
    
    # Fieldsets for the detail view
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        ('Personal Info', {'fields': ('full_name', 'email', 'employee_id', 'department')}),
        ('Permissions', {'fields': ('role', 'is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('Important Dates', {'fields': ('last_login', 'date_joined', 'created_at', 'updated_at')}),
    )
    
    # Read-only fields
    readonly_fields = ['created_at', 'updated_at', 'last_login', 'date_joined']
    
    # Fieldsets for adding a new user
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'email', 'full_name', 'role', 'employee_id', 'department', 'password1', 'password2'),
        }),
    )
    
    def get_queryset(self, request):
        """Customize queryset if needed"""
        return super().get_queryset(request)
