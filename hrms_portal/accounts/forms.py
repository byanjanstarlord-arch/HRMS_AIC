"""
Accounts Forms - User registration and authentication forms
"""

from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.core.exceptions import ValidationError
from .models import User


class EmployeeRegistrationForm(UserCreationForm):
    """
    Employee registration form
    Collects all required information for employee signup
    """
    
    # Additional fields for employee registration
    full_name = forms.CharField(
        max_length=200,
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-input',
            'placeholder': 'Enter your full name',
            'autocomplete': 'name'
        }),
        help_text='Your full name as per company records'
    )
    
    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={
            'class': 'form-input',
            'placeholder': 'Enter your email address',
            'autocomplete': 'email'
        }),
        help_text='A valid email address'
    )
    
    employee_id = forms.CharField(
        max_length=50,
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-input',
            'placeholder': 'Enter your employee ID',
            'autocomplete': 'off'
        }),
        help_text='Your unique employee ID'
    )
    
    department = forms.CharField(
        max_length=100,
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-input',
            'placeholder': 'Enter your department',
            'autocomplete': 'organization'
        }),
        help_text='Your department (e.g., HR, IT, Finance)'
    )
    
    password1 = forms.CharField(
        label='Password',
        widget=forms.PasswordInput(attrs={
            'class': 'form-input',
            'placeholder': 'Create a password',
            'autocomplete': 'new-password'
        }),
        help_text='Password must be at least 8 characters'
    )
    
    password2 = forms.CharField(
        label='Confirm Password',
        widget=forms.PasswordInput(attrs={
            'class': 'form-input',
            'placeholder': 'Confirm your password',
            'autocomplete': 'new-password'
        }),
        help_text='Enter the same password as above'
    )
    
    class Meta:
        model = User
        fields = ['full_name', 'email', 'employee_id', 'department', 'password1', 'password2']
    
    def clean_email(self):
        """Validate email is unique"""
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise ValidationError('This email is already registered.')
        return email
    
    def clean_employee_id(self):
        """Validate employee_id is unique"""
        employee_id = self.cleaned_data.get('employee_id')
        if User.objects.filter(employee_id=employee_id).exists():
            raise ValidationError('This employee ID is already registered.')
        return employee_id
    
    def save(self, commit=True):
        """Save the user with employee role"""
        user = super().save(commit=False)
        user.role = 'employee'
        # Normalize email to lowercase
        email = self.cleaned_data['email'].lower().strip()
        user.username = email  # Use email as username
        user.email = email
        user.full_name = self.cleaned_data['full_name']
        user.employee_id = self.cleaned_data['employee_id']
        user.department = self.cleaned_data['department']
        
        if commit:
            user.save()
        return user


class LoginForm(AuthenticationForm):
    """
    Custom login form for both Admin and Employee
    """
    
    username = forms.EmailField(
        widget=forms.EmailInput(attrs={
            'class': 'form-input',
            'placeholder': 'Enter your email',
            'autocomplete': 'email'
        }),
        help_text='Your registered email address'
    )
    
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-input',
            'placeholder': 'Enter your password',
            'autocomplete': 'current-password'
        })
    )
    
    class Meta:
        model = User
        fields = ['username', 'password']
    
    def clean_username(self):
        """Normalize email to lowercase for consistent authentication"""
        username = self.cleaned_data.get('username')
        if username:
            username = username.lower().strip()
        return username


class UserProfileForm(forms.ModelForm):
    """
    Form for updating user profile information
    """
    
    class Meta:
        model = User
        fields = ['full_name', 'email', 'department']
        widgets = {
            'full_name': forms.TextInput(attrs={
                'class': 'form-input',
                'placeholder': 'Full Name'
            }),
            'email': forms.EmailInput(attrs={
                'class': 'form-input',
                'placeholder': 'Email Address',
                'readonly': 'readonly'
            }),
            'department': forms.TextInput(attrs={
                'class': 'form-input',
                'placeholder': 'Department'
            }),
        }
