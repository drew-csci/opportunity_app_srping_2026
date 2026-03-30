from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.db.models import Q

from .models import Achievement, Opportunity
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
