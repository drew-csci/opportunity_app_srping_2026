from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.db.models import Q

from .models import Achievement, Message, MessageReply
from .forms import AchievementForm, MessageForm, MessageReplyForm

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


# Messaging Views
@login_required
def organization_inbox(request):
    if not hasattr(request.user, 'user_type') or request.user.user_type != 'organization':
        return redirect('screen1')
    
    messages = Message.objects.filter(recipient=request.user).order_by('-created_at')
    unread_count = messages.filter(is_read=False).count()
    
    return render(request, 'pages/inbox.html', {
        'messages': messages,
        'unread_count': unread_count,
    })


@login_required
def message_detail(request, message_id):
    message = get_object_or_404(Message, id=message_id, recipient=request.user)
    
    if not message.is_read:
        message.is_read = True
        message.save()
    
    if request.method == 'POST':
        form = MessageReplyForm(request.POST)
        if form.is_valid():
            reply = form.save(commit=False)
            reply.message = message
            reply.sender = request.user
            reply.save()
            return redirect('message_detail', message_id=message.id)
    else:
        form = MessageReplyForm()
    
    replies = message.replies.all()
    
    return render(request, 'pages/message_detail.html', {
        'message': message,
        'replies': replies,
        'form': form,
    })


@login_required
def send_message(request, recipient_id):
    if not hasattr(request.user, 'user_type') or request.user.user_type != 'student':
        return redirect('screen1')
    
    from accounts.models import User
    recipient = get_object_or_404(User, id=recipient_id, user_type='organization')
    
    if request.method == 'POST':
        form = MessageForm(request.POST)
        if form.is_valid():
            message = form.save(commit=False)
            message.sender = request.user
            message.recipient = recipient
            message.save()
            return redirect('message_sent_success')
    else:
        form = MessageForm()
    
    return render(request, 'pages/send_message.html', {
        'recipient': recipient,
        'form': form,
    })


@login_required
def message_sent_success(request):
    if not hasattr(request.user, 'user_type') or request.user.user_type != 'student':
        return redirect('screen1')
    
    return render(request, 'pages/message_sent_success.html')


@login_required
@require_http_methods(["POST"])
def mark_message_read(request, message_id):
    message = get_object_or_404(Message, id=message_id, recipient=request.user)
    message.is_read = True
    message.save()
    
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({'status': 'success'})
    
    return redirect('organization_inbox')


@login_required
def get_unread_count(request):
    if hasattr(request.user, 'user_type') and request.user.user_type == 'organization':
        unread_count = Message.objects.filter(recipient=request.user, is_read=False).count()
        return JsonResponse({'unread_count': unread_count})
    
    return JsonResponse({'unread_count': 0})
