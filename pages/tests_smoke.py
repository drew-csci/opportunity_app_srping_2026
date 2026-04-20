from django.test import TestCase, Client
from django.urls import reverse
from accounts.models import User
from pages.models import Opportunity


class SmokeTests(TestCase):
    """
    Quick smoke tests to verify core app functionality works.
    These are fast checks that the application basically operates.
    """

    def setUp(self):
        self.client = Client()

    def test_welcome_page_loads(self):
        """Verify the welcome page loads successfully."""
        response = self.client.get(reverse('welcome'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Welcome')

    def test_faq_endpoint_smokes(self):
        """Verify secondary static FAQ routing is alive without 500 crashes."""
        response = self.client.get(reverse('faq'))
        self.assertEqual(response.status_code, 200)

    def test_opportunity_list_redirects_unauthenticated(self):
        """Verify protected opportunity list redirects when not logged in."""
        response = self.client.get(reverse('opportunity_list'))
        self.assertEqual(response.status_code, 302)  # Should redirect to login

    def test_user_model_creation(self):
        """Verify basic user model operations work."""
        user = User.objects.create_user(
            email='smoke@test.com',
            username='smokeuser',
            password='testpass'
        )
        self.assertIsNotNone(user.id)
        self.assertEqual(user.email, 'smoke@test.com')

    def test_opportunity_model_creation(self):
        """Verify opportunity model can be created."""
        org = User.objects.create_user(
            email='org@test.com',
            username='orguser',
            password='testpass',
            user_type='organization'
        )
        opp = Opportunity.objects.create(
            title='Smoke Test Opp',
            description='Test desc',
            organization=org,
            is_active=True
        )
        self.assertIsNotNone(opp.id)
        self.assertEqual(opp.title, 'Smoke Test Opp')

    def test_opportunity_list_loads_for_student(self):
        """Verify opportunity list loads for authenticated student."""
        student = User.objects.create_user(
            email='student@test.com',
            username='studentuser',
            password='testpass',
            user_type='student'
        )
        self.client.login(email='student@test.com', password='testpass')
        response = self.client.get(reverse('opportunity_list'))
        self.assertEqual(response.status_code, 200)