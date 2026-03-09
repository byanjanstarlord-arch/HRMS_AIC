"""
Leaves Forms - Leave application forms
"""

from django import forms
from django.core.exceptions import ValidationError
from datetime import date

from .models import LeaveRequest
from .holiday_calendar import get_chargeable_leave_days


class LeaveApplicationForm(forms.ModelForm):
    """
    Form for employees to apply for leave
    """
    
    leave_type = forms.ChoiceField(
        choices=LeaveRequest.LEAVE_TYPE_CHOICES,
        widget=forms.Select(attrs={
            'class': 'form-select',
        }),
        help_text='Select the type of leave you want to apply for'
    )
    
    start_date = forms.DateField(
        widget=forms.DateInput(attrs={
            'class': 'form-input',
            'type': 'date',
            'min': date.today().isoformat(),
        }),
        help_text='Select the start date of your leave'
    )
    
    end_date = forms.DateField(
        widget=forms.DateInput(attrs={
            'class': 'form-input',
            'type': 'date',
            'min': date.today().isoformat(),
        }),
        help_text='Select the end date of your leave'
    )
    
    reason = forms.CharField(
        widget=forms.Textarea(attrs={
            'class': 'form-textarea',
            'rows': 4,
            'placeholder': 'Please provide a detailed reason for your leave request...'
        }),
        help_text='Provide a clear reason for your leave'
    )
    
    class Meta:
        model = LeaveRequest
        fields = ['leave_type', 'start_date', 'end_date', 'reason']

    def __init__(self, *args, user=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.user = user
    
    def clean(self):
        """Validate form data"""
        cleaned_data = super().clean()
        start_date = cleaned_data.get('start_date')
        end_date = cleaned_data.get('end_date')
        leave_type = cleaned_data.get('leave_type')
        
        if start_date and end_date:
            # Check if start date is not in the past
            if start_date < date.today():
                raise ValidationError({'start_date': 'Start date cannot be in the past.'})
            
            # Check if end date is after start date
            if end_date < start_date:
                raise ValidationError({'end_date': 'End date must be after or equal to start date.'})

        # Check available balance for limited leave types
        if start_date and end_date and leave_type and self.user:
            days = get_chargeable_leave_days(start_date, end_date, leave_type)

            if leave_type == 'casual' and days == 0:
                raise ValidationError({
                    'leave_type': 'Selected dates fall only on configured holidays. Casual leave is not required for these days.'
                })

            if leave_type in ['casual', 'earned', 'medical']:
                balance = self.user.get_leave_balance(leave_type)
                if days > balance:
                    raise ValidationError({'leave_type': f'You cannot apply for {days} day(s). You only have {balance} day(s) left for this leave type.'})
        
        return cleaned_data
    
    def save(self, user=None, commit=True):
        """Save the leave request with the user"""
        leave_request = super().save(commit=False)
        if user:
            leave_request.user = user
        elif self.user:
            leave_request.user = self.user
        leave_request.status = 'pending'

        if commit:
            leave_request.save()
        return leave_request


class LeaveActionForm(forms.Form):
    """
    Form for admin to approve/reject leave requests
    """
    
    action = forms.ChoiceField(
        choices=[
            ('approve', 'Approve'),
            ('reject', 'Reject'),
        ],
        widget=forms.RadioSelect,
        help_text='Select the action to take'
    )
    
    remarks = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={
            'class': 'form-textarea',
            'rows': 3,
            'placeholder': 'Optional remarks...'
        }),
        help_text='Optional remarks for the employee'
    )
