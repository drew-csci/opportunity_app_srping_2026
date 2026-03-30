from django.conf import settings
from django.db import models
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
    organization = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='opportunities',
        limit_choices_to={'user_type': 'organization'}
    )
    title = models.CharField(max_length=200)
    description = models.TextField()
    cause = models.CharField(max_length=200)
    location = models.CharField(max_length=200)
    duration = models.CharField(max_length=200)
    skills_required = models.TextField()
    opportunity_type = models.CharField(max_length=200)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.title


class Application(models.Model):
    class Status(models.TextChoices):
        DRAFT = 'draft', 'Draft'
        PENDING = 'pending', 'Pending'
        ACCEPTED = 'accepted', 'Accepted'
        DENIED = 'denied', 'Denied'

    student = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='applications',
        limit_choices_to={'user_type': 'student'}
    )
    opportunity = models.ForeignKey(
        Opportunity,
        on_delete=models.CASCADE,
        related_name='applications'
    )
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.DRAFT
    )
    applied_date = models.DateTimeField(auto_now_add=True)
    responded_date = models.DateTimeField(null=True, blank=True)
    message = models.TextField()

    class Meta:
        ordering = ['-applied_date']

    def save(self, *args, **kwargs):
        if self.status in (self.Status.ACCEPTED, self.Status.DENIED) and self.responded_date is None:
            self.responded_date = timezone.now()
        super().save(*args, **kwargs)

    def __str__(self):
        return f'{self.student.display_name} — {self.opportunity.title} ({self.get_status_display()})'
