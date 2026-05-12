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


class OrganizationProfileForm(forms.ModelForm):
    class Meta:
        model = OrganizationProfile
        fields = ['organization_name', 'mission', 'location', 'contact_info']
        widgets = {
            'mission': forms.Textarea(attrs={'rows': 4}),
            'contact_info': forms.Textarea(attrs={'rows': 3}),
        }


class OrganizationImpactMetricForm(forms.ModelForm):
    class Meta:
        model = OrganizationImpactMetric
        fields = ['title', 'value', 'description']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 3}),
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


class MessageReplyForm(forms.Form):
    """Form for replying to messages with character limit validation."""
    
    CHAR_LIMIT = 1000
    
    reply_content = forms.CharField(
        max_length=CHAR_LIMIT,
        widget=forms.Textarea(attrs={
            'rows': 5,
            'placeholder': 'Type your reply here (max 1000 characters)...',
            'class': 'form-control',
        }),
        label='Your Reply',
        help_text=f'Maximum {CHAR_LIMIT} characters',
        strip=True,
    )
    
    def clean_reply_content(self):
        """Validate the reply content."""
        content = self.cleaned_data.get('reply_content', '').strip()
        
        if not content:
            raise forms.ValidationError(
                'Please enter a message. Your reply cannot be blank.'
            )
        
        if len(content) > self.CHAR_LIMIT:
            raise forms.ValidationError(
                f'Your reply exceeds the {self.CHAR_LIMIT} character limit. '
                f'Current length: {len(content)} characters. '
                f'Please remove {len(content) - self.CHAR_LIMIT} characters.'
            )
        
        return content


class ReportForm(forms.Form):
    """Form for users to report inappropriate content."""
    
    REASON_CHOICES = [
        ('spam', 'Spam'),
        ('harassment', 'Harassment or Bullying'),
        ('misinformation', 'Misleading or False Information'),
        ('other', 'Other'),
    ]
    
    reason = forms.ChoiceField(
        choices=REASON_CHOICES,
        widget=forms.Select(attrs={
            'class': 'form-select',
        }),
        label='Reason for Report',
        help_text='Please select the reason you are reporting this content'
    )
    
    notes = forms.CharField(
        max_length=1000,
        required=False,
        widget=forms.Textarea(attrs={
            'rows': 4,
            'placeholder': 'Please provide additional details (optional)...',
            'class': 'form-control',
        }),
        label='Additional Details',
        help_text='Optional: Provide any additional context or details about your report'
    )
    
    def clean_reason(self):
        """Ensure reason is a valid choice."""
        reason = self.cleaned_data.get('reason')
        valid_reasons = [choice[0] for choice in self.REASON_CHOICES]
        if reason not in valid_reasons:
            raise forms.ValidationError('Please select a valid reason.')
        return reason
