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


class Opportunity(models.Model): # New model for volunteer opportunities
    organization = models.ForeignKey(  # Foreign key to the User model to link each opportunity to a specific organization
        settings.AUTH_USER_MODEL, 
        on_delete=models.CASCADE, # Delete all related opportunities if the organization is deleted
        related_name='opportunities', # Allow reverse access to opportunities from the organization user model
        limit_choices_to={'user_type': 'organization'} # Limit the choices in the admin interface to only users with user_type 'organization'
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


class Application(models.Model): # New model for student applications to volunteer opportunities
    class Status(models.TextChoices):
        DRAFT = 'draft', 'Draft'
        PENDING = 'pending', 'Pending'
        ACCEPTED = 'accepted', 'Accepted'
        DENIED = 'denied', 'Denied'

    student = models.ForeignKey( # Foreign key to the User model to link each application to a specific student
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='applications',
        limit_choices_to={'user_type': 'student'}
    )
    opportunity = models.ForeignKey( # Foreign key to the Opportunity model to link each application to a specific volunteer opportunity
        Opportunity,
        on_delete=models.CASCADE,
        related_name='applications'
    )
    status = models.CharField( # Status field to track the application status with predefined choices
        max_length=20,
        choices=Status.choices,
        default=Status.DRAFT
    )
    applied_date = models.DateTimeField(auto_now_add=True) # Timestamp when the application is created
    responded_date = models.DateTimeField(null=True, blank=True) # Timestamp when the application is accepted or denied
    message = models.TextField() # Optional message from the student explaining their interest in the opportunity

    class Meta: # Order applications by most recent applied date first
        ordering = ['-applied_date']

    def save(self, *args, **kwargs): # Automatically set the responded_date when the status changes to accepted or denied
        if self.status in (self.Status.ACCEPTED, self.Status.DENIED) and self.responded_date is None:  
            self.responded_date = timezone.now()
        super().save(*args, **kwargs) # Call the original save method to save the instance

    def __str__(self): # Return a string representation of the application showing the student's name, opportunity title, and current status
        return f'{self.student.display_name} — {self.opportunity.title} ({self.get_status_display()})'
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