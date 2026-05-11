from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse, HttpResponseForbidden
from django.utils import timezone
from accounts.models import User
from .models import Achievement, Opportunity, Application, StudentOpportunity, OrganizationFollow, Notification, VolunteerProfile, VolunteerExperience, Message
from .forms import AchievementForm, OpportunityForm, VolunteerProfileForm, VolunteerExperienceForm, MessageReplyForm


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
        from .forms import ApplicationForm
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
        from .forms import ApplicationForm
        form = ApplicationForm(instance=application)

    return render(request, 'pages/application_form.html', {
        'opportunity': opportunity,
        'form': form,
        'application': application,
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
def remind_organization(request, application_id):
    if not hasattr(request.user, 'user_type') or request.user.user_type != 'student':
        return redirect('screen1')

    application = get_object_or_404(Application, id=application_id, student=request.user)
    if application.status != Application.Status.PENDING:
        messages.error(request, 'Reminders can only be sent for applications that are still pending.')
        return redirect('my_applications')

    organization = application.opportunity.organization
    messages.success(request, f'Reminder sent to {organization.display_name}.')
    return redirect('my_applications')


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
            messages.success(request, f'Application status updated.')
            return redirect('organization_applications')
        messages.error(request, 'Please choose a valid decision.')
    return render(request, 'pages/review_application.html', {'application': application})


def faq(request):
    return render(request, 'pages/faq.html')


@login_required
def dashboard(request):
    if hasattr(request.user, 'user_type'):
        if request.user.user_type == 'student':
            return redirect('student_dashboard')
        if request.user.user_type == 'organization':
            return redirect('organization_dashboard')
    role = request.user.user_type.title() if hasattr(request.user, 'user_type') else 'User'
    return render(request, 'pages/dashboard.html', {'role': role})


@login_required
def student_dashboard(request):
    if not hasattr(request.user, 'user_type') or request.user.user_type != 'student':
        return redirect('screen1')

    student = request.user

    completed_opportunities = StudentOpportunity.objects.filter(
        student=student, status='completed'
    ).select_related('opportunity', 'opportunity__organization')
    in_progress_opportunities = StudentOpportunity.objects.filter(
        student=student, status='in_progress'
    ).select_related('opportunity', 'opportunity__organization')
    pending_opportunities = StudentOpportunity.objects.filter(
        student=student, status='pending'
    ).select_related('opportunity', 'opportunity__organization')

    applications_qs = Application.objects.filter(student=student).select_related('opportunity')
    applications_count = applications_qs.count()
    applied_opportunity_ids = list(applications_qs.values_list('opportunity_id', flat=True))

    recommended_opportunities = (
        Opportunity.objects.filter(is_active=True)
        .exclude(id__in=applied_opportunity_ids)
        .select_related('organization')
        .order_by('-posted_date')[:5]
    )

    first_name = (student.first_name or student.display_name or student.email).split(' ')[0]
    initials = ''.join(part[:1] for part in (student.first_name, student.last_name) if part).upper() or first_name[:1].upper()

    context = {
        'student': student,
        'first_name': first_name,
        'initials': initials,
        'applications_count': applications_count,
        'recommended_opportunities': recommended_opportunities,
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

    org = request.user
    recent_applications = (
        Application.objects.filter(opportunity__organization=org)
        .select_related('student', 'opportunity')
        .order_by('-applied_date')[:5]
    )
    pending_count = Application.objects.filter(opportunity__organization=org, status='pending').count()
    accepted_count = Application.objects.filter(opportunity__organization=org, status='accepted').count()
    opportunities_count = Opportunity.objects.filter(organization=org, is_active=True).count()
    unread_message_count = Message.objects.filter(recipient=org, is_read=False).count()

    full = f"{org.first_name} {org.last_name}".strip()
    org_name = full if full else org.email.split('@')[0].replace('_', ' ').title()
    initials_source = full or org_name
    initials = ''.join(part[:1] for part in initials_source.split() if part)[:2].upper() or org_name[:1].upper()

    context = {
        'org': org,
        'org_name': org_name,
        'initials': initials,
        'recent_applications': recent_applications,
        'pending_count': pending_count,
        'accepted_count': accepted_count,
        'total_volunteers': accepted_count,
        'opportunities_count': opportunities_count,
        'unread_message_count': unread_message_count,
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
    is_following = False
    unread_message_count = 0
    if request.user.user_type == 'student':
        is_following = OrganizationFollow.objects.filter(student=request.user, organization=organization).exists()
    elif request.user.user_type == 'organization' and request.user.id == org_id:
        unread_message_count = Message.objects.filter(recipient=request.user, is_read=False).count()
    opportunities = Opportunity.objects.filter(organization=organization, is_active=True)
    return render(request, 'pages/organization_profile.html', {
        'organization': organization, 'is_following': is_following,
        'opportunities': opportunities, 'unread_message_count': unread_message_count,
    })


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
            'first_name': request.user.first_name, 'last_name': request.user.last_name,
            'email': request.user.email, 'phone': profile.phone, 'bio': profile.bio, 'skills': profile.skills,
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


@login_required
def student_notifications(request):
    if not hasattr(request.user, 'user_type') or request.user.user_type != 'student':
        return redirect('screen1')
    notifications = Notification.objects.filter(recipient=request.user)
    return render(request, 'pages/student_notifications.html', {'notifications': notifications})
