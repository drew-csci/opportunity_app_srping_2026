from django.db import models
from django.conf import settings
from django.utils import timezone


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


class Opportunity(models.Model):
    """Model for job/volunteer opportunities posted by organizations"""
    OPPORTUNITY_TYPES = [
        ('volunteer', 'Volunteer'),
        ('internship', 'Internship'),
        ('job', 'Job'),
    ]
    
    DURATION_CHOICES = [
        ('one-time', 'One-time'),
        ('recurring', 'Recurring'),
    ]
    
    organization = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='posted_opportunities',
        limit_choices_to={'user_type': 'organization'},
    )
    title = models.CharField(max_length=200)
    description = models.TextField()
    category = models.CharField(max_length=50)
    opportunity_type = models.CharField(max_length=20, choices=OPPORTUNITY_TYPES, default='volunteer')
    location = models.CharField(max_length=200)
    duration = models.CharField(max_length=20, choices=DURATION_CHOICES, default='one-time')
    hours_per_week = models.IntegerField(null=True, blank=True)
    posted_date = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)
    
    class Meta:
        ordering = ['-posted_date']
    
    def __str__(self):
        return f"{self.title} - {self.organization.display_name}"


class Application(models.Model):
    """Model for student applications to opportunities"""
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('accepted', 'Accepted'),
        ('declined', 'Declined'),
    ]
    
    student = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='applications',
        limit_choices_to={'user_type': 'student'},
    )
    opportunity = models.ForeignKey(
        Opportunity,
        on_delete=models.CASCADE,
        related_name='applications',
    )
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    applied_date = models.DateTimeField(auto_now_add=True)
    responded_date = models.DateTimeField(null=True, blank=True)
    message = models.TextField(blank=True, help_text="Student's application message")
    
    class Meta:
        ordering = ['-applied_date']
        unique_together = ('student', 'opportunity')  # Prevent duplicate applications
    
    def __str__(self):
        return f"{self.student.display_name} - {self.opportunity.title} ({self.status})"
class OrganizationFollow(models.Model):
    student = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='following',
        limit_choices_to={'user_type': 'student'},
    )
    organization = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='followers',
        limit_choices_to={'user_type': 'organization'},
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('student', 'organization')

    def __str__(self):
        return f"{self.student} follows {self.organization}"
