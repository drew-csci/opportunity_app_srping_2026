from django.db import models
from django.conf import settings

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


class Opportunity(models.Model):
    """Represents an opportunity (volunteer, internship, work, etc.) that can be posted by organizations."""
    
    class OpportunityStatus(models.TextChoices):
        OPEN = 'open', 'Open'
        CLOSED = 'closed', 'Closed'
    
    title = models.CharField(max_length=200)
    description = models.TextField()
    organization = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='posted_opportunities',
        limit_choices_to={'user_type': 'organization'},
    )
    status = models.CharField(
        max_length=20,
        choices=OpportunityStatus.choices,
        default=OpportunityStatus.OPEN
    )
    date_posted = models.DateTimeField(auto_now_add=True)
    date_updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title

    class Meta:
        ordering = ['-date_posted']


class StudentOpportunity(models.Model):
    """Tracks the relationship between a student and an opportunity, including completion status."""
    
    class CompletionStatus(models.TextChoices):
        NOT_STARTED = 'not_started', 'Not Started'
        IN_PROGRESS = 'in_progress', 'In Progress'
        COMPLETED = 'completed', 'Completed'
    
    student = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='student_opportunities',
        limit_choices_to={'user_type': 'student'},
    )
    opportunity = models.ForeignKey(
        Opportunity,
        on_delete=models.CASCADE,
        related_name='student_participants',
    )
    status = models.CharField(
        max_length=20,
        choices=CompletionStatus.choices,
        default=CompletionStatus.NOT_STARTED
    )
    date_joined = models.DateTimeField(auto_now_add=True)
    date_completed = models.DateTimeField(null=True, blank=True)

    class Meta:
        unique_together = ('student', 'opportunity')
        ordering = ['-date_completed', '-date_joined']

    def __str__(self):
        return f"{self.student.email} - {self.opportunity.title} ({self.status})"
