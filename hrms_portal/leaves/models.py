"""
Leaves Models - Leave Request Management
"""

from django.db import models
from django.conf import settings
from django.utils import timezone


class LeaveRequest(models.Model):
    """
    Leave Request model
    Stores all leave applications with their status
    """
    
    # Leave type choices
    LEAVE_TYPE_CHOICES = [
        ('annual', 'Annual Leave'),
        ('sick', 'Sick Leave'),
        ('casual', 'Casual Leave'),
        ('maternity', 'Maternity Leave'),
        ('paternity', 'Paternity Leave'),
        ('bereavement', 'Bereavement Leave'),
        ('unpaid', 'Unpaid Leave'),
        ('other', 'Other'),
    ]
    
    # Status choices
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
    ]
    
    # Foreign key to user
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='leave_requests',
        help_text='Employee who requested the leave'
    )
    
    # Leave details
    leave_type = models.CharField(
        max_length=20,
        choices=LEAVE_TYPE_CHOICES,
        default='annual',
        help_text='Type of leave requested'
    )
    
    start_date = models.DateField(
        help_text='Start date of the leave'
    )
    
    end_date = models.DateField(
        help_text='End date of the leave'
    )
    
    reason = models.TextField(
        help_text='Reason for the leave request'
    )
    
    # Status tracking
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='pending',
        help_text='Current status of the leave request'
    )
    
    # Admin actions
    approved_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='approved_leaves',
        help_text='Admin who approved/rejected the request'
    )
    
    admin_remarks = models.TextField(
        blank=True,
        null=True,
        help_text='Admin remarks on the decision'
    )
    
    action_date = models.DateTimeField(
        null=True,
        blank=True,
        help_text='Date when the request was approved/rejected'
    )
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Leave Request'
        verbose_name_plural = 'Leave Requests'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['status']),
            models.Index(fields=['user', 'status']),
            models.Index(fields=['created_at']),
        ]
    
    def __str__(self):
        """String representation of leave request"""
        return f"{self.user.full_name or self.user.username} - {self.get_leave_type_display()} ({self.start_date} to {self.end_date})"
    
    def get_duration_days(self):
        """Calculate the duration of leave in days"""
        if self.start_date and self.end_date:
            delta = self.end_date - self.start_date
            return delta.days + 1  # Include both start and end dates
        return 0
    
    def is_pending(self):
        """Check if the request is pending"""
        return self.status == 'pending'
    
    def is_approved(self):
        """Check if the request is approved"""
        return self.status == 'approved'
    
    def is_rejected(self):
        """Check if the request is rejected"""
        return self.status == 'rejected'
    
    def approve(self, admin_user, remarks=None):
        """Approve the leave request"""
        self.status = 'approved'
        self.approved_by = admin_user
        self.admin_remarks = remarks
        self.action_date = timezone.now()
        self.save()
    
    def reject(self, admin_user, remarks=None):
        """Reject the leave request"""
        self.status = 'rejected'
        self.approved_by = admin_user
        self.admin_remarks = remarks
        self.action_date = timezone.now()
        self.save()
    
    def get_status_color(self):
        """Get CSS color class based on status"""
        color_map = {
            'pending': 'warning',
            'approved': 'success',
            'rejected': 'danger',
        }
        return color_map.get(self.status, 'secondary')
