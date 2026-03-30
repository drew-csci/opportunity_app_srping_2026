from django import forms
from .models import Achievement, Message
from django.conf import settings

class AchievementForm(forms.ModelForm):
    class Meta:
        model = Achievement
        fields = ['title', 'description', 'date_completed']
        widgets = {
            'date_completed': forms.DateInput(attrs={'type': 'date'}),
        }


class MessageForm(forms.ModelForm):
    class Meta:
        model = Message
        fields = ['recipient', 'subject', 'body']
        widgets = {
            'recipient': forms.Select(attrs={'class': 'form-control'}),
            'subject': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Message subject'}),
            'body': forms.Textarea(attrs={'class': 'form-control', 'rows': 5, 'placeholder': 'Message body'}),
        }
        labels = {
            'recipient': 'Send to Organization',
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Set the queryset to only organizations
        from accounts.models import User
        self.fields['recipient'].queryset = User.objects.filter(user_type='organization')
