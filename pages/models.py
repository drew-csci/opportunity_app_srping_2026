from django.db import models
from django.conf import settings


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
        PENDING = 'pending', 'Pending Approval'
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
    date_pending = models.DateTimeField(null=True, blank=True)
    date_completed = models.DateTimeField(null=True, blank=True)
    denial_reason = models.TextField(null=True, blank=True)

    class Meta:
        unique_together = ('student', 'opportunity')
        ordering = ['-date_completed', '-date_joined']

    def __str__(self):
        return f"{self.student.email} - {self.opportunity.title} ({self.status})"


class Notification(models.Model):
    """Tracks notifications sent to users about opportunity status changes."""
    
    class NotificationType(models.TextChoices):
        COMPLETION_DENIED = 'completion_denied', 'Completion Denied'
        COMPLETION_APPROVED = 'completion_approved', 'Completion Approved'
    
    recipient = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='notifications',
    )
    notification_type = models.CharField(
        max_length=30,
        choices=NotificationType.choices,
    )
    student_opportunity = models.ForeignKey(
        StudentOpportunity,
        on_delete=models.CASCADE,
        related_name='notifications',
    )
    message = models.TextField()
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Notification to {self.recipient.email} - {self.notification_type}"


class VolunteerProfile(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='volunteer_profile',
    )
    phone = models.CharField(max_length=20, blank=True)
    bio = models.TextField(blank=True)
    skills = models.TextField(blank=True, help_text="Comma-separated list of skills")

    def __str__(self):
        return f"{self.user.display_name}'s profile"

    def skills_list(self):
        return [s.strip() for s in self.skills.split(',') if s.strip()]


class VolunteerExperience(models.Model):
    volunteer = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='volunteer_experiences',
    )
    organization_name = models.CharField(max_length=200)
    role = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    start_date = models.DateField()
    end_date = models.DateField(null=True, blank=True)
    is_current = models.BooleanField(default=False)

    class Meta:
        ordering = ['-start_date']

    def __str__(self):
        return f"{self.role} at {self.organization_name}"
    
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
