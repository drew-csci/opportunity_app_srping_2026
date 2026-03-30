"""
Management command to seed test data for opportunities and student-opportunity relationships.

Usage:
    python manage.py seed_opportunities
"""

from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta
from pages.models import Opportunity, StudentOpportunity
from accounts.models import User


class Command(BaseCommand):
    help = 'Seed test data for opportunities and student-opportunity relationships'

    def add_arguments(self, parser):
        parser.add_argument(
            '--clear',
            action='store_true',
            help='Clear all existing opportunities and student_opportunity records before seeding',
        )

    def handle(self, *args, **options):
        if options['clear']:
            self.stdout.write('Clearing existing data...')
            StudentOpportunity.objects.all().delete()
            Opportunity.objects.all().delete()
            self.stdout.write(self.style.SUCCESS('✓ Data cleared'))

        # Get or create sample organization users
        org1, _ = User.objects.get_or_create(
            email='nonprofit@example.com',
            defaults={
                'username': 'nonprofit',
                'first_name': 'Non',
                'last_name': 'Profit',
                'user_type': 'organization'
            }
        )

        org2, _ = User.objects.get_or_create(
            email='tech-company@example.com',
            defaults={
                'username': 'techcompany',
                'first_name': 'Tech',
                'last_name': 'Company',
                'user_type': 'organization'
            }
        )

        # Get or create sample student users
        student1, _ = User.objects.get_or_create(
            email='student1@example.com',
            defaults={
                'username': 'student1',
                'first_name': 'John',
                'last_name': 'Doe',
                'user_type': 'student'
            }
        )

        student2, _ = User.objects.get_or_create(
            email='student2@example.com',
            defaults={
                'username': 'student2',
                'first_name': 'Jane',
                'last_name': 'Smith',
                'user_type': 'student'
            }
        )

        # Create sample opportunities
        opp1, created1 = Opportunity.objects.get_or_create(
            title='Summer Volunteer Program',
            organization=org1,
            defaults={
                'description': 'Join us for a meaningful summer volunteer experience helping underprivileged communities.',
                'status': 'open',
            }
        )

        opp2, created2 = Opportunity.objects.get_or_create(
            title='Tech Internship 2026',
            organization=org2,
            defaults={
                'description': 'Exciting internship opportunity for students interested in software development and cloud technologies.',
                'status': 'open',
            }
        )

        opp3, created3 = Opportunity.objects.get_or_create(
            title='Community Leadership Program',
            organization=org1,
            defaults={
                'description': 'Develop leadership skills while making a positive impact in your community.',
                'status': 'open',
            }
        )

        # Create student-opportunity relationships with various statuses
        now = timezone.now()

        # Student 1: has completed opportunities
        student_opp1, created = StudentOpportunity.objects.get_or_create(
            student=student1,
            opportunity=opp1,
            defaults={
                'status': 'completed',
                'date_joined': now - timedelta(days=90),
                'date_completed': now - timedelta(days=30),
            }
        )

        student_opp2, created = StudentOpportunity.objects.get_or_create(
            student=student1,
            opportunity=opp2,
            defaults={
                'status': 'in_progress',
                'date_joined': now - timedelta(days=14),
                'date_completed': None,
            }
        )

        # Student 2: has completed opportunities
        student_opp3, created = StudentOpportunity.objects.get_or_create(
            student=student2,
            opportunity=opp3,
            defaults={
                'status': 'completed',
                'date_joined': now - timedelta(days=60),
                'date_completed': now - timedelta(days=15),
            }
        )

        student_opp4, created = StudentOpportunity.objects.get_or_create(
            student=student2,
            opportunity=opp1,
            defaults={
                'status': 'completed',
                'date_joined': now - timedelta(days=120),
                'date_completed': now - timedelta(days=45),
            }
        )

        self.stdout.write(self.style.SUCCESS('✓ Successfully created:'))
        self.stdout.write(f'  - {2} organizations')
        self.stdout.write(f'  - {2} students')
        self.stdout.write(f'  - {3} opportunities')
        self.stdout.write(f'  - {4} student-opportunity relationships')
        self.stdout.write('')
        self.stdout.write('Sample data ready! You can now:')
        self.stdout.write(f'  1. Log in as student1@example.com to see completed opportunities')
        self.stdout.write(f'  2. Navigate to /student-dashboard/ to view the student dashboard')
        self.stdout.write(f'  3. Use Django admin to manage opportunities')
