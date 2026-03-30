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


class Conversation(models.Model):
    """Track conversations between a volunteer and an organization"""
    volunteer = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='volunteer_conversations',
        limit_choices_to={'user_type': 'student'},
    )
    organization = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='organization_conversations',
        limit_choices_to={'user_type': 'organization'},
    )
    created_at = models.DateTimeField(auto_now_add=True)
    last_message_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('volunteer', 'organization')
        ordering = ['-last_message_at']

    def __str__(self):
        return f"{self.volunteer.display_name} <-> {self.organization.display_name}"


class Message(models.Model):
    """Store individual messages between volunteers and organizations"""
    conversation = models.ForeignKey(
        Conversation,
        on_delete=models.CASCADE,
        related_name='messages',
    )
    sender = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='sent_messages',
    )
    content = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)

    class Meta:
        ordering = ['timestamp']

    def __str__(self):
        return f"Message from {self.sender.display_name} at {self.timestamp}"


class FAQSuggestion(models.Model):
    """Store AI-generated FAQ suggestions for messages"""
    message = models.ForeignKey(
        Message,
        on_delete=models.CASCADE,
        related_name='faq_suggestions',
    )
    faq_content = models.TextField()
    relevance_score = models.FloatField(default=0.0)
    was_accepted = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-relevance_score']

    def __str__(self):
        return f"FAQ suggestion for message {self.message.id}"
