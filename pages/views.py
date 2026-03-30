from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required

from .models import Achievement, StudentOpportunity, Opportunity
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

    context = {
        'completed_opportunities': completed_opportunities,
        'in_progress_opportunities': in_progress_opportunities,
        'completed_count': completed_opportunities.count(),
    }

    return render(request, 'pages/student_dashboard.html', context)
