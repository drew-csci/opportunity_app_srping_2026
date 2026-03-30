from django.db import models
from django.conf import settings
from django.utils import timezone
from datetime import timedelta

# Create your models here.
class Achievement(models.Model):
    student = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='achievements',
        limit_choices_to={'user_type': 'student'},
    )
    title = models.CharField(max_length=200)
    description = models.TextField()
    date_completed = models.DateField()

    def __str__(self):
        return self.title


class Application(models.Model):
    """Model representing a student's application to an opportunity."""
    STATUS_CHOICES = (
        ('applied', 'Applied'),
        ('accepted', 'Accepted'),
        ('declined', 'Declined'),
    )
    
    student = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='applications',
        limit_choices_to={'user_type': 'student'},
    )
    organization = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='received_applications',
        limit_choices_to={'user_type': 'organization'},
    )
    opportunity_title = models.CharField(max_length=255)
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='applied'
    )
    applied_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    cover_letter = models.TextField(blank=True)
    
    class Meta:
        ordering = ['-applied_at']
    
    def __str__(self):
        return f"{self.student.display_name} - {self.opportunity_title} ({self.status})"
    
    @property
    def can_remind(self):
        """Check if a reminder can be sent for this application."""
        return self.status == 'applied'


class ApplicationReminder(models.Model):
    """Model to track reminders sent for applications."""
    application = models.ForeignKey(
        Application,
        on_delete=models.CASCADE,
        related_name='reminders'
    )
    sent_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='sent_reminders',
        limit_choices_to={'user_type': 'student'},
    )
    sent_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-sent_at']
    
    def __str__(self):
        return f"Reminder for {self.application} sent at {self.sent_at}"
    
    @classmethod
    def can_send_reminder(cls, application):
        """Check if a new reminder can be sent (rate limiting: max 1 per 24 hours)."""
        if not application.can_remind:
            return False
        
        # Check if a reminder was sent in the last 24 hours
        last_reminder = cls.objects.filter(
            application=application
        ).order_by('-sent_at').first()
        
        if not last_reminder:
            return True
        
        # Allow reminder if more than 24 hours have passed
        time_diff = timezone.now() - last_reminder.sent_at
        return time_diff > timedelta(hours=24)
