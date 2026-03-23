from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required

from .models import Achievement, VolunteerProfile, VolunteerExperience
from .forms import AchievementForm, VolunteerProfileForm, VolunteerExperienceForm

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