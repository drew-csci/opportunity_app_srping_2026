from django import forms
from .models import Achievement, StudentOpportunity

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
