from django.test import TestCase, Client
from django.urls import reverse
from accounts.models import User
from pages.models import Opportunity, Application


class IntegrationTests(TestCase):
    """
    Integration tests verifying key system components work together.
    Tests full user flows from creation to completion.
    """

    def setUp(self):
        self.client = Client()
        # Create test users
        self.student = User.objects.create_user(
            email='student@test.com',
            username='student',
            password='pass',
            user_type='student'
        )
        self.org = User.objects.create_user(
            email='org@test.com',
            username='org',
            password='pass',
            user_type='organization'
        )
        # Create test opportunity
        self.opportunity = Opportunity.objects.create(
            title='Test Opportunity',
            description='Test description',
            organization=self.org,
            is_active=True
        )

    def test_full_application_workflow(self):
        """Test complete flow: student applies, organization reviews."""
        # Step 1: Student logs in and views opportunities
        self.client.login(email='student@test.com', password='pass')
        response = self.client.get(reverse('opportunity_list'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Test Opportunity')

        # Step 2: Student applies to opportunity
        response = self.client.post(
            reverse('apply_to_opportunity', args=[self.opportunity.id]),
            {'message': 'I want to help', 'action': 'submit'}
        )
        self.assertEqual(response.status_code, 302)  # Redirect after submit

        # Verify application created with correct status
        application = Application.objects.get(
            student=self.student,
            opportunity=self.opportunity
        )
        self.assertEqual(application.status, Application.Status.PENDING)

        # Step 3: Organization logs in and reviews application
        self.client.login(email='org@test.com', password='pass')
        response = self.client.post(
            reverse('review_application', args=[application.id]),
            {'decision': 'accepted'}
        )
        self.assertEqual(response.status_code, 302)  # Redirect after decision

        # Verify application status updated
        application.refresh_from_db()
        self.assertEqual(application.status, Application.Status.ACCEPTED)

    def test_my_applications_data_aggregation(self):
        """Test my_applications view correctly shows user's applications."""
        # Create some test data
        app1 = Application.objects.create(
            student=self.student,
            opportunity=self.opportunity,
            status=Application.Status.PENDING
        )
        app2 = Application.objects.create(
            student=self.student,
            opportunity=self.opportunity,
            status=Application.Status.ACCEPTED
        )

        # Login and access my applications
        self.client.login(email='student@test.com', password='pass')
        response = self.client.get(reverse('my_applications'))
        self.assertEqual(response.status_code, 200)

        # Verify page shows application data
        self.assertContains(response, 'Test Opportunity')

    def test_organization_application_management(self):
        """Test organization can view and manage their applications."""
        # Create application for org's opportunity
        app = Application.objects.create(
            student=self.student,
            opportunity=self.opportunity,
            status=Application.Status.PENDING
        )

        # Organization logs in and views applications
        self.client.login(email='org@test.com', password='pass')
        response = self.client.get(reverse('organization_applications'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Test Opportunity')

        # Organization reviews specific application
        response = self.client.get(reverse('review_application', args=[app.id]))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, app.student.email)

    def test_profile_experience_system_integration(self):
        """
        Integration: Validates the data chain crossing the Router -> View ->
        Form logic -> and firmly linking into the Database constraints via Foreign Key.
        """
        self.client.login(email='student@test.com', password='pass')
        
        # 1. Fire fake payload into the Routing Layer
        response = self.client.post(reverse('experience_add'), {
            'organization_name': 'Global Tech Relief',
            'role': 'Coordinator',
            'description': 'Helped organize technical relief events.',
            'start_date': '2023-01-01',
            'is_current': 'on'
        })
        
        # 2. View successfully intercepted and bounced back to Profile Editor securely
        self.assertEqual(response.status_code, 302) 
        self.assertRedirects(response, reverse('volunteer_profile_edit'))
        
        # 3. Form and DB Layer physically connected, parsing and securely saving the data
        from pages.models import VolunteerExperience
        db_record = VolunteerExperience.objects.filter(volunteer=self.student).first()
        self.assertIsNotNone(db_record)
        self.assertEqual(db_record.organization_name, 'Global Tech Relief')
        self.assertEqual(db_record.role, 'Coordinator')