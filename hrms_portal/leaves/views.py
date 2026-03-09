"""
Leaves Views - Leave management views
"""

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_protect
from django.core.paginator import Paginator
from django.utils import timezone

from .models import LeaveRequest
from .forms import LeaveApplicationForm
from .holiday_calendar import get_excluded_holiday_strings


# ==================== EMPLOYEE LEAVE VIEWS ====================

@login_required
@require_http_methods(["GET", "POST"])
@csrf_protect
def apply_leave(request):
    """
    Apply for leave view (Employee only)
    Handles leave application form submission
    """
    # Check if user is an employee
    if not request.user.is_employee():
        messages.error(request, 'Access denied. Only employees can apply for leave.')
        return redirect('admin_dashboard')
    
    if request.method == 'POST':
        form = LeaveApplicationForm(request.POST, user=request.user)
        if form.is_valid():
            leave_request = form.save(user=request.user)
            messages.success(
                request, 
                f'Your leave request has been submitted successfully! '
                f'Reference ID: #{leave_request.id}'
            )
            return redirect('leave_status')
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, error)
    else:
        form = LeaveApplicationForm(user=request.user)

    context = {
        'form': form,
        'casual_leaves': request.user.casual_leaves,
        'earned_leaves': request.user.earned_leaves,
        'medical_leaves': request.user.medical_leaves,
        'holiday_dates': get_excluded_holiday_strings(),
    }

    return render(request, 'leaves/apply_leave.html', context)


@login_required
def leave_status(request):
    """
    Leave Status view (Employee only)
    Displays all leave requests with their current status
    """
    # Check if user is an employee
    if not request.user.is_employee():
        messages.error(request, 'Access denied.')
        return redirect('admin_dashboard')
    
    # Get all leave requests for the current user
    leaves = LeaveRequest.objects.filter(user=request.user).order_by('-created_at')
    
    # Pagination
    paginator = Paginator(leaves, 10)  # 10 leaves per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
        'total_leaves': leaves.count(),
        'pending_count': leaves.filter(status='pending').count(),
        'approved_count': leaves.filter(status='approved').count(),
        'rejected_count': leaves.filter(status='rejected').count(),
    }
    
    return render(request, 'leaves/leave_status.html', context)


@login_required
def leave_detail(request, leave_id):
    """
    Leave Detail view
    Shows detailed information about a specific leave request
    """
    leave = get_object_or_404(LeaveRequest, id=leave_id)
    
    # Check permissions
    if request.user.is_employee() and leave.user != request.user:
        messages.error(request, 'Access denied. You can only view your own leave requests.')
        return redirect('leave_status')
    
    return render(request, 'leaves/leave_detail.html', {'leave': leave})


# ==================== ADMIN LEAVE VIEWS ====================

@login_required
def leave_requests(request):
    """
    Leave Requests view (Admin only)
    Displays all leave requests with approval actions
    """
    # Check if user is an admin
    if not request.user.is_admin():
        messages.error(request, 'Access denied. Only administrators can view all leave requests.')
        return redirect('employee_dashboard')
    
    # Get filter parameters
    status_filter = request.GET.get('status', 'all')
    
    # Get all leave requests
    leaves = LeaveRequest.objects.select_related('user').all().order_by('-created_at')
    
    # Apply filters
    if status_filter == 'pending':
        leaves = leaves.filter(status='pending')
    elif status_filter == 'approved':
        leaves = leaves.filter(status='approved')
    elif status_filter == 'rejected':
        leaves = leaves.filter(status='rejected')
    
    # Pagination
    paginator = Paginator(leaves, 15)  # 15 leaves per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
        'status_filter': status_filter,
        'total_count': LeaveRequest.objects.count(),
        'pending_count': LeaveRequest.objects.filter(status='pending').count(),
        'approved_count': LeaveRequest.objects.filter(status='approved').count(),
        'rejected_count': LeaveRequest.objects.filter(status='rejected').count(),
    }
    
    return render(request, 'leaves/leave_requests.html', context)


@login_required
@require_http_methods(["POST"])
@csrf_protect
def approve_leave(request, leave_id):
    """
    Approve leave request (Admin only)
    AJAX endpoint for approving a leave request
    """
    # Check if user is an admin
    if not request.user.is_admin():
        return JsonResponse({
            'success': False,
            'message': 'Access denied. Only administrators can approve leaves.'
        }, status=403)
    
    leave = get_object_or_404(LeaveRequest, id=leave_id)
    
    if not leave.is_pending():
        return JsonResponse({
            'success': False,
            'message': f'This leave request is already {leave.status}.'
        }, status=400)
    
    # Get remarks from request
    remarks = request.POST.get('remarks', '')
    
    # Approve the leave (handle insufficient balance)
    try:
        leave.approve(admin_user=request.user, remarks=remarks)
    except ValueError as e:
        return JsonResponse({'success': False, 'message': str(e)}, status=400)

    return JsonResponse({
        'success': True,
        'message': f'Leave request #{leave_id} has been approved successfully.',
        'leave_id': leave_id,
        'status': 'approved',
        'action_date': leave.action_date.strftime('%Y-%m-%d %H:%M:%S') if leave.action_date else None
    })


@login_required
@require_http_methods(["POST"])
@csrf_protect
def reject_leave(request, leave_id):
    """
    Reject leave request (Admin only)
    AJAX endpoint for rejecting a leave request
    """
    # Check if user is an admin
    if not request.user.is_admin():
        return JsonResponse({
            'success': False,
            'message': 'Access denied. Only administrators can reject leaves.'
        }, status=403)
    
    leave = get_object_or_404(LeaveRequest, id=leave_id)
    
    if not leave.is_pending():
        return JsonResponse({
            'success': False,
            'message': f'This leave request is already {leave.status}.'
        }, status=400)
    
    # Get remarks from request
    remarks = request.POST.get('remarks', '')
    
    # Reject the leave
    leave.reject(admin_user=request.user, remarks=remarks)
    
    return JsonResponse({
        'success': True,
        'message': f'Leave request #{leave_id} has been rejected.',
        'leave_id': leave_id,
        'status': 'rejected',
        'action_date': leave.action_date.strftime('%Y-%m-%d %H:%M:%S') if leave.action_date else None
    })


# ==================== AJAX API VIEWS ====================

@login_required
def get_leave_requests_ajax(request):
    """
    AJAX endpoint to get leave requests
    Used for real-time dashboard updates
    """
    if request.user.is_admin():
        # Admin sees all pending requests
        pending_leaves = LeaveRequest.objects.filter(status='pending').select_related('user')
        data = {
            'pending_count': pending_leaves.count(),
            'requests': [
                {
                    'id': leave.id,
                    'employee_name': leave.user.full_name or leave.user.username,
                    'employee_id': leave.user.employee_id,
                    'leave_type': leave.get_leave_type_display(),
                    'start_date': leave.start_date.strftime('%Y-%m-%d'),
                    'end_date': leave.end_date.strftime('%Y-%m-%d'),
                    'reason': leave.reason[:100] + '...' if len(leave.reason) > 100 else leave.reason,
                    'created_at': leave.created_at.strftime('%Y-%m-%d %H:%M:%S'),
                }
                for leave in pending_leaves[:10]
            ]
        }
    else:
        # Employee sees their own requests
        user_leaves = LeaveRequest.objects.filter(user=request.user).order_by('-created_at')
        data = {
            'total_leaves': user_leaves.count(),
            'pending_count': user_leaves.filter(status='pending').count(),
            'approved_count': user_leaves.filter(status='approved').count(),
            'rejected_count': user_leaves.filter(status='rejected').count(),
            'requests': [
                {
                    'id': leave.id,
                    'leave_type': leave.get_leave_type_display(),
                    'start_date': leave.start_date.strftime('%Y-%m-%d'),
                    'end_date': leave.end_date.strftime('%Y-%m-%d'),
                    'status': leave.status,
                    'status_display': leave.get_status_display(),
                    'created_at': leave.created_at.strftime('%Y-%m-%d %H:%M:%S'),
                }
                for leave in user_leaves[:5]
            ]
        }
    
    return JsonResponse(data)


@login_required
def check_new_requests(request):
    """
    AJAX endpoint to check for new leave requests
    Used for real-time notifications
    """
    if request.user.is_admin():
        pending_count = LeaveRequest.objects.filter(status='pending').count()
        return JsonResponse({
            'new_requests': pending_count > 0,
            'pending_count': pending_count
        })
    else:
        # For employees, check if any of their requests were updated
        recent_updates = LeaveRequest.objects.filter(
            user=request.user,
            status__in=['approved', 'rejected']
        ).exclude(
            action_date__isnull=True
        ).order_by('-action_at')[:5]
        
        return JsonResponse({
            'recent_updates': [
                {
                    'id': leave.id,
                    'status': leave.status,
                    'action_date': leave.action_date.strftime('%Y-%m-%d %H:%M:%S') if leave.action_date else None
                }
                for leave in recent_updates
            ]
        })
