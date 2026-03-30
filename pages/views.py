from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from django.http import HttpResponseForbidden

from .models import Achievement, StudentOpportunity, Opportunity, Notification
from .forms import AchievementForm, MarkOpportunityPendingForm, DenyOpportunityForm

def welcome(request):
    return render(request, 'pages/welcome.html')

@login_required
def screen1(request):
    role = request.user.user_type.title() if hasattr(request.user, 'user_type') else 'User'
    return render(request, 'pages/screen1.html', {'role': role})

@login_required
def screen2(request):
    role = request.user.user_type.title() if hasattr(request.user, 'user_type') else 'User'
    return render(request, 'pages/screen2.html', {'role': role})

@login_required
def screen3(request):
    role = request.user.user_type.title() if hasattr(request.user, 'user_type') else 'User'
    return render(request, 'pages/screen3.html', {'role': role})


@login_required
def student_achievements(request):
    if not hasattr(request.user, 'user_type') or request.user.user_type != 'student':
        # Redirect non-students
        return redirect('screen1')

    if request.method == 'POST':
        form = AchievementForm(request.POST)
        if form.is_valid():
            achievement = form.save(commit=False)
            achievement.student = request.user
            achievement.save()
            return redirect('student_achievements')
    else:
        form = AchievementForm()

    achievements = Achievement.objects.filter(student=request.user).order_by('-date_completed')
    return render(request, 'pages/student_achievements.html', {
        'achievements': achievements,
        'form': form,
    })

def faq(request):
    return render(request, 'pages/faq.html')

def dashboard(request):
    return render(request, 'pages/dashboard.html')


@login_required
def student_dashboard(request):
    """
    Student-specific dashboard displaying completed opportunities.
    Only accessible to users with 'student' user type.
    """
    # Verify the user is a student
    if not hasattr(request.user, 'user_type') or request.user.user_type != 'student':
        return redirect('screen1')

    # Get all completed opportunities for the logged-in student
    completed_opportunities = StudentOpportunity.objects.filter(
        student=request.user,
        status='completed'
    ).select_related('opportunity', 'opportunity__organization')

    # Optional: Get in-progress opportunities as well for context
    in_progress_opportunities = StudentOpportunity.objects.filter(
        student=request.user,
        status='in_progress'
    ).select_related('opportunity', 'opportunity__organization')
    
    # Get pending opportunities
    pending_opportunities = StudentOpportunity.objects.filter(
        student=request.user,
        status='pending'
    ).select_related('opportunity', 'opportunity__organization')

    context = {
        'completed_opportunities': completed_opportunities,
        'in_progress_opportunities': in_progress_opportunities,
        'pending_opportunities': pending_opportunities,
        'completed_count': completed_opportunities.count(),
        'pending_count': pending_opportunities.count(),
    }

    return render(request, 'pages/student_dashboard.html', context)


@login_required
def mark_opportunity_pending(request, student_opportunity_id):
    """
    Mark an in-progress opportunity as pending completion.
    Only accessible to the student who is working on the opportunity.
    """
    # Verify the user is a student
    if not hasattr(request.user, 'user_type') or request.user.user_type != 'student':
        return HttpResponseForbidden("Only students can access this action.")

    # Get the student opportunity record
    student_opportunity = get_object_or_404(StudentOpportunity, id=student_opportunity_id)

    # Verify the student owns this record
    if student_opportunity.student != request.user:
        return HttpResponseForbidden("You can only mark your own opportunities as pending.")

    # Verify the opportunity is currently in_progress
    if student_opportunity.status != 'in_progress':
        return redirect('student_dashboard')

    if request.method == 'POST':
        form = MarkOpportunityPendingForm(request.POST, instance=student_opportunity)
        if form.is_valid():
            student_opportunity.status = 'pending'
            student_opportunity.date_pending = timezone.now()
            student_opportunity.save()
            return redirect('student_dashboard')
    else:
        form = MarkOpportunityPendingForm(instance=student_opportunity)

    return render(request, 'pages/mark_opportunity_pending.html', {
        'form': form,
        'student_opportunity': student_opportunity,
    })


@login_required
def organization_dashboard(request):
    """
    Organization dashboard showing pending opportunity completions.
    Only accessible to users with 'organization' user type.
    """
    # Verify the user is an organization
    if not hasattr(request.user, 'user_type') or request.user.user_type != 'organization':
        return redirect('screen1')

    # Get all pending completions for opportunities posted by this organization
    pending_completions = StudentOpportunity.objects.filter(
        opportunity__organization=request.user,
        status='pending'
    ).select_related('student', 'opportunity')

    context = {
        'pending_completions': pending_completions,
        'pending_count': pending_completions.count(),
    }

    return render(request, 'pages/organization_dashboard.html', context)


@login_required
def approve_opportunity_completion(request, student_opportunity_id):
    """
    Approve a pending opportunity completion.
    Changes status from 'pending' to 'completed'.
    Only accessible to the organization that posted the opportunity.
    """
    # Verify the user is an organization
    if not hasattr(request.user, 'user_type') or request.user.user_type != 'organization':
        return HttpResponseForbidden("Only organizations can access this action.")

    # Get the student opportunity record
    student_opportunity = get_object_or_404(StudentOpportunity, id=student_opportunity_id)

    # Verify this organization posted the related opportunity
    if student_opportunity.opportunity.organization != request.user:
        return HttpResponseForbidden("You can only manage opportunities you posted.")

    # Verify the opportunity is currently pending
    if student_opportunity.status != 'pending':
        return redirect('organization_dashboard')

    if request.method == 'POST':
        # Mark as completed
        student_opportunity.status = 'completed'
        student_opportunity.date_completed = timezone.now()
        student_opportunity.save()

        # Create notification for student
        Notification.objects.create(
            recipient=student_opportunity.student,
            notification_type=Notification.NotificationType.COMPLETION_APPROVED,
            student_opportunity=student_opportunity,
            message=f"Your completion of '{student_opportunity.opportunity.title}' has been approved!"
        )

        return redirect('organization_dashboard')

    return render(request, 'pages/approve_opportunity.html', {
        'student_opportunity': student_opportunity,
    })


@login_required
def deny_opportunity_completion(request, student_opportunity_id):
    """
    Deny a pending opportunity completion and send it back to in_progress.
    Only accessible to the organization that posted the opportunity.
    """
    # Verify the user is an organization
    if not hasattr(request.user, 'user_type') or request.user.user_type != 'organization':
        return HttpResponseForbidden("Only organizations can access this action.")

    # Get the student opportunity record
    student_opportunity = get_object_or_404(StudentOpportunity, id=student_opportunity_id)

    # Verify this organization posted the related opportunity
    if student_opportunity.opportunity.organization != request.user:
        return HttpResponseForbidden("You can only manage opportunities you posted.")

    # Verify the opportunity is currently pending
    if student_opportunity.status != 'pending':
        return redirect('organization_dashboard')

    if request.method == 'POST':
        form = DenyOpportunityForm(request.POST)
        if form.is_valid():
            denial_reason = form.cleaned_data['denial_reason']

            # Mark as back to in_progress
            student_opportunity.status = 'in_progress'
            student_opportunity.denial_reason = denial_reason
            student_opportunity.date_pending = None  # Clear the pending date
            student_opportunity.save()

            # Create notification for student
            Notification.objects.create(
                recipient=student_opportunity.student,
                notification_type=Notification.NotificationType.COMPLETION_DENIED,
                student_opportunity=student_opportunity,
                message=f"Your completion of '{student_opportunity.opportunity.title}' was not approved.\n\nFeedback: {denial_reason}"
            )

            return redirect('organization_dashboard')
    else:
        form = DenyOpportunityForm()

    return render(request, 'pages/deny_opportunity.html', {
        'form': form,
        'student_opportunity': student_opportunity,
    })


@login_required
def student_notifications(request):
    """
    Show all notifications for the logged-in student.
    Only accessible to users with 'student' user type.
    """
    # Verify the user is a student
    if not hasattr(request.user, 'user_type') or request.user.user_type != 'student':
        return redirect('screen1')

    notifications = Notification.objects.filter(recipient=request.user)

    context = {
        'notifications': notifications,
    }

    return render(request, 'pages/student_notifications.html', context)
