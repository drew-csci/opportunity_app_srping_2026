from django.test import TestCase, Client
from django.urls import reverse
from accounts.models import User
from pages.models import Opportunity, Application, OrganizationFollow

class CriticalFeatureRegressionTests(TestCase):
    """
    Dedicated regression test suite designed to lock in the primary
    business logic and workflows of the application, ensuring that
    new features don't inadvertently break existing core behavior over time.
    """
    
    def setUp(self):
        self.client = Client()
        # Ensure base data dependencies exist
        self.student = User.objects.create_user(
            email='student_regress@test.com', username='student_regress', 
            password='testpass', user_type='student'
        )
        self.org = User.objects.create_user(
            email='org_regress@test.com', username='org_regress', 
            password='testpass', user_type='organization'
        )
        self.opportunity = Opportunity.objects.create(
            title='Regression Master Opportunity',
            description='Must not break.',
            organization=self.org,
            is_active=True
        )

    def test_regression_application_decision_lock(self):
        """
        Regression: Validates that Applications gracefully move from DRAFT 
        to PENDING, and finally to ACCEPTED by the organization with proper timestamps.
        If UI changes accidentally break form routing or status flags later, 
        this suite acts as a physical barrier.
        """
        # Step 1: Student creates DRAFT
        self.client.force_login(self.student)
        self.client.post(
            reverse('apply_to_opportunity', args=[self.opportunity.id]),
            {'message': 'Draft message', 'action': 'save_draft'}
        )
        app = Application.objects.get(student=self.student, opportunity=self.opportunity)
        self.assertEqual(app.status, Application.Status.DRAFT)
        self.assertEqual(app.message, 'Draft message')
        
        # Step 2: Student finalizes submission creating a PENDING state
        self.client.post(
            reverse('apply_to_opportunity', args=[self.opportunity.id]),
            {'message': 'Final application', 'action': 'submit'}
        )
        app.refresh_from_db()
        self.assertEqual(app.status, Application.Status.PENDING)
        self.assertEqual(app.message, 'Final application')
        
        # Step 3: Organization evaluates making it ACCEPTED
        self.client.force_login(self.org)
        self.client.post(
            reverse('review_application', args=[app.id]),
            {'decision': Application.Status.ACCEPTED}
        )
        app.refresh_from_db()
        self.assertEqual(app.status, Application.Status.ACCEPTED)
        
        # Ensure timestamp automation wasn't bypassed
        self.assertIsNotNone(app.responded_date)

    def test_regression_organization_follow_state(self):
        """
        Regression: Verifies that a student can follow an organization natively, 
        that the relationship renders correctly to the standard dashboard, 
        and allows clean unfollow mapping tracking.
        """
        self.client.force_login(self.student)
        
        # Link student to organization
        self.client.post(reverse('follow_organization', args=[self.org.id]))
        self.assertTrue(OrganizationFollow.objects.filter(student=self.student, organization=self.org).exists())
        
        # Safely render following list
        response = self.client.get(reverse('followed_organizations'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.org.email)
        
        # Unlink the organization link safely
        self.client.post(reverse('unfollow_organization', args=[self.org.id]))
        self.assertFalse(OrganizationFollow.objects.filter(student=self.student, organization=self.org).exists())
