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


class Message(models.Model):
    sender = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='sent_messages',
        limit_choices_to={'user_type': 'student'},
    )
    recipient = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='received_messages',
        limit_choices_to={'user_type': 'organization'},
    )
    subject = models.CharField(max_length=255)
    body = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.sender.display_name} to {self.recipient.display_name}: {self.subject}"
