from django import forms
from .models import Achievement, Application
from .models import VolunteerProfile, VolunteerExperience


class AchievementForm(forms.ModelForm):
    class Meta:
        model = Achievement
        fields = ['title', 'description', 'date_completed']
        widgets = {
            'date_completed': forms.DateInput(attrs={'type': 'date'}),
        }

class ApplicationForm(forms.ModelForm):
    class Meta:
        model = Application
        fields = ['message']
        labels = {
            'message': 'Application details',
        }
        widgets = {
            'message': forms.Textarea(attrs={'rows': 6}),
        }


class VolunteerProfileForm(forms.Form):
    first_name = forms.CharField(max_length=150, label="First name")
    last_name = forms.CharField(max_length=150, label="Last name")
    email = forms.EmailField(label="Email")
    phone = forms.CharField(max_length=20, required=False, label="Phone number")
    bio = forms.CharField(
        widget=forms.Textarea(attrs={'rows': 3}),
        required=False,
        label="Bio",
    )
    skills = forms.CharField(
        required=False,
        label="Skills",
        help_text="Comma-separated, e.g. Tutoring, Communicative, Fundraising",
    )


class VolunteerExperienceForm(forms.ModelForm):
    class Meta:
        model = VolunteerExperience
        fields = ['organization_name', 'role', 'description', 'start_date', 'end_date', 'is_current']
        labels = {
            'organization_name': 'Organization name',
            'role': 'Your role / title',
            'description': 'Description',
            'start_date': 'Start date',
            'end_date': 'End date',
            'is_current': 'I currently volunteer here',
        }
        widgets = {
            'start_date': forms.DateInput(attrs={'type': 'date'}),
            'end_date': forms.DateInput(attrs={'type': 'date'}),
            'description': forms.Textarea(attrs={'rows': 3}),
        }
