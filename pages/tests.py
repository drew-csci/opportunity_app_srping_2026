from django.test import TestCase, Client
from django.urls import reverse

from accounts.models import User
from .models import Opportunity


class Screen1NoQueryReturnsAllActiveOpportunitiesTest(TestCase):
    """
    Test #10: Search with no query returns all active opportunities.
    Load /screen1/ with no GET parameters and assert all active
    opportunities in the database are returned (unfiltered baseline state).
    """

    def setUp(self):
        # Create an organization user to own the opportunities
        self.org_user = User.objects.create_user(
            username='testorg@example.com',
            email='testorg@example.com',
            password='testpass123',
            user_type='organization',
        )

        # Create a student user to log in as
        self.student_user = User.objects.create_user(
            username='teststudent@example.com',
            email='teststudent@example.com',
            password='testpass123',
            user_type='student',
        )

        # Create two active opportunities
        self.opp1 = Opportunity.objects.create(
            title='Park Cleanup Volunteer',
            organization=self.org_user,
            description='Help clean up the local park.',
            cause='Environment',
            location='Chicago, IL',
            duration='1 day',
            skills_required='None',
            opportunity_type='volunteer',
            is_active=True,
        )
        self.opp2 = Opportunity.objects.create(
            title='Coding Bootcamp Internship',
            organization=self.org_user,
            description='Assist instructors at a youth coding camp.',
            cause='Education',
            location='Remote',
            duration='3 months',
            skills_required='Python, HTML',
            opportunity_type='internship',
            is_active=True,
        )

        # Create one inactive opportunity — should NOT appear in results
        self.opp_inactive = Opportunity.objects.create(
            title='Inactive Listing',
            organization=self.org_user,
            description='This should not be visible.',
            cause='Health',
            location='New York, NY',
            duration='2 weeks',
            skills_required='None',
            opportunity_type='volunteer',
            is_active=False,
        )

        self.client = Client()
        self.client.login(email='teststudent@example.com', password='testpass123')

    def test_no_query_returns_all_active_opportunities(self):
        response = self.client.get(reverse('screen1'))

        self.assertEqual(response.status_code, 200)

        opportunities = response.context['opportunities']

        # Both active opportunities must be present
        self.assertIn(self.opp1, opportunities)
        self.assertIn(self.opp2, opportunities)

        # The inactive opportunity must NOT be present
        self.assertNotIn(self.opp_inactive, opportunities)

        # Total count must equal the number of active opportunities (2)
        self.assertEqual(opportunities.count(), 2)


class ClearButtonVisibilityIntegrationTest(TestCase):
    """
    Integration Test #4: The Clear button appears only when a search or
    filter is active.
    - Plain /screen1/ with no parameters → Clear button must NOT be in the HTML.
    - /screen1/?q=health with a keyword → Clear button MUST be in the HTML.
    """

    def setUp(self):
        # Create an organization user to satisfy the Opportunity ForeignKey
        self.org_user = User.objects.create_user(
            username='testorg2@example.com',
            email='testorg2@example.com',
            password='testpass123',
            user_type='organization',
        )

        # Create a student user to access the page
        self.student_user = User.objects.create_user(
            username='teststudent2@example.com',
            email='teststudent2@example.com',
            password='testpass123',
            user_type='student',
        )

        # Seed one active opportunity so the page renders the full template
        Opportunity.objects.create(
            title='Health Clinic Volunteer',
            organization=self.org_user,
            description='Assist at a community health clinic.',
            cause='Health',
            location='Boston, MA',
            duration='Ongoing',
            skills_required='Communication',
            opportunity_type='volunteer',
            is_active=True,
        )

        self.client = Client()
        self.client.login(email='teststudent2@example.com', password='testpass123')

    def test_clear_button_absent_with_no_query(self):
        # Load the page with no search or filter parameters
        response = self.client.get(reverse('screen1'))

        self.assertEqual(response.status_code, 200)

        # The Clear button must NOT be rendered when no search is active
        self.assertNotContains(response, 'btn-clear')

    def test_clear_button_present_with_keyword_query(self):
        # Load the page with an active keyword search
        response = self.client.get(reverse('screen1'), {'q': 'health'})

        self.assertEqual(response.status_code, 200)

        # The Clear button MUST be rendered when a keyword search is active
        self.assertContains(response, 'btn-clear')

    def test_clear_button_present_with_filter_only(self):
        # Load the page with a filter applied but no keyword search
        response = self.client.get(reverse('screen1'), {'location': 'Boston'})

        self.assertEqual(response.status_code, 200)

        # The Clear button MUST also appear when only a filter is active
        self.assertContains(response, 'btn-clear')
