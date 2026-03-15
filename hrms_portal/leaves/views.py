"""
Leaves Views - Leave management views
"""

import logging
import threading

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_protect
from django.core.paginator import Paginator
from django.core.mail import EmailMultiAlternatives, get_connection
from django.core import signing
from django.conf import settings
from django.urls import reverse
from django.utils import timezone

from .models import LeaveRequest
from .forms import LeaveApplicationForm
from .holiday_calendar import get_excluded_holiday_strings


EMAIL_ACTION_SALT = 'leave-email-action'
EMAIL_ACTION_MAX_AGE_SECONDS = 60 * 60 * 24 * 7
logger = logging.getLogger(__name__)


def _send_leave_notification_async(subject, message, html_message, from_email, to_email):
    """Send leave notification email in a background thread with 587/465 fallback."""
    def _send():
        timeout = int(getattr(settings, 'EMAIL_TIMEOUT', 3))
        for port, use_tls, use_ssl in [(587, True, False), (465, False, True)]:
            try:
                conn = get_connection(
                    backend='django.core.mail.backends.smtp.EmailBackend',
                    host=settings.EMAIL_HOST,
                    port=port,
                    username=settings.EMAIL_HOST_USER,
                    password=settings.EMAIL_HOST_PASSWORD,
                    use_tls=use_tls,
                    use_ssl=use_ssl,
                    timeout=timeout,
                )
                email = EmailMultiAlternatives(
                    subject=subject,
                    body=message,
                    from_email=from_email,
                    to=[to_email],
                    connection=conn,
                )
                email.attach_alternative(html_message, 'text/html')
                email.send(fail_silently=False)
                logger.info('Leave notification sent via port %s', port)
                return
            except Exception as exc:
                logger.warning('SMTP port %s failed: %s', port, exc)
        logger.error('All SMTP attempts failed for leave notification to %s', to_email)

    t = threading.Thread(target=_send, daemon=True)
    t.start()


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

            applicant_name = request.user.full_name or request.user.username
            applicant_email = request.user.email or 'N/A'
            duration_days = leave_request.get_duration_days()
            submitted_at = timezone.localtime(leave_request.created_at).strftime('%Y-%m-%d %H:%M:%S')
            subject = f'New Leave Application - #{leave_request.id}'
            approve_token = signing.dumps(
                {'leave_id': leave_request.id, 'action': 'approve'},
                salt=EMAIL_ACTION_SALT,
            )
            reject_token = signing.dumps(
                {'leave_id': leave_request.id, 'action': 'reject'},
                salt=EMAIL_ACTION_SALT,
            )
            approve_url = request.build_absolute_uri(
                f"{reverse('leave_email_action', kwargs={'leave_id': leave_request.id, 'action': 'approve'})}?token={approve_token}"
            )
            reject_url = request.build_absolute_uri(
                f"{reverse('leave_email_action', kwargs={'leave_id': leave_request.id, 'action': 'reject'})}?token={reject_token}"
            )
            message = (
                f'A new leave application has been submitted.\n\n'
                f'Reference ID: #{leave_request.id}\n'
                f'Applicant: {applicant_name}\n'
                f'Applicant Email: {applicant_email}\n'
                f'Leave Type: {leave_request.get_leave_type_display()}\n'
                f'Start Date: {leave_request.start_date}\n'
                f'End Date: {leave_request.end_date}\n'
                f'Duration (days): {duration_days}\n'
                f'Reason: {leave_request.reason}\n'
                f'Submitted At: {submitted_at}\n'
                f'\nQuick Actions (Admin):\n'
                f'Approve: {approve_url}\n'
                f'Decline: {reject_url}\n'
            )

            html_message = f"""
            <html>
              <body style=\"font-family: Arial, sans-serif; color: #222; line-height: 1.5;\">
                <h2 style=\"margin-bottom: 8px;\">New Leave Application Submitted</h2>
                <p style=\"margin-top: 0; color: #555;\">Reference ID: <strong>#{leave_request.id}</strong></p>
                <table style=\"border-collapse: collapse; width: 100%; max-width: 680px;\">
                  <tr><td style=\"padding: 8px; border: 1px solid #ddd; width: 220px;\"><strong>Applicant</strong></td><td style=\"padding: 8px; border: 1px solid #ddd;\">{applicant_name}</td></tr>
                  <tr><td style=\"padding: 8px; border: 1px solid #ddd;\"><strong>Applicant Email</strong></td><td style=\"padding: 8px; border: 1px solid #ddd;\">{applicant_email}</td></tr>
                  <tr><td style=\"padding: 8px; border: 1px solid #ddd;\"><strong>Leave Type</strong></td><td style=\"padding: 8px; border: 1px solid #ddd;\">{leave_request.get_leave_type_display()}</td></tr>
                  <tr><td style=\"padding: 8px; border: 1px solid #ddd;\"><strong>Start Date</strong></td><td style=\"padding: 8px; border: 1px solid #ddd;\">{leave_request.start_date}</td></tr>
                  <tr><td style=\"padding: 8px; border: 1px solid #ddd;\"><strong>End Date</strong></td><td style=\"padding: 8px; border: 1px solid #ddd;\">{leave_request.end_date}</td></tr>
                  <tr><td style=\"padding: 8px; border: 1px solid #ddd;\"><strong>Duration (days)</strong></td><td style=\"padding: 8px; border: 1px solid #ddd;\">{duration_days}</td></tr>
                  <tr><td style=\"padding: 8px; border: 1px solid #ddd;\"><strong>Submitted At</strong></td><td style=\"padding: 8px; border: 1px solid #ddd;\">{submitted_at}</td></tr>
                </table>
                <h3 style=\"margin-top: 18px; margin-bottom: 8px;\">Reason</h3>
                <p style=\"padding: 10px; background: #f7f7f7; border: 1px solid #e6e6e6; max-width: 680px; white-space: pre-wrap;\">{leave_request.reason}</p>
                                <h3 style="margin-top: 18px; margin-bottom: 10px;">Quick Actions</h3>
                                <p style="max-width: 680px; margin-bottom: 10px; color: #555;">Admin can review and take action directly from this email.</p>
                                <div style="max-width: 680px;">
                                    <a href="{approve_url}" style="display: inline-block; padding: 10px 16px; margin-right: 8px; background: #16a34a; color: #fff; text-decoration: none; border-radius: 6px; font-weight: 600;">Approve</a>
                                    <a href="{reject_url}" style="display: inline-block; padding: 10px 16px; background: #dc2626; color: #fff; text-decoration: none; border-radius: 6px; font-weight: 600;">Decline</a>
                                </div>
              </body>
            </html>
            """

            _send_leave_notification_async(
                subject=subject,
                message=message,
                html_message=html_message,
                from_email=settings.DEFAULT_FROM_EMAIL,
                to_email=settings.ADMIN_NOTIFICATION_EMAIL,
            )

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


@login_required
@require_http_methods(["GET"])
def leave_email_action(request, leave_id, action):
    """Approve or reject a leave request directly from a signed email link."""
    if not request.user.is_admin():
        messages.error(request, 'Access denied. Only administrators can perform this action.')
        return redirect('employee_dashboard')

    leave = get_object_or_404(LeaveRequest, id=leave_id)
    token = request.GET.get('token', '')
    if not token:
        messages.error(request, 'Missing action token. Please use the latest email link.')
        return redirect('leave_requests')

    try:
        payload = signing.loads(
            token,
            salt=EMAIL_ACTION_SALT,
            max_age=EMAIL_ACTION_MAX_AGE_SECONDS,
        )
    except signing.SignatureExpired:
        messages.error(request, 'This email action link has expired. Please use the dashboard.')
        return redirect('leave_requests')
    except signing.BadSignature:
        messages.error(request, 'Invalid email action link. Please use the dashboard.')
        return redirect('leave_requests')

    if payload.get('leave_id') != leave_id or payload.get('action') != action:
        messages.error(request, 'Invalid action details in link. Please use the dashboard.')
        return redirect('leave_requests')

    if not leave.is_pending():
        messages.warning(request, f'Leave request #{leave.id} is already {leave.get_status_display().lower()}.')
        return redirect('leave_requests')

    try:
        if action == 'approve':
            leave.approve(admin_user=request.user, remarks='Approved via email action link.')
            messages.success(request, f'Leave request #{leave.id} approved successfully.')
        elif action == 'reject':
            leave.reject(admin_user=request.user, remarks='Rejected via email action link.')
            messages.success(request, f'Leave request #{leave.id} rejected successfully.')
        else:
            messages.error(request, 'Unsupported action. Please use the dashboard.')
    except ValueError as error:
        messages.error(request, str(error))

    return redirect('leave_requests')
