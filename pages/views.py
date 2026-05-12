from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.http import JsonResponse, HttpResponseForbidden
from django.utils import timezone
from django.views.decorators.http import require_http_methods
from django.contrib.auth import get_user_model
from django.contrib import messages

from .models import Achievement, StudentOpportunity, Opportunity, OrganizationFollow, Notification, VolunteerProfile, VolunteerExperience, Application, OrganizationProfile, OrganizationImpactMetric, Message, ContactMessage
from .forms import AchievementForm, OpportunityForm, VolunteerProfileForm, VolunteerExperienceForm, ApplicationForm, OrganizationProfileForm, OrganizationImpactMetricForm, MessageReplyForm, ContactForm
from django.contrib.auth import get_user_model

User = get_user_model()

def welcome(request):
    return render(request, 'pages/welcome.html')

@login_required
def screen1(request):
    role = request.user.user_type.title() if hasattr(request.user, 'user_type') else 'User'

    base_opportunities = Opportunity.objects.filter(is_active=True)
    opportunities = base_opportunities

    query = request.GET.get('q', '').strip()
    location = request.GET.get('location', '').strip()
    cause = request.GET.get('cause', '').strip()
    duration = request.GET.get('duration', '').strip()
    skills = request.GET.get('skills', '').strip()
    opp_type = request.GET.get('type', '').strip()

    if query:
        opportunities = opportunities.filter(
            Q(title__icontains=query) |
            Q(description__icontains=query) |
            Q(cause__icontains=query) |
            Q(location__icontains=query) |
            Q(required_skills__icontains=query)
        )
    if location:
        opportunities = opportunities.filter(location__icontains=location)
    if cause:
        opportunities = opportunities.filter(cause__icontains=cause)
    if duration:
        opportunities = opportunities.filter(duration__icontains=duration)
    if skills:
        opportunities = opportunities.filter(required_skills__icontains=skills)
    if opp_type:
        opportunities = opportunities.filter(opportunity_type=opp_type)

    location_options = sorted(
        base_opportunities.exclude(location='').values_list('location', flat=True).distinct()
    )
    duration_options = sorted(
        base_opportunities.exclude(duration='').values_list('duration', flat=True).distinct()
    )

    skill_options = []
    seen_skills = set()
    for skill_text in base_opportunities.exclude(required_skills='').values_list('required_skills', flat=True):
        for skill in [value.strip() for value in skill_text.split(',') if value.strip()]:
            normalized = skill.lower()
            if normalized in seen_skills:
                continue
            seen_skills.add(normalized)
            skill_options.append(skill)
    skill_options.sort(key=str.lower)

    context = {
        'role': role,
        'opportunities': opportunities,
        'query': query,
        'filter_options': {
            'locations': location_options,
            'durations': duration_options,
            'skills': skill_options,
        },
        'filters': {
            'location': location,
            'cause': cause,
            'duration': duration,
            'skills': skills,
            'type': opp_type,
        },
    }
    return render(request, 'pages/screen1.html', context)

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
def application_detail(request, application_id): # View to display the details of a specific application, including the opportunity information and the current status of the application
    if not hasattr(request.user, 'user_type') or request.user.user_type != 'student':
        return redirect('screen1')

    application = get_object_or_404(Application, id=application_id, student=request.user) # Get the application object based on the provided ID and ensure it belongs to the current student. If it does not exist, return a 404 error.
    return render(request, 'pages/application_detail.html', {
        'application': application,
    })


@login_required
@require_http_methods(['POST'])
def remind_organization(request, application_id):
    if not hasattr(request.user, 'user_type') or request.user.user_type != 'student':
        return redirect('screen1')

    application = get_object_or_404(Application, id=application_id, student=request.user)
    if application.status != 'pending':
        messages.error(request, 'Reminders are only for pending applications.')
        return redirect('my_applications')

    organization = application.opportunity.organization
    messages.success(request, f'Reminder sent to {organization.display_name}.')
    return redirect('my_applications')
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
def my_applications(request):
    if not hasattr(request.user, 'user_type') or request.user.user_type != 'student':
        return redirect('screen1')
    applications = Application.objects.filter(student=request.user).select_related('opportunity').order_by('-applied_date')
    return render(request, 'pages/my_applications.html', {'applications': applications})


@login_required
def organization_applications(request):
    if not hasattr(request.user, 'user_type') or request.user.user_type != 'organization':
        return redirect('screen1')
    applications = Application.objects.filter(
        opportunity__organization=request.user
    ).select_related('student', 'opportunity').order_by('-applied_date')
    return render(request, 'pages/organization_applications.html', {
        'applications': applications,
    })


@login_required
def review_application(request, application_id):
    if not hasattr(request.user, 'user_type') or request.user.user_type != 'organization':
        return redirect('screen1')
    application = get_object_or_404(Application, id=application_id, opportunity__organization=request.user)
    if request.method == 'POST':
        decision = request.POST.get('decision')
        if decision in ('accepted', 'declined'):
            application.status = decision
            if application.responded_date is None:
                application.responded_date = timezone.now()
            application.save()
            from django.db import connection as db_conn
            with db_conn.cursor() as cur:
                cur.execute(
                    "INSERT INTO pages_notification (recipient_id, message, is_read, created_at, notification_type) VALUES (%s, %s, %s, NOW(), %s)",
                    [application.student.id, f"Your application to '{application.opportunity.title}' has been {decision}.", False, decision]
                )
            messages.success(request, f'Application status updated.')
            return redirect('organization_applications')
        messages.error(request, 'Please choose a valid decision.')
    return render(request, 'pages/review_application.html', {'application': application})


def faq(request):
    return render(request, 'pages/faq.html')


@login_required
def dashboard(request):
    role = request.user.user_type.title() if hasattr(request.user, 'user_type') else 'User'
    context = {'role': role}
    if hasattr(request.user, 'user_type') and request.user.user_type == 'organization':
        unread_count = Message.objects.filter(recipient=request.user, is_read=False).count()
        context['unread_message_count'] = unread_count
    return render(request, 'pages/dashboard.html', context)


@login_required
def student_dashboard(request):
    if not hasattr(request.user, 'user_type') or request.user.user_type != 'student':
        return redirect('screen1')
    completed_opportunities = StudentOpportunity.objects.filter(student=request.user, status='completed').select_related('opportunity', 'opportunity__organization')
    in_progress_opportunities = StudentOpportunity.objects.filter(student=request.user, status='in_progress').select_related('opportunity', 'opportunity__organization')
    pending_opportunities = StudentOpportunity.objects.filter(student=request.user, status='pending').select_related('opportunity', 'opportunity__organization')
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
    if not hasattr(request.user, 'user_type') or request.user.user_type != 'student':
        return HttpResponseForbidden("Only students can access this action.")
    student_opportunity = get_object_or_404(StudentOpportunity, id=student_opportunity_id)
    if student_opportunity.student != request.user:
        return HttpResponseForbidden("You can only mark your own opportunities as pending.")
    if student_opportunity.status != 'in_progress':
        return redirect('student_dashboard')
    if request.method == 'POST':
        student_opportunity.status = 'pending'
        student_opportunity.date_pending = timezone.now()
        student_opportunity.save()
        return redirect('student_dashboard')
    return render(request, 'pages/mark_opportunity_pending.html', {'student_opportunity': student_opportunity})


@login_required
def organization_dashboard(request):
    if request.user.user_type != 'organization':
        return redirect('screen1')
    recent_applications = Application.objects.filter(opportunity__organization=request.user).select_related('student', 'opportunity').order_by('-applied_date')[:10]
    pending_count = Application.objects.filter(opportunity__organization=request.user, status='pending').count()
    accepted_count = Application.objects.filter(opportunity__organization=request.user, status='accepted').count()
    opportunities_count = Opportunity.objects.filter(organization=request.user, is_active=True).count()
    context = {
        'recent_applications': recent_applications,
        'pending_count': pending_count,
        'accepted_count': accepted_count,
        'total_volunteers': accepted_count,
        'opportunities_count': opportunities_count,
    }
    return render(request, 'pages/organization_dashboard.html', context)


@login_required
def applicant_profile(request, applicant_id):
    if request.user.user_type != 'organization':
        return redirect('screen1')
    student = get_object_or_404(User, id=applicant_id, user_type='student')
    achievements = student.achievements.all()
    applications = Application.objects.filter(student=student, opportunity__organization=request.user).select_related('opportunity')
    return render(request, 'pages/applicant_profile.html', {
        'student': student, 'achievements': achievements, 'applications': applications,
    })


@login_required
def accept_application(request, application_id):
    application = get_object_or_404(Application, id=application_id)
    if application.opportunity.organization != request.user:
        return JsonResponse({'error': 'Unauthorized'}, status=403)
    application.status = 'accepted'
    application.responded_date = timezone.now()
    application.save()
    from pages.models import Notification
    Notification.objects.create(
            recipient=application.student,
            message=f"Your application to '{application.opportunity.title}' has been accepted!",
            is_read=False,
        )
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({'success': True, 'status': 'accepted', 'message': f'{application.student.display_name} application accepted!'})
    return redirect('applicant_profile', applicant_id=application.student.id)


@login_required
def decline_application(request, application_id):
    application = get_object_or_404(Application, id=application_id)
    if application.opportunity.organization != request.user:
        return JsonResponse({'error': 'Unauthorized'}, status=403)
    application.status = 'declined'
    application.responded_date = timezone.now()
    application.save()
    from django.db import connection
    with connection.cursor() as cursor:
        cursor.execute(
            "INSERT INTO pages_notification (recipient_id, message, is_read, created_at, notification_type) VALUES (%s, %s, %s, CURRENT_TIMESTAMP, %s)",
            [application.student.id, f"Your application to '{application.opportunity.title}' has been declined.", False, "declined"]
        )
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({'success': True, 'status': 'declined', 'message': f'{application.student.display_name} application declined.'})
    return redirect('applicant_profile', applicant_id=application.student.id)


@login_required
def organization_opportunities(request):
    if request.user.user_type != 'organization':
        return redirect('screen1')
    opportunities = Opportunity.objects.filter(organization=request.user).prefetch_related('applications')
    return render(request, 'pages/organization_opportunities.html', {'opportunities': opportunities})


@login_required
def organization_post_opportunity(request):
    if request.user.user_type != 'organization':
        return redirect('screen1')
    if request.method == 'POST':
        form = OpportunityForm(request.POST)
        if form.is_valid():
            opportunity = form.save(commit=False)
            opportunity.organization = request.user
            opportunity.save()
            messages.success(request, f'"{opportunity.title}" has been posted successfully.')
            return redirect('organization_opportunities')
        messages.error(request, 'Please correct the highlighted fields and try again.')
    else:
        form = OpportunityForm()
    return render(request, 'pages/organization_post_opportunity.html', {'form': form})


@login_required
def volunteer_profile(request):
    try:
        profile = VolunteerProfile.objects.get(user=request.user)
    except VolunteerProfile.DoesNotExist:
        return redirect('volunteer_profile_edit')
    experiences = VolunteerExperience.objects.filter(volunteer=request.user)
    return render(request, 'pages/volunteer_profile_view.html', {'profile': profile, 'experiences': experiences})


@login_required
def organization_profile(request, org_id):
    organization = get_object_or_404(User, id=org_id, user_type='organization')
    profile, _ = OrganizationProfile.objects.get_or_create(organization=organization)
    is_following = False
    unread_message_count = 0
    if request.user.user_type == 'student':
        is_following = OrganizationFollow.objects.filter(student=request.user, organization=organization).exists()
    elif request.user.user_type == 'organization' and request.user.id == org_id:
        unread_message_count = Message.objects.filter(recipient=request.user, is_read=False).count()

    current_opportunities = Opportunity.objects.filter(
        organization=organization,
        is_active=True
    ).order_by('-posted_date')

    past_opportunities = Opportunity.objects.filter(
        organization=organization,
        is_active=False
    ).order_by('-posted_date')

    return render(request, 'pages/organization_profile.html', {
        'organization': organization,
        'profile': profile,
        'is_following': is_following,
        'current_opportunities': current_opportunities,
        'past_opportunities': past_opportunities,
        'impact_metrics': profile.impact_metrics.all(),
        'unread_message_count': unread_message_count,
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
            profile.location = form.cleaned_data['location']
            profile.bio = form.cleaned_data['bio']
            profile.skills = form.cleaned_data['skills']
            profile.interests = form.cleaned_data['interests']
            profile.save()
            return redirect('volunteer_profile')
    else:
        form = VolunteerProfileForm(initial={
            'first_name': request.user.first_name, 'last_name': request.user.last_name,
            'email': request.user.email, 'phone': profile.phone, 'location': profile.location,
            'bio': profile.bio, 'skills': profile.skills, 'interests': profile.interests,
        })
    experiences = VolunteerExperience.objects.filter(volunteer=request.user)
    return render(request, 'pages/volunteer_profile_edit.html', {'form': form, 'experiences': experiences})


@login_required
def experience_add(request):
    if request.method == 'POST':
        form = VolunteerExperienceForm(request.POST)
        if form.is_valid():
            exp = form.save(commit=False)
            exp.volunteer = request.user
            exp.save()
            return redirect('volunteer_profile_edit')
    else:
        form = VolunteerExperienceForm()
    return render(request, 'pages/experience_form.html', {'form': form})


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
    return render(request, 'pages/experience_form.html', {'form': form})


@login_required
def experience_delete(request, pk):
    experience = get_object_or_404(VolunteerExperience, pk=pk, volunteer=request.user)
    if request.method == 'POST':
        experience.delete()
    return redirect('volunteer_profile_edit')


@login_required
def follow_organization(request, org_id):
    """Follow an organization. Supports both regular POST and AJAX requests."""
    if request.user.user_type != 'student':
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({'success': False, 'error': 'Only students can follow organizations'}, status=403)
        return redirect('screen1')
    organization = get_object_or_404(User, id=org_id, user_type='organization')
    OrganizationFollow.objects.get_or_create(student=request.user, organization=organization)
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({'success': True, 'following': True, 'message': f'You are now following {organization.display_name}'})
    return redirect('organization_profile', org_id=org_id)


@login_required
def unfollow_organization(request, org_id):
    if request.user.user_type != 'student':
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({'success': False, 'error': 'Only students can unfollow organizations'}, status=403)
        return redirect('screen1')
    organization = get_object_or_404(User, id=org_id, user_type='organization')
    OrganizationFollow.objects.filter(student=request.user, organization=organization).delete()
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({'success': True, 'following': False, 'message': f'You unfollowed {organization.display_name}'})
    return redirect('organization_profile', org_id=org_id)


@login_required
def followed_organizations(request):
    if request.user.user_type != 'student':
        return redirect('screen1')
    follows = OrganizationFollow.objects.filter(student=request.user).select_related('organization')
    return render(request, 'pages/followed_organizations.html', {'follows': follows})



@login_required
def organization_inbox(request):
    if not hasattr(request.user, 'user_type') or request.user.user_type != 'organization':
        return redirect('screen1')
    inbox_messages = Message.objects.filter(recipient=request.user).select_related('sender').order_by('-sent_at')
    return render(request, 'pages/organization_inbox.html', {'messages': inbox_messages})


@login_required
def message_detail(request, message_id):
    if not hasattr(request.user, 'user_type') or request.user.user_type != 'organization':
        return redirect('screen1')
    message = get_object_or_404(Message, id=message_id, recipient=request.user)
    message.mark_as_read()
    replies = message.replies.all().select_related('sender', 'recipient').order_by('sent_at')
    if request.method == 'POST':
        form = MessageReplyForm(request.POST)
        if form.is_valid():
            try:
                Message.objects.create(
                    sender=request.user, recipient=message.sender,
                    subject=f"Re: {message.subject}", content=form.cleaned_data['reply_content'],
                    reply_to=message,
                )
                messages.success(request, 'Your reply has been sent successfully!')
                return redirect('message_detail', message_id=message_id)
            except Exception as e:
                messages.error(request, f'There was an error sending your reply: {str(e)}')
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, str(error))
    else:
        form = MessageReplyForm()
    return render(request, 'pages/message_detail.html', {'message': message, 'replies': replies, 'form': form})


@login_required
def volunteer_sent_messages(request):
    if not hasattr(request.user, 'user_type') or request.user.user_type != 'student':
        return redirect('screen1')
    sent_messages = Message.objects.filter(sender=request.user).select_related('recipient').order_by('-sent_at')
    return render(request, 'pages/volunteer_sent_messages.html', {'messages': sent_messages})


@login_required
def volunteer_sent_message_detail(request, message_id):
    if not hasattr(request.user, 'user_type') or request.user.user_type != 'student':
        return redirect('screen1')
    message = get_object_or_404(Message, id=message_id, sender=request.user)
    replies = message.replies.all().select_related('sender', 'recipient').order_by('sent_at')
    return render(request, 'pages/volunteer_sent_message_detail.html', {'message': message, 'replies': replies})

    return render(request, 'pages/volunteer_sent_message_detail.html', {
        'message': message,
        'replies': replies,
    })


@login_required
@require_http_methods(["POST"])
def submit_report(request):
    """
    Handle report submission from modal.
    Expects POST data with: target_type, target_id, reason, notes
    Returns JSON response with success/error status.
    """
    if request.method == 'POST':
        target_type = request.POST.get('target_type')
        target_id = request.POST.get('target_id')
        reason = request.POST.get('reason')
        notes = request.POST.get('notes', '').strip()
        
        # Validate required fields
        if not all([target_type, target_id, reason]):
            return JsonResponse(
                {'success': False, 'error': 'Missing required fields'},
                status=400
            )
        
        # Validate target_type
        valid_target_types = [choice[0] for choice in Report.TargetType.choices]
        if target_type not in valid_target_types:
            return JsonResponse(
                {'success': False, 'error': 'Invalid target type'},
                status=400
            )
        
        # Validate reason
        valid_reasons = [choice[0] for choice in Report.ReportReason.choices]
        if reason not in valid_reasons:
            return JsonResponse(
                {'success': False, 'error': 'Invalid report reason'},
                status=400
            )
        
        # Validate target_id is a positive integer
        try:
            target_id = int(target_id)
            if target_id <= 0:
                raise ValueError
        except (ValueError, TypeError):
            return JsonResponse(
                {'success': False, 'error': 'Invalid target ID'},
                status=400
            )
        
        try:
            # Create the report
            report = Report.objects.create(
                reporter=request.user,
                target_type=target_type,
                target_id=target_id,
                reason=reason,
                notes=notes,
                status=Report.ReportStatus.PENDING
            )
            
            return JsonResponse({
                'success': True,
                'message': 'Thank you for your report. Our moderation team will review it shortly.',
                'report_id': report.id
            })
        except Exception as e:
            return JsonResponse(
                {'success': False, 'error': f'Error submitting report: {str(e)}'},
                status=500
            )
    
    return JsonResponse(
        {'success': False, 'error': 'Invalid request method'},
        status=405
    )


@login_required
def report_queue(request):
    """
    Display queue of reported content for administrative review.
    Only accessible to staff/admin users.
    """
    # Check if user is staff/admin
    if not request.user.is_staff:
        return HttpResponseForbidden("You do not have permission to access this page.")
    
    # Get all pending reports with related data
    pending_reports = Report.objects.filter(
        status=Report.ReportStatus.PENDING
    ).select_related('reporter').order_by('-created_at')
    
    # Get summary counts
    total_pending = pending_reports.count()
    pending_by_type = {}
    pending_by_reason = {}
    
    for report in pending_reports:
        # Count by target type
        pending_by_type[report.get_target_type_display()] = \
            pending_by_type.get(report.get_target_type_display(), 0) + 1
        
        # Count by reason
        pending_by_reason[report.get_reason_display()] = \
            pending_by_reason.get(report.get_reason_display(), 0) + 1
    
    # Optional filtering
    filter_target_type = request.GET.get('target_type')
    filter_reason = request.GET.get('reason')
    filter_status = request.GET.get('status', Report.ReportStatus.PENDING)
    
    reports = Report.objects.select_related('reporter').order_by('-created_at')
    
    if filter_target_type:
        reports = reports.filter(target_type=filter_target_type)
    
    if filter_reason:
        reports = reports.filter(reason=filter_reason)
    
    if filter_status:
        reports = reports.filter(status=filter_status)
    
    context = {
        'reports': reports,
        'total_pending': total_pending,
        'pending_by_type': pending_by_type,
        'pending_by_reason': pending_by_reason,
        'filter_target_type': filter_target_type,
        'filter_reason': filter_reason,
        'filter_status': filter_status,
        'status_choices': Report.ReportStatus.choices,
        'target_type_choices': Report.TargetType.choices,
        'reason_choices': Report.ReportReason.choices,
    }
    
    return render(request, 'pages/report_queue.html', context)

@login_required
def student_notifications(request):
    if not hasattr(request.user, 'user_type') or request.user.user_type != 'student':
        return redirect('screen1')
    notifications = Notification.objects.filter(recipient=request.user)
    return render(request, 'pages/student_notifications.html', {'notifications': notifications})


@login_required
def contact_us(request):
    success = False
    initial = {}
    if request.user.is_authenticated:
        initial['role'] = request.user.user_type if request.user.user_type in ('student', 'organization') else ''

    if request.method == 'POST':
        form = ContactForm(request.POST)
        if form.is_valid():
            form.save()
            success = True
            form = ContactForm(initial=initial)
    else:
        form = ContactForm(initial=initial)

    return render(request, 'pages/contact_us.html', {'form': form, 'success': success})
