"""
Management command to create test data for messaging system
"""
from django.core.management.base import BaseCommand
from django.utils import timezone
from accounts.models import User
from pages.models import Conversation, Message


class Command(BaseCommand):
    help = 'Create test data for messaging system'

    def handle(self, *args, **options):
        # Create test users
        volunteer, created = User.objects.get_or_create(
            email='volunteer@test.com',
            defaults={
                'username': 'volunteer',
                'user_type': 'student',
                'first_name': 'Test',
                'last_name': 'Volunteer',
            }
        )

        org1, created = User.objects.get_or_create(
            email='redcross@test.com',
            defaults={
                'username': 'redcross',
                'user_type': 'organization',
                'first_name': 'Red',
                'last_name': 'Cross',
            }
        )

        org2, created = User.objects.get_or_create(
            email='foodbank@test.com',
            defaults={
                'username': 'foodbank',
                'user_type': 'organization',
                'first_name': 'Food',
                'last_name': 'Bank',
            }
        )

        # Create conversations
        conv1, _ = Conversation.objects.get_or_create(
            volunteer=volunteer,
            organization=org1,
        )

        conv2, _ = Conversation.objects.get_or_create(
            volunteer=volunteer,
            organization=org2,
        )

        # Create test messages
        Message.objects.get_or_create(
            conversation=conv1,
            sender=volunteer,
            content='Hi Red Cross! I want to volunteer.',
            defaults={'timestamp': timezone.now()}
        )

        Message.objects.get_or_create(
            conversation=conv1,
            sender=org1,
            content='Welcome! What are your interests?',
            defaults={'timestamp': timezone.now()}
        )

        Message.objects.get_or_create(
            conversation=conv2,
            sender=volunteer,
            content='Hello Food Bank! How can I help?',
            defaults={'timestamp': timezone.now()}
        )

        self.stdout.write(self.style.SUCCESS('Test data created successfully!'))
