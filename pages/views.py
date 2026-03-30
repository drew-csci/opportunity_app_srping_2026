from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone

from .models import Achievement, Opportunity, Application
from .forms import AchievementForm, ApplicationForm


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
def opportunity_list(request):
    if not hasattr(request.user, 'user_type') or request.user.user_type != 'student':
        return redirect('screen1')

    opportunities = Opportunity.objects.filter(is_active=True).order_by('-created_at')
    return render(request, 'pages/opportunity_list.html', {
        'opportunities': opportunities,
    })


@login_required
def opportunity_detail(request, opportunity_id):
    if not hasattr(request.user, 'user_type') or request.user.user_type != 'student':
        return redirect('screen1')

    opportunity = get_object_or_404(Opportunity, id=opportunity_id, active=True)
    application = Application.objects.filter(student=request.user, opportunity=opportunity).first()

    return render(request, 'pages/opportunity_detail.html', {
        'opportunity': opportunity,
        'application': application,
    })


@login_required
def apply_to_opportunity(request, opportunity_id):
    if not hasattr(request.user, 'user_type') or request.user.user_type != 'student':
        return redirect('screen1')

    opportunity = get_object_or_404(Opportunity, id=opportunity_id, is_active=True)
    application, created = Application.objects.get_or_create(
        student=request.user,
        opportunity=opportunity,
        defaults={'status': Application.Status.DRAFT, 'message': ''}
    )

    if application.status != Application.Status.DRAFT and not created:
        messages.warning(request, 'You have already applied for this opportunity.')
        return redirect('application_detail', application_id=application.id)

    if request.method == 'POST':
        form = ApplicationForm(request.POST, instance=application)
        if form.is_valid():
            application = form.save(commit=False)
            action = request.POST.get('action')
            if action == 'save_draft':
                application.status = Application.Status.DRAFT
                messages.success(request, 'Application draft saved. You can complete it later.')
            else:
                application.status = Application.Status.PENDING
                application.responded_date = None
                messages.success(request, 'Application submitted. The organization will review it soon.')
            application.save()
            return redirect('application_detail', application_id=application.id)
    else:
        form = ApplicationForm(instance=application)

    return render(request, 'pages/application_form.html', {
        'opportunity': opportunity,
        'form': form,
        'application': application,
    })


@login_required
def my_applications(request):
    if not hasattr(request.user, 'user_type') or request.user.user_type != 'student':
        return redirect('screen1')

    applications = Application.objects.filter(student=request.user).select_related('opportunity').order_by('-applied_date')
    return render(request, 'pages/my_applications.html', {
        'applications': applications,
    })


@login_required
def application_detail(request, application_id):
    if not hasattr(request.user, 'user_type') or request.user.user_type != 'student':
        return redirect('screen1')

    application = get_object_or_404(Application, id=application_id, student=request.user)
    return render(request, 'pages/application_detail.html', {
        'application': application,
    })


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


@login_required
def organization_applications(request):
    if not hasattr(request.user, 'user_type') or request.user.user_type != 'organization':
        return redirect('screen1')

    applications = Application.objects.filter(
        opportunity__organization=request.user
    ).exclude(status=Application.Status.DRAFT).select_related('student', 'opportunity').order_by('-applied_date')

    return render(request, 'pages/organization_applications.html', {
        'applications': applications,
    })


@login_required
def review_application(request, application_id):
    if not hasattr(request.user, 'user_type') or request.user.user_type != 'organization':
        return redirect('screen1')

    application = get_object_or_404(
        Application,
        id=application_id,
        opportunity__organization=request.user
    )

    if request.method == 'POST':
        decision = request.POST.get('decision')
        if decision in (Application.Status.ACCEPTED, Application.Status.DENIED):
            application.status = decision
            if application.responded_date is None:
                application.responded_date = timezone.now()
            application.save()
            messages.success(request, f'Application status updated to {application.get_status_display()}.')
            return redirect('organization_applications')
        messages.error(request, 'Please choose a valid decision.')

    return render(request, 'pages/review_application.html', {
        'application': application,
    })


def faq(request):
    return render(request, 'pages/faq.html')


def dashboard(request):
    return render(request, 'pages/dashboard.html')
