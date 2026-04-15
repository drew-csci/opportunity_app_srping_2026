from django import forms
from .models import Achievement, Application, Message
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
        
        # Check if field is empty
        if not content:
            raise forms.ValidationError(
                'Please enter a message. Your reply cannot be blank.'
            )
        
        # Check character limit
        if len(content) > self.CHAR_LIMIT:
            raise forms.ValidationError(
                f'Your reply exceeds the {self.CHAR_LIMIT} character limit. '
                f'Current length: {len(content)} characters. '
                f'Please remove {len(content) - self.CHAR_LIMIT} characters.'
            )
        
        return content
