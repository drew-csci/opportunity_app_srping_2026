from django import forms
from .models import Achievement, Application

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
