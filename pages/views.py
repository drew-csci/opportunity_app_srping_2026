from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.http import JsonResponse

from accounts.models import User
from .models import Achievement, Opportunity, OrganizationFollow
from .forms import AchievementForm


def welcome(request):
    return render(request, 'pages/welcome.html')


@login_required
def screen1(request):
    role = request.user.user_type.title() if hasattr(request.user, 'user_type') else 'User'

    opportunities = Opportunity.objects.filter(is_active=True)

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
            Q(skills_required__icontains=query)
        )
    if location:
        opportunities = opportunities.filter(location__icontains=location)
    if cause:
        opportunities = opportunities.filter(cause__icontains=cause)
    if duration:
        opportunities = opportunities.filter(duration__icontains=duration)
    if skills:
        opportunities = opportunities.filter(skills_required__icontains=skills)
    if opp_type:
        opportunities = opportunities.filter(opportunity_type=opp_type)

    context = {
        'role': role,
        'opportunities': opportunities,
        'query': query,
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


@login_required
def organization_profile(request, org_id):
    """Display an organization's profile with follow/unfollow button and opportunities."""
    organization = get_object_or_404(User, id=org_id, user_type='organization')
    is_following = False

    if request.user.user_type == 'student':
        is_following = OrganizationFollow.objects.filter(
            student=request.user,
            organization=organization,
        ).exists()

    # TODO: Query opportunities when Opportunity model is added
    opportunities = []

    return render(request, 'pages/organization_profile.html', {
        'organization': organization,
        'is_following': is_following,
        'opportunities': opportunities,
    })


@login_required
def follow_organization(request, org_id):
    """Follow an organization. Supports both regular POST and AJAX requests."""
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