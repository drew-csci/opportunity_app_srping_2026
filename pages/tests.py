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
