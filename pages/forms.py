from django import forms
from .models import Achievement, StudentOpportunity, VolunteerProfile, VolunteerExperience, Opportunity
from .models import Achievement, Application
from .models import VolunteerProfile, VolunteerExperience
from datetime import date


class OpportunityForm(forms.ModelForm):
    """
    Form for creating and editing volunteer/internship opportunities.
    Reusable for both organization posting and editing existing opportunities.
    """
    application_deadline = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={'type': 'date'}),
        help_text='When students must submit their applications'
    )
    
    class Meta:
        model = Opportunity
        fields = ['title', 'description', 'required_skills', 'location', 'opportunity_type', 
                  'duration', 'status', 'application_deadline']
        widgets = {
            'title': forms.TextInput(attrs={
                'placeholder': 'E.g., Summer Volunteer Program Manager',
                'class': 'form-control',
            }),
            'description': forms.Textarea(attrs={
                'rows': 6,
                'placeholder': 'Describe the role, responsibilities, and what success looks like...',
                'class': 'form-control',
            }),
            'required_skills': forms.Textarea(attrs={
                'rows': 4,
                'placeholder': 'E.g., Communication, Project Management, Teamwork',
                'class': 'form-control',
            }),
            'location': forms.TextInput(attrs={
                'placeholder': 'E.g., San Francisco, CA or Remote',
                'class': 'form-control',
            }),
            'opportunity_type': forms.TextInput(attrs={
                'placeholder': 'E.g., Volunteer, Internship, Fellowship',
                'class': 'form-control',
            }),
            'duration': forms.TextInput(attrs={
                'placeholder': 'E.g., 3 months, Summer 2026, Ongoing',
                'class': 'form-control',
            }),
            'status': forms.Select(attrs={
                'class': 'form-control',
            }),
        }
        labels = {
            'title': 'Opportunity Title',
            'description': 'Description',
            'required_skills': 'Required Skills',
            'location': 'Location',
            'opportunity_type': 'Opportunity Type',
            'duration': 'Duration',
            'status': 'Status',
            'application_deadline': 'Application Deadline',
        }
    
    def clean_application_deadline(self):
        """Validate that application deadline is not in the past."""
        deadline = self.cleaned_data.get('application_deadline')
        if deadline and deadline < date.today():
            raise forms.ValidationError('Application deadline cannot be in the past.')
        return deadline
    
    def clean_required_skills(self):
        """Ensure required_skills is filled."""
        required_skills = self.cleaned_data.get('required_skills')
        if not required_skills or not required_skills.strip():
            raise forms.ValidationError('Please specify the required skills or qualifications.')
        return required_skills


class AchievementForm(forms.ModelForm):
    class Meta:
        model = Achievement
        fields = ['title', 'description', 'date_completed']
        widgets = {
            'date_completed': forms.DateInput(attrs={'type': 'date'}),
        }

class MarkOpportunityPendingForm(forms.ModelForm):
    """Form for students to mark an in-progress opportunity as pending completion."""
    
    class Meta:
        model = StudentOpportunity
        fields = ['status']
        widgets = {
            'status': forms.HiddenInput(),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Only allow transitioning to pending status
        if self.instance:
            self.fields['status'].initial = 'pending'
    
    def clean(self):
        cleaned_data = super().clean()
        # Validate that the current status is in_progress
        if self.instance and self.instance.status != 'in_progress':
            raise forms.ValidationError(
                "Only opportunities that are 'In Progress' can be marked as pending."
            )
        return cleaned_data


class DenyOpportunityForm(forms.Form):
    """Form for organizations to deny a pending opportunity completion."""
    
    denial_reason = forms.CharField(
        label='Reason for Denial',
        widget=forms.Textarea(attrs={
            'rows': 5,
            'placeholder': 'Please provide feedback on why this opportunity completion was not approved...',
            'class': 'form-control',
        }),
        required=True,
        max_length=1000,
        help_text='This feedback will be sent to the student.'
    )
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
