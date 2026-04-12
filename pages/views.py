from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import get_user_model
from django.contrib import messages
from django.utils import timezone
from accounts.models import User
from .models import Achievement, Opportunity, Application, VolunteerProfile, VolunteerExperience, OrganizationProfile, OrganizationImpactMetric, OrganizationFollow
from .forms import AchievementForm, ApplicationForm, VolunteerProfileForm, VolunteerExperienceForm, OrganizationProfileForm, OrganizationImpactMetricForm
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods

User = get_user_model()


def welcome(request):
    return render(request, 'pages/welcome.html')


@login_required
def screen1(request):
    role = request.user.user_type.title() if hasattr(request.user, 'user_type') else 'User'

    applications = [
        {"student_name": "Alice Chen", "opportunity_title": "Food Bank", "date_applied": "Mar 10", "status": "Applied"},
        {"student_name": "John Smith", "opportunity_title": "Tutoring", "date_applied": "Mar 11", "status": "Accepted"},
        {"student_name": "Maria Lopez", "opportunity_title": "Park Clean", "date_applied": "Mar 12", "status": "Declined"},
    ]

    if request.method == "POST":
        index = int(request.POST.get("index"))
        action = request.POST.get("action")
        if action == "accept":
            applications[index]["status"] = "Accepted"
        elif action == "decline":
            applications[index]["status"] = "Declined"

    return render(request, 'pages/screen1.html', {
        'role': role,
        'applications': applications
    })


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

    opportunity = get_object_or_404(Opportunity, id=opportunity_id, is_active=True)
    application = Application.objects.filter(student=request.user, opportunity=opportunity).first()

    return render(request, 'pages/opportunity_detail.html', {
        'opportunity': opportunity,
        'application': application,
    })


@login_required
def apply_to_opportunity(request, opportunity_id):
    if not hasattr(request.user, 'user_type') or request.user.user_type != 'student':
        return redirect('screen1')

    opportunity = get_object_or_404(Opportunity, id=opportunity_id, is_active=True) # Get the opportunity object based on the provided ID and ensure it is active
    application, created = Application.objects.get_or_create( # Get or create an application object for the current student and opportunity. If it already exists, it will be returned; otherwise, a new one will be created with default values for status and message.
        student=request.user,
        opportunity=opportunity,
        defaults={'status': Application.Status.DRAFT, 'message': ''}
    )

    if application.status != Application.Status.DRAFT and not created: # If the application already exists and is not in draft status, show a warning message and redirect to the application detail page for that application
        messages.warning(request, 'You have already applied for this opportunity.')
        return redirect('application_detail', application_id=application.id)

    if request.method == 'POST': # If the request method is POST, it means the student is submitting the application form. Process the form data to either save it as a draft or submit it as pending based on the action taken by the student.
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
def my_applications(request): # View to display the current student's applications to volunteer opportunities, showing the status and allowing access to application details
    if not hasattr(request.user, 'user_type') or request.user.user_type != 'student':
        return redirect('screen1')

    applications = Application.objects.filter(student=request.user).select_related('opportunity').order_by('-applied_date') # Retrieve all applications for the current student, along with the related opportunity data, and order them by most recent applied date first
    return render(request, 'pages/my_applications.html', {
        'applications': applications,
    })


@login_required
def application_detail(request, application_id): # View to display the details of a specific application, including the opportunity information and the current status of the application
    if not hasattr(request.user, 'user_type') or request.user.user_type != 'student':
        return redirect('screen1')

    application = get_object_or_404(Application, id=application_id, student=request.user) # Get the application object based on the provided ID and ensure it belongs to the current student. If it does not exist, return a 404 error.
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
def organization_applications(request): # View for organizations to see all applications submitted to their volunteer opportunities, excluding drafts, and allowing them to review and manage those applications
    if not hasattr(request.user, 'user_type') or request.user.user_type != 'organization':
        return redirect('screen1')

    applications = Application.objects.filter(
        opportunity__organization=request.user
    ).exclude(status=Application.Status.DRAFT).select_related('student', 'opportunity').order_by('-applied_date')

    return render(request, 'pages/organization_applications.html', {
        'applications': applications,
    })


@login_required
def review_application(request, application_id): # View for organizations to review and manage a specific application submitted to their volunteer opportunities
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

@login_required
def volunteer_profile(request):
    try:
        profile = VolunteerProfile.objects.get(user=request.user)
    except VolunteerProfile.DoesNotExist:
        return redirect('volunteer_profile_edit')
    experiences = VolunteerExperience.objects.filter(volunteer=request.user)
    return render(request, 'pages/volunteer_profile_view.html', {
        'profile': profile,
        'experiences': experiences,
    })

@login_required
def organization_profile(request, org_id):
    organization = get_object_or_404(User, id=org_id, user_type='organization')
    profile, _ = OrganizationProfile.objects.get_or_create(organization=organization)
    is_following = False

    if request.user.user_type == 'student':
        is_following = OrganizationFollow.objects.filter(
            student=request.user,
            organization=organization,
        ).exists()

    opportunities = Opportunity.objects.filter(organization=organization, is_active=True).order_by('-created_at')

    return render(request, 'pages/organization_profile.html', {
        'organization': organization,
        'profile': profile,
        'is_following': is_following,
        'opportunities': opportunities,
        'impact_metrics': profile.impact_metrics.all(),
    })


@login_required
def organization_profile_edit(request, org_id):
    organization = get_object_or_404(User, id=org_id, user_type='organization')
    if request.user != organization:
        return redirect('organization_profile', org_id=org_id)

    profile, _ = OrganizationProfile.objects.get_or_create(organization=organization)

    if request.method == 'POST':
        form = OrganizationProfileForm(request.POST, instance=profile)
        if form.is_valid():
            form.save()
            messages.success(request, 'Organization profile updated.')
            return redirect('organization_profile', org_id=org_id)
    else:
        form = OrganizationProfileForm(instance=profile)

    return render(request, 'pages/organization_profile_edit.html', {
        'organization': organization,
        'profile': profile,
        'form': form,
        'impact_metrics': profile.impact_metrics.all(),
    })


@login_required
def organization_metric_add(request, org_id):
    organization = get_object_or_404(User, id=org_id, user_type='organization')
    if request.user != organization:
        return redirect('organization_profile', org_id=org_id)

    profile, _ = OrganizationProfile.objects.get_or_create(organization=organization)

    if request.method == 'POST':
        form = OrganizationImpactMetricForm(request.POST)
        if form.is_valid():
            metric = form.save(commit=False)
            metric.organization_profile = profile
            metric.save()
            messages.success(request, 'Impact metric added.')
            return redirect('organization_profile_edit', org_id=org_id)
    else:
        form = OrganizationImpactMetricForm()

    return render(request, 'pages/organization_profile_edit.html', {
        'organization': organization,
        'profile': profile,
        'form': OrganizationProfileForm(instance=profile),
        'metric_form': form,
        'impact_metrics': profile.impact_metrics.all(),
        'editing_metric': None,
    })


@login_required
def organization_metric_edit(request, org_id, pk):
    organization = get_object_or_404(User, id=org_id, user_type='organization')
    if request.user != organization:
        return redirect('organization_profile', org_id=org_id)

    profile, _ = OrganizationProfile.objects.get_or_create(organization=organization)
    metric = get_object_or_404(OrganizationImpactMetric, pk=pk, organization_profile=profile)

    if request.method == 'POST':
        form = OrganizationImpactMetricForm(request.POST, instance=metric)
        if form.is_valid():
            form.save()
            messages.success(request, 'Impact metric updated.')
            return redirect('organization_profile_edit', org_id=org_id)
    else:
        form = OrganizationImpactMetricForm(instance=metric)

    return render(request, 'pages/organization_profile_edit.html', {
        'organization': organization,
        'profile': profile,
        'form': OrganizationProfileForm(instance=profile),
        'metric_form': form,
        'impact_metrics': profile.impact_metrics.all(),
        'editing_metric': metric,
    })


@login_required
def organization_metric_delete(request, org_id, pk):
    organization = get_object_or_404(User, id=org_id, user_type='organization')
    if request.user != organization:
        return redirect('organization_profile', org_id=org_id)

    profile, _ = OrganizationProfile.objects.get_or_create(organization=organization)
    metric = get_object_or_404(OrganizationImpactMetric, pk=pk, organization_profile=profile)
    if request.method == 'POST':
        metric.delete()
        messages.success(request, 'Impact metric deleted.')
    return redirect('organization_profile_edit', org_id=org_id)


@login_required
def volunteer_profile_edit(request):
    profile, _ = VolunteerProfile.objects.get_or_create(user=request.user)
    if request.method == 'POST':
        form = VolunteerProfileForm(request.POST)
        if form.is_valid():
            request.user.first_name = form.cleaned_data['first_name']
            request.user.last_name = form.cleaned_data['last_name']
            request.user.email = form.cleaned_data['email']
            request.user.save()
            profile.phone = form.cleaned_data['phone']
            profile.bio = form.cleaned_data['bio']
            profile.skills = form.cleaned_data['skills']
            profile.save()
            return redirect('volunteer_profile')
    else:
        form = VolunteerProfileForm(initial={
            'first_name': request.user.first_name,
            'last_name': request.user.last_name,
            'email': request.user.email,
            'phone': profile.phone,
            'bio': profile.bio,
            'skills': profile.skills,
        })
    experiences = VolunteerExperience.objects.filter(volunteer=request.user)
    return render(request, 'pages/volunteer_profile_edit.html', {
        'form': form,
        'experiences': experiences,
    })


@login_required
def experience_add(request):
    if request.method == 'POST':
        form = VolunteerExperienceForm(request.POST)
        if form.is_valid():
            experience = form.save(commit=False)
            experience.volunteer = request.user
            experience.save()
            return redirect('volunteer_profile_edit')
    else:
        form = VolunteerExperienceForm()
    return render(request, 'pages/volunteer_profile_edit.html', {'form': form})


@login_required
def experience_edit(request, pk):
    experience = get_object_or_404(VolunteerExperience, pk=pk, volunteer=request.user)
    if request.method == 'POST':
        form = VolunteerExperienceForm(request.POST, instance=experience)
        if form.is_valid():
            form.save()
            return redirect('volunteer_profile_edit')
    else:
        form = VolunteerExperienceForm(instance=experience)
    return render(request, 'pages/volunteer_profile_edit.html', {
        'form': form,
        'experience': experience,
    })


@login_required
def experience_delete(request, pk):
    experience = get_object_or_404(VolunteerExperience, pk=pk, volunteer=request.user)
    if request.method == 'POST':
        experience.delete()
    return redirect('volunteer_profile_edit')

@login_required
def follow_organization(request, org_id):
    """follow an organization. Supports both regular POST and AJAX requests."""
    if request.user.user_type != 'student':
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({'success': False, 'error': 'Only students can follow organizations'}, status=403)
        return redirect('screen1')

    organization = get_object_or_404(User, id=org_id, user_type='organization')
    follow_obj, created = OrganizationFollow.objects.get_or_create(
        student=request.user,
        organization=organization,
    )
    
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({
            'success': True,
            'following': True,
            'message': f'You are now following {organization.display_name}'
        })
    
    return redirect('organization_profile', org_id=org_id)


@login_required
@login_required
def unfollow_organization(request, org_id):
    """Unfollow an organization. Supports both regular POST and AJAX requests."""
    if request.user.user_type != 'student':
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({'success': False, 'error': 'Only students can unfollow organizations'}, status=403)
        return redirect('screen1')

    organization = get_object_or_404(User, id=org_id, user_type='organization')
    OrganizationFollow.objects.filter(
        student=request.user,
        organization=organization,
    ).delete()
    
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({
            'success': True,
            'following': False,
            'message': f'You unfollowed {organization.display_name}'
        })
    
    return redirect('organization_profile', org_id=org_id)


@login_required
def followed_organizations(request):
    """Show all organizations the logged-in student follows."""
    if request.user.user_type != 'student':
        return redirect('screen1')

    follows = OrganizationFollow.objects.filter(
        student=request.user,
    ).select_related('organization')

    return render(request, 'pages/followed_organizations.html', {
        'follows': follows,
    })