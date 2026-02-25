"""
Accounts Models - Custom User Model
Extends Django's AbstractUser to add role-based fields
"""

from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    """
    Custom User model with role-based authentication
    Supports both Admin and Employee roles
    """
    
    # Role choices
    ROLE_CHOICES = [
        ('admin', 'Admin'),
        ('employee', 'Employee'),
    ]
    
    # Additional fields
    role = models.CharField(
        max_length=20,
        choices=ROLE_CHOICES,
        default='employee',
        help_text='User role - Admin or Employee'
    )
    
    employee_id = models.CharField(
        max_length=50,
        unique=True,
        blank=True,
        null=True,
        help_text='Unique employee ID (required for employees)'
    )
    
    department = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        help_text='Employee department'
    )
    
    full_name = models.CharField(
        max_length=200,
        blank=True,
        null=True,
        help_text='Full name of the user'
    )
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'User'
        verbose_name_plural = 'Users'
        ordering = ['-created_at']
    
    def __str__(self):
        """String representation of the user"""
        if self.full_name:
            return f"{self.full_name} ({self.username})"
        return self.username
    
    def is_admin(self):
        """Check if user is an admin"""
        return self.role == 'admin'
    
    def is_employee(self):
        """Check if user is an employee"""
        return self.role == 'employee'
    
    def get_pending_leaves_count(self):
        """Get count of pending leave requests for this user"""
        if hasattr(self, 'leave_requests'):
            return self.leave_requests.filter(status='pending').count()
        return 0
    
    def get_total_leaves_count(self):
        """Get total leave requests for this user"""
        if hasattr(self, 'leave_requests'):
            return self.leave_requests.count()
        return 0
