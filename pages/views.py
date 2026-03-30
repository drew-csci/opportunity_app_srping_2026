from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages

from .models import Achievement, Message
from .forms import AchievementForm, MessageForm

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


@login_required
def send_message(request):
    """View for students to send messages to organizations."""
    if not hasattr(request.user, 'user_type') or request.user.user_type != 'student':
        # Redirect non-students
        return redirect('screen1')

    if request.method == 'POST':
        form = MessageForm(request.POST)
        if form.is_valid():
            message = form.save(commit=False)
            message.sender = request.user
            message.save()
            messages.success(request, 'Message sent successfully!')
            return redirect('send_message')
    else:
        form = MessageForm()

    return render(request, 'pages/send_message.html', {'form': form})


@login_required
def organization_inbox(request):
    """View for organizations to see messages sent by students."""
    if not hasattr(request.user, 'user_type') or request.user.user_type != 'organization':
        # Redirect non-organizations
        return redirect('screen1')

    # Get all messages sent to this organization, ordered by newest first
    inbox_messages = Message.objects.filter(recipient=request.user)
    message_count = inbox_messages.count()

    return render(request, 'pages/inbox.html', {
        'messages': inbox_messages,
        'message_count': message_count,
    })


@login_required
def message_detail(request, pk):
    """View for organizations to see full message details."""
    if not hasattr(request.user, 'user_type') or request.user.user_type != 'organization':
        # Redirect non-organizations
        return redirect('screen1')

    message = Message.objects.get(pk=pk, recipient=request.user)
    
    return render(request, 'pages/message_detail.html', {'message': message})


def faq(request):
    return render(request, 'pages/faq.html')

def dashboard(request):
    return render(request, 'pages/dashboard.html')
