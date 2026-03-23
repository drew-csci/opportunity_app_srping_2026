from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from django.http import JsonResponse

from .models import Achievement, Opportunity, Application
from .forms import AchievementForm
from accounts.models import User


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


# ---------------------------------------------------------------------------
# Organization Dashboard Views
# ---------------------------------------------------------------------------

@login_required
def organization_dashboard(request):
    """Display organization home dashboard with recent applications."""
    if request.user.user_type != 'organization':
        return redirect('screen1')

    recent_applications = Application.objects.filter(
        opportunity__organization=request.user
    ).select_related('student', 'opportunity').order_by('-applied_date')[:10]

    pending_count = Application.objects.filter(
        opportunity__organization=request.user,
        status='pending'
    ).count()

    accepted_count = Application.objects.filter(
        opportunity__organization=request.user,
        status='accepted'
    ).count()

    total_volunteers = accepted_count

    opportunities_count = Opportunity.objects.filter(
        organization=request.user,
        is_active=True
    ).count()

    context = {
        'recent_applications': recent_applications,
        'pending_count': pending_count,
        'accepted_count': accepted_count,
        'total_volunteers': total_volunteers,
        'opportunities_count': opportunities_count,
    }

    return render(request, 'pages/organization_dashboard.html', context)


@login_required
def applicant_profile(request, applicant_id):
    """Display student profile with achievements and application details."""
    if request.user.user_type != 'organization':
        return redirect('screen1')

    student = get_object_or_404(User, id=applicant_id, user_type='student')
    achievements = student.achievements.all()
    applications = Application.objects.filter(
        student=student,
        opportunity__organization=request.user
    ).select_related('opportunity')

    context = {
        'student': student,
        'achievements': achievements,
        'applications': applications,
    }

    return render(request, 'pages/applicant_profile.html', context)


@login_required
def accept_application(request, application_id):
    """Accept a student application."""
    application = get_object_or_404(Application, id=application_id)

    if application.opportunity.organization != request.user:
        return JsonResponse({'error': 'Unauthorized'}, status=403)

    application.status = 'accepted'
    application.responded_date = timezone.now()
    application.save()

    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({
            'success': True,
            'status': 'accepted',
            'message': f'{application.student.display_name} application accepted!'
        })

    return redirect('applicant_profile', applicant_id=application.student.id)


@login_required
def decline_application(request, application_id):
    """Decline a student application."""
    application = get_object_or_404(Application, id=application_id)

    if application.opportunity.organization != request.user:
        return JsonResponse({'error': 'Unauthorized'}, status=403)

    application.status = 'declined'
    application.responded_date = timezone.now()
    application.save()

    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({
            'success': True,
            'status': 'declined',
            'message': f'{application.student.display_name} application declined.'
        })

    return redirect('applicant_profile', applicant_id=application.student.id)


@login_required
def organization_profile(request):
    """View organization profile."""
    if request.user.user_type != 'organization':
        return redirect('screen1')

    opportunities = Opportunity.objects.filter(organization=request.user)
    context = {
        'opportunities': opportunities,
    }

    return render(request, 'pages/organization_profile.html', context)


@login_required
def organization_messages(request):
    """View organization messages."""
    if request.user.user_type != 'organization':
        return redirect('screen1')

    return render(request, 'pages/organization_messages.html')


@login_required
def organization_opportunities(request):
    """View and manage organization opportunities."""
    if request.user.user_type != 'organization':
        return redirect('screen1')

    opportunities = Opportunity.objects.filter(
        organization=request.user
    ).prefetch_related('applications')

    context = {
        'opportunities': opportunities,
    }

    return render(request, 'pages/organization_opportunities.html', context)
