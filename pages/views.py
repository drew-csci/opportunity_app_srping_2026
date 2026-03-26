from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required

from .models import Achievement
from .forms import AchievementForm

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
