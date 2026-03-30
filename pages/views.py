from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.core.mail import send_mail
from django.conf import settings

from .models import Achievement, Application, ApplicationReminder
from .forms import AchievementForm

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

@login_required
def dashboard(request):
    """Display student applications with reminder functionality."""
    # Ensure only students can access this
    if not hasattr(request.user, 'user_type') or request.user.user_type != 'student':
        return redirect('screen1')
    
    applications = Application.objects.filter(student=request.user)
    
    # Add reminder eligibility info to each application
    for app in applications:
        app.can_send_reminder = ApplicationReminder.can_send_reminder(app)
    
    return render(request, 'pages/dashboard.html', {
        'applications': applications,
    })


@login_required
@require_http_methods(["POST"])
def send_application_reminder(request, application_id):
    """
    Send a reminder for a pending application.
    Only students can send reminders for their own applications.
    """
    # Ensure user is a student
    if not hasattr(request.user, 'user_type') or request.user.user_type != 'student':
        messages.error(request, 'Only students can send reminders.')
        return redirect('dashboard')
    
    # Get the application
    application = get_object_or_404(Application, id=application_id)
    
    # Verify ownership
    if application.student != request.user:
        messages.error(request, 'You can only send reminders for your own applications.')
        return redirect('dashboard')
    
    # Check if application can be reminded
    if not application.can_remind:
        messages.error(request, f'Cannot send reminder for {application.status} application.')
        return redirect('dashboard')
    
    # Check rate limiting
    if not ApplicationReminder.can_send_reminder(application):
        messages.error(request, 'You can only send one reminder per 24 hours.')
        return redirect('dashboard')
    
    try:
        # Create reminder record
        reminder = ApplicationReminder.objects.create(
            application=application,
            sent_by=request.user
        )
        
        # Send email to organization
        send_reminder_email(application, request.user)
        
        messages.success(request, f'Reminder sent to {application.organization.display_name}!')
        
        return redirect('dashboard')
    
    except Exception as e:
        messages.error(request, f'Error sending reminder: {str(e)}')
        return redirect('dashboard')


def send_reminder_email(application, student):
    """Send email to organization notifying them of the reminder."""
    subject = f"Application Reminder: {student.display_name} - {application.opportunity_title}"
    
    message = f"""
Hello {application.organization.display_name},

{student.display_name} has sent you a reminder about their application for {application.opportunity_title}.

Application Details:
- Student: {student.display_name}
- Email: {student.email}
- Opportunity: {application.opportunity_title}
- Applied: {application.applied_at.strftime('%B %d, %Y')}

Please review their application at your earliest convenience.

Best regards,
Opportunity App Team
    """
    
    try:
        send_mail(
            subject,
            message,
            settings.DEFAULT_FROM_EMAIL,
            [application.organization.email],
            fail_silently=False,
        )
    except Exception as e:
        print(f"Failed to send email: {str(e)}")
