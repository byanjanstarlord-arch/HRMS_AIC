"""
Accounts Views - Authentication and user management views
"""

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_protect

from .models import User
from .forms import EmployeeRegistrationForm, LoginForm
from leaves.models import LeaveRequest
from .forms import TopUpLeavesForm


def landing_page(request):
    """
    Landing page view
    Displays the main entry point with login options
    """
    # If user is already logged in, redirect to appropriate dashboard
    if request.user.is_authenticated:
        if request.user.is_admin():
            return redirect('admin_dashboard')
        else:
            return redirect('employee_dashboard')
    
    return render(request, 'accounts/landing.html')


@require_http_methods(["GET", "POST"])
@csrf_protect
def employee_register(request):
    """
    Employee registration view
    Handles new employee signup
    """
    # Redirect if already logged in
    if request.user.is_authenticated:
        return redirect('employee_dashboard')
    
    if request.method == 'POST':
        form = EmployeeRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            # Log the user in after registration
            login(request, user)
            messages.success(request, f'Welcome {user.full_name}! Your account has been created successfully.')
            return redirect('employee_dashboard')
        else:
            # Display form errors
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f"{field.replace('_', ' ').title()}: {error}")
    else:
        form = EmployeeRegistrationForm()
    
    return render(request, 'accounts/register.html', {'form': form})


@require_http_methods(["GET", "POST"])
@csrf_protect
def user_login(request):
    """
    User login view
    Handles both Admin and Employee login
    """
    # Redirect if already logged in
    if request.user.is_authenticated:
        if request.user.is_admin():
            return redirect('admin_dashboard')
        else:
            return redirect('employee_dashboard')
    
    if request.method == 'POST':
        form = LoginForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            messages.success(request, f'Welcome back, {user.full_name or user.username}!')
            
            # Redirect based on role
            if user.is_admin():
                return redirect('admin_dashboard')
            else:
                return redirect('employee_dashboard')
        else:
            messages.error(request, 'Invalid email or password. Please try again.')
    else:
        form = LoginForm()
    
    return render(request, 'accounts/login.html', {'form': form})


@login_required
def user_logout(request):
    """
    User logout view
    Logs out the current user and redirects to landing page
    """
    logout(request)
    messages.success(request, 'You have been logged out successfully.')
    return redirect('landing_page')


# ==================== EMPLOYEE VIEWS ====================

@login_required
def employee_dashboard(request):
    """
    Employee Dashboard view
    Displays employee's leave statistics and recent activity
    """
    # Check if user is an employee
    if not request.user.is_employee():
        messages.error(request, 'Access denied. This page is for employees only.')
        return redirect('admin_dashboard')
    
    # Get leave statistics
    total_leaves = LeaveRequest.objects.filter(user=request.user).count()
    pending_leaves = LeaveRequest.objects.filter(user=request.user, status='pending').count()
    approved_leaves = LeaveRequest.objects.filter(user=request.user, status='approved').count()
    rejected_leaves = LeaveRequest.objects.filter(user=request.user, status='rejected').count()
    
    # Get recent leave requests (last 5)
    recent_leaves = LeaveRequest.objects.filter(user=request.user).order_by('-created_at')[:5]
    
    context = {
        'total_leaves': total_leaves,
        'pending_leaves': pending_leaves,
        'approved_leaves': approved_leaves,
        'rejected_leaves': rejected_leaves,
        'recent_leaves': recent_leaves,
    }
    
    return render(request, 'accounts/employee_dashboard.html', context)


@login_required
def employee_about(request):
    """
    Employee About/Profile view
    Displays employee's profile information
    """
    # Check if user is an employee
    if not request.user.is_employee():
        messages.error(request, 'Access denied.')
        return redirect('admin_dashboard')
    
    return render(request, 'accounts/employee_about.html', {'user': request.user})


# ==================== ADMIN VIEWS ====================

@login_required
def admin_dashboard(request):
    """
    Admin Dashboard view
    Displays admin overview with statistics
    """
    # Check if user is an admin
    if not request.user.is_admin():
        messages.error(request, 'Access denied. This page is for administrators only.')
        return redirect('employee_dashboard')
    
    # Get statistics
    total_employees = User.objects.filter(role='employee').count()
    total_leaves = LeaveRequest.objects.count()
    pending_requests = LeaveRequest.objects.filter(status='pending').count()
    approved_requests = LeaveRequest.objects.filter(status='approved').count()
    rejected_requests = LeaveRequest.objects.filter(status='rejected').count()
    
    # Get recent leave requests (last 10)
    recent_requests = LeaveRequest.objects.select_related('user').order_by('-created_at')[:10]
    
    context = {
        'total_employees': total_employees,
        'total_leaves': total_leaves,
        'pending_requests': pending_requests,
        'approved_requests': approved_requests,
        'rejected_requests': rejected_requests,
        'recent_requests': recent_requests,
    }
    
    return render(request, 'accounts/admin_dashboard.html', context)


@login_required
def employees_list(request):
    """
    Employees List view (Admin only)
    Displays all registered employees
    """
    # Check if user is an admin
    if not request.user.is_admin():
        messages.error(request, 'Access denied.')
        return redirect('employee_dashboard')
    
    employees = User.objects.filter(role='employee').order_by('-created_at')
    
    return render(request, 'accounts/employees_list.html', {'employees': employees})


@login_required
def top_up_leaves(request, user_id):
    """
    Admin view to top-up or set leave balances for an employee
    """
    # Check if user is an admin
    if not request.user.is_admin():
        messages.error(request, 'Access denied.')
        return redirect('employee_dashboard')

    employee = get_object_or_404(User, id=user_id, role='employee')

    if request.method == 'POST':
        form = TopUpLeavesForm(request.POST, instance=employee)
        if form.is_valid():
            form.save()
            messages.success(request, f'Leave balances updated for {employee.full_name or employee.username}.')
            return redirect('employees_list')
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, error)
    else:
        form = TopUpLeavesForm(instance=employee)

    return render(request, 'accounts/top_up_leaves.html', {'form': form, 'employee': employee})


# ==================== AJAX API VIEWS ====================

@login_required
def get_user_stats(request):
    """
    AJAX endpoint to get user statistics
    Used for real-time dashboard updates
    """
    if request.user.is_admin():
        data = {
            'total_employees': User.objects.filter(role='employee').count(),
            'total_leaves': LeaveRequest.objects.count(),
            'pending_requests': LeaveRequest.objects.filter(status='pending').count(),
            'approved_requests': LeaveRequest.objects.filter(status='approved').count(),
            'rejected_requests': LeaveRequest.objects.filter(status='rejected').count(),
        }
    else:
        data = {
            'total_leaves': LeaveRequest.objects.filter(user=request.user).count(),
            'pending_leaves': LeaveRequest.objects.filter(user=request.user, status='pending').count(),
            'approved_leaves': LeaveRequest.objects.filter(user=request.user, status='approved').count(),
            'rejected_leaves': LeaveRequest.objects.filter(user=request.user, status='rejected').count(),
        }
    
    return JsonResponse(data)
