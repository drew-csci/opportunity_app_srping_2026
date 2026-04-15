from django import forms
from django.utils import timezone

from .models import Achievement, Opportunity

class AchievementForm(forms.ModelForm):
    class Meta:
        model = Achievement
        fields = ['title', 'description', 'date_completed']
        widgets = {
            'date_completed': forms.DateInput(attrs={'type': 'date'}),
        }


class OpportunityForm(forms.ModelForm):
    class Meta:
        model = Opportunity
        fields = [
            'title',
            'category',
            'opportunity_type',
            'description',
            'required_skills',
            'location',
            'duration',
            'hours_per_week',
            'application_deadline',
        ]
        widgets = {
            'title': forms.TextInput(attrs={
                'placeholder': 'Community Outreach Intern',
            }),
            'category': forms.TextInput(attrs={
                'placeholder': 'Education, Healthcare, Environment...',
            }),
            'description': forms.Textarea(attrs={
                'rows': 5,
                'placeholder': 'Describe the role, responsibilities, and what volunteers or interns will work on.',
            }),
            'required_skills': forms.Textarea(attrs={
                'rows': 4,
                'placeholder': 'Communication, event planning, Excel, social media, bilingual Spanish...',
            }),
            'location': forms.TextInput(attrs={
                'placeholder': 'Madison, NJ or Remote',
            }),
            'hours_per_week': forms.NumberInput(attrs={
                'min': '1',
                'placeholder': '10',
            }),
            'application_deadline': forms.DateInput(attrs={'type': 'date'}),
        }
        labels = {
            'category': 'Category / Focus Area',
            'required_skills': 'Required Skills',
            'hours_per_week': 'Hours Per Week',
            'application_deadline': 'Application Deadline',
        }
        help_texts = {
            'required_skills': 'List the skills, experience, or qualifications applicants should have.',
            'hours_per_week': 'Optional for one-time roles; recommended for recurring opportunities.',
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['required_skills'].required = True
        self.fields['application_deadline'].required = True

    def clean_application_deadline(self):
        deadline = self.cleaned_data.get('application_deadline')
        if deadline and deadline < timezone.localdate():
            raise forms.ValidationError('Application deadline cannot be in the past.')
        return deadline

    def clean_hours_per_week(self):
        hours = self.cleaned_data.get('hours_per_week')
        if hours is not None and hours <= 0:
            raise forms.ValidationError('Hours per week must be greater than zero.')
        return hours

    def clean_required_skills(self):
        required_skills = self.cleaned_data.get('required_skills', '').strip()
        if not required_skills:
            raise forms.ValidationError('Please provide the required skills for this opportunity.')
        return required_skills
