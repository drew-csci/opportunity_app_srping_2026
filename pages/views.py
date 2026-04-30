from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse, HttpResponseForbidden
from django.utils import timezone
from django.views.decorators.http import require_http_methods

from accounts.models import User

from .models import Achievement, StudentOpportunity, Opportunity, OrganizationFollow, Notification, VolunteerProfile, VolunteerExperience
from .forms import AchievementForm, MarkOpportunityPendingForm, DenyOpportunityForm, VolunteerProfileForm, VolunteerExperienceForm
from django.contrib.auth import get_user_model
from django.contrib import messages
from django.utils import timezone
from .models import Achievement, Opportunity, Application, VolunteerProfile, VolunteerExperience, OrganizationFollow, Message
from .forms import AchievementForm, ApplicationForm, VolunteerProfileForm, VolunteerExperienceForm, MessageReplyForm
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
    context = {}
    
    # If user is an organization, add unread message count
    if hasattr(request.user, 'user_type') and request.user.user_type == 'organization':
        unread_count = Message.objects.filter(recipient=request.user, is_read=False).count()
        context['unread_message_count'] = unread_count
    
    return render(request, 'pages/dashboard.html', context)


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
    """Display an organization's profile with follow/unfollow button and opportunities."""
    organization = get_object_or_404(User, id=org_id, user_type='organization')
    is_following = False
    unread_message_count = 0

    if request.user.user_type == 'student':
        is_following = OrganizationFollow.objects.filter(
            student=request.user,
            organization=organization,
        ).exists()
    elif request.user.user_type == 'organization' and request.user.id == org_id:
        # If organization is viewing their own profile, show unread message count
        unread_message_count = Message.objects.filter(recipient=request.user, is_read=False).count()

    # TODO: Query opportunities when Opportunity model is added
    opportunities = []

    return render(request, 'pages/organization_profile.html', {
        'organization': organization,
        'is_following': is_following,
        'opportunities': opportunities,
        'unread_message_count': unread_message_count,
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
def current_volunteers_list(request):
    """
    Display all current active volunteers (accepted applications) for an organization's opportunities.
    Only accessible to users with 'organization' user type.
    Supports filtering by opportunity.
    """
    # Verify the user is an organization
    if not hasattr(request.user, 'user_type') or request.user.user_type != 'organization':
        return redirect('screen1')

    # Get all opportunities posted by this organization
    opportunities = Opportunity.objects.filter(organization=request.user).order_by('-created_at')

    # Get all accepted applications for this organization's opportunities
    volunteers_query = Application.objects.filter(
        opportunity__organization=request.user,
        status=Application.Status.ACCEPTED
    ).select_related('student', 'opportunity').order_by('-responded_date')

    # Filter by opportunity if provided
    selected_opportunity_id = request.GET.get('opportunity')
    if selected_opportunity_id:
        try:
            volunteers_query = volunteers_query.filter(opportunity_id=selected_opportunity_id)
        except (ValueError, TypeError):
            pass

    context = {
        'volunteers': volunteers_query,
        'opportunities': opportunities,
        'selected_opportunity_id': selected_opportunity_id,
        'volunteers_count': volunteers_query.count(),
    }

    return render(request, 'pages/current_volunteers_list.html', context)


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


@login_required
def organization_inbox(request):
    """Display inbox for organizations to see messages from volunteers, sorted by most recent."""
    if not hasattr(request.user, 'user_type') or request.user.user_type != 'organization':
        return redirect('screen1')

    # Get all messages received by this organization, ordered by most recent first
    inbox_messages = Message.objects.filter(recipient=request.user).select_related('sender').order_by('-sent_at')

    return render(request, 'pages/organization_inbox.html', {
        'messages': inbox_messages,
    })


@login_required
def message_detail(request, message_id):
    """Display a specific message and handle replies with character limit validation."""
    if not hasattr(request.user, 'user_type') or request.user.user_type != 'organization':
        return redirect('screen1')

    message = get_object_or_404(Message, id=message_id, recipient=request.user)
    
    # Mark message as read (using the model method that sets read_at timestamp)
    message.mark_as_read()
    
    # Get all replies to this message
    replies = message.replies.all().select_related('sender', 'recipient').order_by('sent_at')
    
    # Handle reply submission
    if request.method == 'POST':
        form = MessageReplyForm(request.POST)
        if form.is_valid():
            try:
                # Create a new reply message
                reply = Message.objects.create(
                    sender=request.user,  # Organization is sending the reply
                    recipient=message.sender,  # Reply goes back to the volunteer
                    subject=f"Re: {message.subject}",
                    content=form.cleaned_data['reply_content'],
                    reply_to=message,  # Link to the original message
                )
                messages.success(request, 'Your reply has been sent successfully!')
                return redirect('message_detail', message_id=message_id)
            except Exception as e:
                messages.error(request, f'There was an error sending your reply: {str(e)}')
        else:
            # Display form errors
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, str(error))
    else:
        form = MessageReplyForm()

    return render(request, 'pages/message_detail.html', {
        'message': message,
        'replies': replies,
        'form': form,
    })


@login_required
def volunteer_sent_messages(request):
    """Display all messages sent by a volunteer (student) with read receipt status."""
    if not hasattr(request.user, 'user_type') or request.user.user_type != 'student':
        return redirect('screen1')

    # Get all messages sent by this student, ordered by most recent first
    sent_messages = Message.objects.filter(sender=request.user).select_related('recipient').order_by('-sent_at')

    return render(request, 'pages/volunteer_sent_messages.html', {
        'messages': sent_messages,
    })


@login_required
def volunteer_sent_message_detail(request, message_id):
    """Display a sent message with read receipt information and any replies for a volunteer."""
    if not hasattr(request.user, 'user_type') or request.user.user_type != 'student':
        return redirect('screen1')

    message = get_object_or_404(Message, id=message_id, sender=request.user)
    
    # Get all replies to this message
    replies = message.replies.all().select_related('sender', 'recipient').order_by('sent_at')

    return render(request, 'pages/volunteer_sent_message_detail.html', {
        'message': message,
        'replies': replies,
    })
