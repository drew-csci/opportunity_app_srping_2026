from django.test import TestCase, Client
from django.urls import reverse
from accounts.models import User
from pages.models import Achievement, Opportunity, Application, VolunteerExperience

class CoverageCompletenessTests(TestCase):
    """
    These tests specifically target edge cases, non-happy-paths, 
    and smaller sub-views to drive up code coverage across pages/views.py.
    """
    
    def setUp(self):
        self.client = Client()
        self.student = User.objects.create_user(
            email='cov_student@test.com', username='cov_student', password='pass', user_type='student'
        )
        self.org = User.objects.create_user(
            email='cov_org@test.com', username='cov_org', password='pass', user_type='organization'
        )
        self.opp = Opportunity.objects.create(
            title='Cov Test Opp', organization=self.org, is_active=True
        )

    def test_static_screens_and_faq(self):
        """Test simple rendering views."""
        self.client.force_login(self.student)
        self.assertEqual(self.client.get(reverse('screen2')).status_code, 200)
        self.assertEqual(self.client.get(reverse('screen3')).status_code, 200)
        self.assertEqual(self.client.get(reverse('faq')).status_code, 200)

    def test_screen1_decline_action(self):
        """Test POST action 'decline' in screen1."""
        self.client.force_login(self.org)
        response = self.client.post(reverse('screen1'), {'index': '0', 'action': 'decline'})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Declined')

    def test_student_achievements_view(self):
        """Test GET and valid POST on student achievements."""
        self.client.force_login(self.student)
        # GET
        self.assertEqual(self.client.get(reverse('student_achievements')).status_code, 200)
        # POST
        response = self.client.post(reverse('student_achievements'), {
            'title': 'Coverage Test',
            'description': 'Hit 100%',
            'date_completed': '2025-01-01'
        })
        self.assertRedirects(response, reverse('student_achievements'))
        self.assertEqual(Achievement.objects.filter(student=self.student).count(), 1)

    def test_volunteer_profile_not_exist_redirect(self):
        """Test redirect to edit when profile doesn't exist."""
        self.client.force_login(self.student)
        response = self.client.get(reverse('volunteer_profile'))
        self.assertRedirects(response, reverse('volunteer_profile_edit'))

    def test_experience_add_get_and_edit_workflow(self):
        """Test GET for adding and both GET/POST for editing experience."""
        self.client.force_login(self.student)
        self.assertEqual(self.client.get(reverse('experience_add')).status_code, 200)
        
        # Create an experience to edit
        exp = VolunteerExperience.objects.create(
            volunteer=self.student, organization_name='Org', role='Role',
            description='Desc', start_date='2024-01-01'
        )
        self.assertEqual(self.client.get(reverse('experience_edit', args=[exp.id])).status_code, 200)
        
        # Valid edit submission
        response = self.client.post(reverse('experience_edit', args=[exp.id]), {
            'organization_name': 'New Org',
            'role': 'New Role',
            'description': 'New Desc',
            'start_date': '2024-01-01',
            'is_current': 'on'
        })
        self.assertRedirects(response, reverse('volunteer_profile_edit'))
        exp.refresh_from_db()
        self.assertEqual(exp.organization_name, 'New Org')

    def test_role_enforcement_redirects(self):
        """Ensure views block wrong user types and redirect safely to screen1."""
        self.client.force_login(self.org)
        
        # Org trying to hit student routes
        self.assertRedirects(self.client.get(reverse('opportunity_list')), reverse('screen1'))
        self.assertRedirects(self.client.get(reverse('apply_to_opportunity', args=[self.opp.id])), reverse('screen1'))
        
        # Provide an application for application_detail
        app = Application.objects.create(student=self.student, opportunity=self.opp)
        self.assertRedirects(self.client.get(reverse('application_detail', args=[app.id])), reverse('screen1'))
        self.assertRedirects(self.client.get(reverse('followed_organizations')), reverse('screen1'))
        
        # Student trying to hit org routes
        self.client.force_login(self.student)
        self.assertRedirects(self.client.get(reverse('review_application', args=[app.id])), reverse('screen1'))
