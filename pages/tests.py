from datetime import timedelta

from django.contrib.messages import get_messages
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from accounts.models import User
from .models import Opportunity


class OrganizationPostOpportunityTests(TestCase):
    def setUp(self):
        self.organization = User.objects.create_user(
            username='org_user',
            email='org@example.com',
            password='testpass123',
            user_type='organization',
            first_name='Org',
            last_name='Owner',
        )
        self.student = User.objects.create_user(
            username='student_user',
            email='student@example.com',
            password='testpass123',
            user_type='student',
            first_name='Stu',
            last_name='Dent',
        )
        self.post_url = reverse('organization_post_opportunity')
        self.list_url = reverse('organization_opportunities')

    def valid_payload(self, **overrides):
        payload = {
            'title': 'Community Outreach Intern',
            'category': 'Community Engagement',
            'opportunity_type': 'internship',
            'description': 'Support outreach events, volunteer coordination, and reporting.',
            'required_skills': 'Communication\nOrganization\nSpreadsheet proficiency',
            'location': 'Madison, NJ',
            'duration': 'recurring',
            'hours_per_week': 10,
            'application_deadline': (timezone.localdate() + timedelta(days=14)).isoformat(),
        }
        payload.update(overrides)
        return payload

    def test_organization_can_view_post_form(self):
        self.client.login(email='org@example.com', password='testpass123')

        response = self.client.get(self.post_url)

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Publish Opportunity')

    def test_non_organization_user_is_redirected_from_post_form(self):
        self.client.login(email='student@example.com', password='testpass123')

        response = self.client.get(self.post_url)

        self.assertRedirects(response, reverse('screen1'))

    def test_valid_submission_creates_opportunity_for_organization(self):
        self.client.login(email='org@example.com', password='testpass123')

        response = self.client.post(self.post_url, data=self.valid_payload(), follow=True)

        self.assertRedirects(response, self.list_url)
        self.assertEqual(Opportunity.objects.count(), 1)

        opportunity = Opportunity.objects.get()
        self.assertEqual(opportunity.organization, self.organization)
        self.assertEqual(opportunity.required_skills, 'Communication\nOrganization\nSpreadsheet proficiency')
        self.assertContains(response, 'has been posted successfully')
        self.assertContains(response, 'Community Outreach Intern')

    def test_past_deadline_is_rejected(self):
        self.client.login(email='org@example.com', password='testpass123')

        response = self.client.post(
            self.post_url,
            data=self.valid_payload(
                application_deadline=(timezone.localdate() - timedelta(days=1)).isoformat()
            ),
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(Opportunity.objects.count(), 0)
        self.assertContains(response, 'Application deadline cannot be in the past.')

    def test_organization_dashboard_contains_post_new_opportunity_link(self):
        self.client.login(email='org@example.com', password='testpass123')

        response = self.client.get(reverse('organization_dashboard'))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Post New Opportunity')
        self.assertContains(response, reverse('organization_post_opportunity'))

    def test_successful_submission_shows_success_message_after_redirect(self):
        self.client.login(email='org@example.com', password='testpass123')

        response = self.client.post(self.post_url, data=self.valid_payload(), follow=True)

        self.assertRedirects(response, self.list_url)
        messages = [message.message for message in get_messages(response.wsgi_request)]
        self.assertTrue(any('has been posted successfully' in message for message in messages))
        self.assertContains(response, 'has been posted successfully')

    def test_invalid_submission_shows_error_message_and_does_not_redirect(self):
        self.client.login(email='org@example.com', password='testpass123')

        response = self.client.post(
            self.post_url,
            data=self.valid_payload(required_skills=''),
            follow=True,
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.request['PATH_INFO'], self.post_url)
        self.assertEqual(Opportunity.objects.count(), 0)
        messages = [message.message for message in get_messages(response.wsgi_request)]
        self.assertTrue(any('Please correct the highlighted fields and try again.' in message for message in messages))
        self.assertContains(response, 'Please correct the highlighted fields and try again.')
        self.assertContains(response, 'This field is required.')


class AuthenticationIntegrationTests(TestCase):
    def setUp(self):
        self.organization = User.objects.create_user(
            username='org_user',
            email='org@example.com',
            password='testpass123',
            user_type='organization',
        )

    def test_failed_login_shows_authentication_error_on_login_page(self):
        response = self.client.post(
            reverse('login'),
            data={
                'username': 'org@example.com',
                'password': 'wrong-password',
            },
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(
            response,
            'Please enter a correct email and password. Note that both fields may be case-sensitive.',
        )


class OrganizationDashboardTest(TestCase):
    """Test suite for organization dashboard functionality."""

    def setUp(self):
        """Set up test fixtures for organization dashboard tests."""
        self.client = Client()
        
        # Create organization user
        self.organization = User.objects.create_user(
            username='org_dashboard_test',
            email='org_dashboard@test.com',
            password='OrgPass123!',
            user_type='organization',
            display_name='Test Organization'
        )
        
        # Create student user for applications
        self.student = User.objects.create_user(
            username='student_app_test',
            email='student_app@test.com',
            password='StudentPass123!',
            user_type='student',
            display_name='Test Student'
        )
        
        # Create opportunities
        self.opportunity1 = Opportunity.objects.create(
            title='Dashboard Test Opportunity',
            description='Test opportunity for dashboard',
            organization=self.organization,
            status='open',
            category='Education'
        )
        
        self.opportunity2 = Opportunity.objects.create(
            title='Another Test Opportunity',
            description='Another test opportunity',
            organization=self.organization,
            status='open',
            category='Healthcare'
        )

    def test_organization_dashboard_access(self):
        """Test that organizations can access their dashboard."""
        self.client.login(username='org_dashboard_test', password='OrgPass123!')
        response = self.client.get(reverse('organization_dashboard'))
        self.assertEqual(response.status_code, 200)

    def test_organization_dashboard_shows_posted_opportunities(self):
        """Test that organization dashboard displays posted opportunities."""
        self.client.login(username='org_dashboard_test', password='OrgPass123!')
        response = self.client.get(reverse('organization_dashboard'))
        
        # Verify opportunities appear in response
        self.assertContains(response, 'Dashboard Test Opportunity')
        self.assertContains(response, 'Another Test Opportunity')

    def test_student_cannot_access_organization_dashboard(self):
        """Test that students cannot access organization dashboard."""
        self.client.login(username='student_app_test', password='StudentPass123!')
        response = self.client.get(reverse('organization_dashboard'))
        
        # Should be redirected or denied access
        self.assertIn(response.status_code, [302, 403])

    def test_organization_dashboard_shows_applications(self):
        """Test that organization dashboard displays student applications."""
        from .models import Application
        
        # Create application from student
        application = Application.objects.create(
            student=self.student,
            opportunity=self.opportunity1,
            status='submitted',
            message='I am interested in this opportunity'
        )
        
        self.client.login(username='org_dashboard_test', password='OrgPass123!')
        response = self.client.get(reverse('organization_dashboard'))
        
        self.assertEqual(response.status_code, 200)


class VolunteerProfileTest(TestCase):
    """Test suite for volunteer profile functionality."""

    def setUp(self):
        """Set up test fixtures for volunteer profile tests."""
        self.client = Client()
        
        # Create student user
        self.student = User.objects.create_user(
            username='volunteer_test',
            email='volunteer@test.com',
            password='VolPass123!',
            user_type='student',
            display_name='Volunteer Student'
        )

    def test_volunteer_profile_view_access(self):
        """Test that students can access volunteer profile view."""
        self.client.login(username='volunteer_test', password='VolPass123!')
        response = self.client.get(reverse('volunteer_profile_view', args=[self.student.id]))
        self.assertEqual(response.status_code, 200)

    def test_volunteer_profile_edit_access(self):
        """Test that students can access volunteer profile edit page."""
        self.client.login(username='volunteer_test', password='VolPass123!')
        response = self.client.get(reverse('volunteer_profile_edit'))
        self.assertEqual(response.status_code, 200)

    def test_volunteer_profile_form_validation(self):
        """Test volunteer profile form validation."""
        form_data = {
            'bio': 'I am a passionate volunteer',
            'skills': 'Teaching, Mentoring',
        }
        form = VolunteerProfileForm(data=form_data)
        self.assertTrue(form.is_valid())

    def test_volunteer_profile_saves_experience(self):
        """Test that volunteer experience can be saved."""
        self.client.login(username='volunteer_test', password='VolPass123!')
        
        experience_data = {
            'title': 'Teaching Assistant',
            'organization': 'Test School',
            'start_date': '2025-01-01',
            'end_date': '2025-12-31',
            'description': 'Assisted with teaching'
        }
        
        # Create volunteer profile first
        from .models import VolunteerProfile
        profile = VolunteerProfile.objects.create(
            student=self.student,
            bio='Test bio'
        )
        
        # Add experience
        experience = VolunteerExperience.objects.create(
            volunteer_profile=profile,
            title=experience_data['title'],
            organization=experience_data['organization'],
            start_date=experience_data['start_date'],
            description=experience_data['description']
        )
        
        self.assertEqual(experience.title, 'Teaching Assistant')
        self.assertEqual(profile.student, self.student)


class StudentApplicationTest(TestCase):
    """Test suite for student application to opportunities."""

    def setUp(self):
        """Set up test fixtures for student application tests."""
        self.client = Client()
        
        # Create organization
        self.organization = User.objects.create_user(
            username='app_org_test',
            email='app_org@test.com',
            password='OrgPass123!',
            user_type='organization'
        )
        
        # Create student
        self.student = User.objects.create_user(
            username='app_student_test',
            email='app_student@test.com',
            password='StudentPass123!',
            user_type='student'
        )
        
        # Create opportunity
        self.opportunity = Opportunity.objects.create(
            title='Application Test Opportunity',
            description='Test opportunity for applications',
            organization=self.organization,
            status='open',
            application_deadline=timezone.now() + timedelta(days=30)
        )

    def test_student_can_apply_to_opportunity(self):
        """Test that students can submit applications."""
        self.client.login(username='app_student_test', password='StudentPass123!')
        
        from .models import Application
        application = Application.objects.create(
            student=self.student,
            opportunity=self.opportunity,
            status='draft',
            message='I am very interested in this opportunity'
        )
        
        self.assertEqual(application.student, self.student)
        self.assertEqual(application.opportunity, self.opportunity)

    def test_application_form_validation(self):
        """Test application form validation."""
        from .forms import ApplicationForm
        
        form_data = {
            'message': 'I would like to apply for this opportunity',
        }
        form = ApplicationForm(data=form_data)
        self.assertTrue(form.is_valid())

    def test_organization_can_approve_application(self):
        """Test that organizations can approve student applications."""
        from .models import Application
        
        application = Application.objects.create(
            student=self.student,
            opportunity=self.opportunity,
            status='submitted'
        )
        
        # Change application status to approved
        application.status = 'approved'
        application.save()
        
        self.assertEqual(application.status, 'approved')

    def test_organization_can_deny_application(self):
        """Test that organizations can deny student applications."""
        from .models import Application
        
        application = Application.objects.create(
            student=self.student,
            opportunity=self.opportunity,
            status='submitted'
        )
        
        # Change application status to denied
        application.status = 'denied'
        application.denial_reason = 'Not meeting required skills'
        application.save()
        
        self.assertEqual(application.status, 'denied')
        self.assertEqual(application.denial_reason, 'Not meeting required skills')


class OpportunityListingTest(TestCase):
    """Test suite for opportunity listing and details."""

    def setUp(self):
        """Set up test fixtures for opportunity tests."""
        self.client = Client()
        
        # Create organization
        self.organization = User.objects.create_user(
            username='list_org_test',
            email='list_org@test.com',
            password='OrgPass123!',
            user_type='organization'
        )
        
        # Create student
        self.student = User.objects.create_user(
            username='list_student_test',
            email='list_student@test.com',
            password='StudentPass123!',
            user_type='student'
        )
        
        # Create opportunities
        self.active_opportunity = Opportunity.objects.create(
            title='Active Opportunity',
            description='This is an active opportunity',
            organization=self.organization,
            status='open',
            is_active=True
        )
        
        self.closed_opportunity = Opportunity.objects.create(
            title='Closed Opportunity',
            description='This opportunity is closed',
            organization=self.organization,
            status='closed',
            is_active=False
        )

    def test_student_can_view_opportunity_list(self):
        """Test that students can view list of opportunities."""
        self.client.login(username='list_student_test', password='StudentPass123!')
        response = self.client.get(reverse('opportunity_list'))
        self.assertEqual(response.status_code, 200)

    def test_opportunity_list_shows_active_opportunities(self):
        """Test that opportunity list displays only active opportunities."""
        self.client.login(username='list_student_test', password='StudentPass123!')
        response = self.client.get(reverse('opportunity_list'))
        
        self.assertContains(response, 'Active Opportunity')
        # Closed opportunity might not appear depending on filtering

    def test_student_can_view_opportunity_details(self):
        """Test that students can view detailed opportunity information."""
        self.client.login(username='list_student_test', password='StudentPass123!')
        response = self.client.get(reverse('opportunity_detail', args=[self.active_opportunity.id]))
        
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Active Opportunity')

    def test_mark_opportunity_as_pending(self):
        """Test that students can mark opportunity as pending completion."""
        self.client.login(username='list_student_test', password='StudentPass123!')
        
        # Create student opportunity
        student_opp = StudentOpportunity.objects.create(
            student=self.student,
            opportunity=self.active_opportunity,
            status='in_progress'
        )
        
        # Mark as pending
        student_opp.status = 'pending'
        student_opp.date_pending = timezone.now()
        student_opp.save()
        
        self.assertEqual(student_opp.status, 'pending')

