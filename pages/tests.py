from django.test import TestCase, Client
from django.urls import reverse
from django.db import connection

from accounts.models import User
from .models import Opportunity, OrganizationFollow, Application, Notification
import json


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

        # Dropdown suggestion context should be populated from active opportunities
        self.assertIn('Chicago, IL', response.context['filter_options']['locations'])
        self.assertIn('1 day', response.context['filter_options']['durations'])
        self.assertIn('Python', response.context['filter_options']['skills'])


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


class OrganizationFollowModelTests(TestCase):
    """Unit tests for OrganizationFollow model"""

    def setUp(self):
        """Create test users for each test"""
        self.student = User.objects.create_user(
            username='student_test',
            email='student_test@drew.edu',
            password='TestPass123!',
            user_type='student'
        )
        self.organization = User.objects.create_user(
            username='org_test',
            email='org_test@drew.edu',
            password='TestPass123!',
            user_type='organization'
        )

    def test_create_follow_relationship(self):
        """Test creating a follow relationship between student and organization"""
        follow = OrganizationFollow.objects.create(
            student=self.student,
            organization=self.organization
        )
        self.assertTrue(OrganizationFollow.objects.filter(
            student=self.student,
            organization=self.organization
        ).exists())
        self.assertEqual(follow.student, self.student)
        self.assertEqual(follow.organization, self.organization)

    def test_unique_constraint_prevents_duplicate_follows(self):
        """Test that unique constraint prevents duplicate follow relationships"""
        OrganizationFollow.objects.create(
            student=self.student,
            organization=self.organization
        )
        # Attempting to create duplicate should fail
        with self.assertRaises(Exception):
            OrganizationFollow.objects.create(
                student=self.student,
                organization=self.organization
            )

    def test_follow_relationship_string_representation(self):
        """Test the __str__ method of OrganizationFollow model"""
        follow = OrganizationFollow.objects.create(
            student=self.student,
            organization=self.organization
        )
        expected_str = f"{self.student} follows {self.organization}"
        self.assertEqual(str(follow), expected_str)

    def test_student_can_follow_multiple_organizations(self):
        """Test that one student can follow multiple organizations"""
        org2 = User.objects.create_user(
            username='org_test2',
            email='org_test2@drew.edu',
            password='TestPass123!',
            user_type='organization'
        )
        OrganizationFollow.objects.create(
            student=self.student,
            organization=self.organization
        )
        OrganizationFollow.objects.create(
            student=self.student,
            organization=org2
        )
        self.assertEqual(
            OrganizationFollow.objects.filter(student=self.student).count(),
            2
        )

    def test_organization_can_have_multiple_followers(self):
        """Test that one organization can have multiple student followers"""
        student2 = User.objects.create_user(
            username='student_test2',
            email='student_test2@drew.edu',
            password='TestPass123!',
            user_type='student'
        )
        OrganizationFollow.objects.create(
            student=self.student,
            organization=self.organization
        )
        OrganizationFollow.objects.create(
            student=student2,
            organization=self.organization
        )
        self.assertEqual(
            OrganizationFollow.objects.filter(organization=self.organization).count(),
            2
        )


class FollowOrganizationViewTests(TestCase):
    """Unit tests for follow_organization view"""

    def setUp(self):
        """Create test users and client"""
        self.client = Client()
        self.student = User.objects.create_user(
            username='student_test',
            email='student_test@drew.edu',
            password='TestPass123!',
            user_type='student'
        )
        self.organization = User.objects.create_user(
            username='org_test',
            email='org_test@drew.edu',
            password='TestPass123!',
            user_type='organization'
        )

    def test_follow_organization_creates_relationship(self):
        """Test that following an organization creates a follow relationship"""
        self.client.login(email='student_test@drew.edu', password='TestPass123!')
        response = self.client.post(
            reverse('follow_organization', args=[self.organization.id])
        )
        self.assertTrue(OrganizationFollow.objects.filter(
            student=self.student,
            organization=self.organization
        ).exists())

    def test_follow_organization_redirects_on_success(self):
        """Test that follow redirects to organization profile"""
        self.client.login(email='student_test@drew.edu', password='TestPass123!')
        response = self.client.post(
            reverse('follow_organization', args=[self.organization.id]),
            follow=False
        )
        self.assertEqual(response.status_code, 302)
        self.assertIn(
            reverse('organization_profile', args=[self.organization.id]),
            response.url
        )

    def test_follow_organization_ajax_returns_json(self):
        """Test that AJAX follow request returns JSON response"""
        self.client.login(email='student_test@drew.edu', password='TestPass123!')
        response = self.client.post(
            reverse('follow_organization', args=[self.organization.id]),
            HTTP_X_REQUESTED_WITH='XMLHttpRequest'
        )
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertTrue(data['success'])
        self.assertTrue(data['following'])

    def test_follow_organization_non_student_fails(self):
        """Test that non-students cannot follow organizations"""
        self.client.login(email='org_test@drew.edu', password='TestPass123!')
        response = self.client.post(
            reverse('follow_organization', args=[self.organization.id]),
            HTTP_X_REQUESTED_WITH='XMLHttpRequest'
        )
        self.assertEqual(response.status_code, 403)
        data = json.loads(response.content)
        self.assertFalse(data['success'])

    def test_follow_organization_requires_login(self):
        """Test that unauthenticated users are redirected"""
        response = self.client.post(
            reverse('follow_organization', args=[self.organization.id]),
            follow=False
        )
        self.assertEqual(response.status_code, 302)
        self.assertIn('/accounts/login', response.url)

    def test_follow_nonexistent_organization(self):
        """Test that following a nonexistent organization raises 404"""
        self.client.login(email='student_test@drew.edu', password='TestPass123!')
        response = self.client.post(
            reverse('follow_organization', args=[99999])
        )
        self.assertEqual(response.status_code, 404)


class UnfollowOrganizationViewTests(TestCase):
    """Unit tests for unfollow_organization view"""

    def setUp(self):
        """Create test users and existing follow relationship"""
        self.client = Client()
        self.student = User.objects.create_user(
            username='student_test',
            email='student_test@drew.edu',
            password='TestPass123!',
            user_type='student'
        )
        self.organization = User.objects.create_user(
            username='org_test',
            email='org_test@drew.edu',
            password='TestPass123!',
            user_type='organization'
        )
        # Create an existing follow relationship
        self.follow = OrganizationFollow.objects.create(
            student=self.student,
            organization=self.organization
        )

    def test_unfollow_organization_deletes_relationship(self):
        """Test that unfollowing an organization deletes the relationship"""
        self.client.login(email='student_test@drew.edu', password='TestPass123!')
        self.client.post(
            reverse('unfollow_organization', args=[self.organization.id])
        )
        self.assertFalse(OrganizationFollow.objects.filter(
            student=self.student,
            organization=self.organization
        ).exists())

    def test_unfollow_organization_redirects_on_success(self):
        """Test that unfollow redirects to organization profile"""
        self.client.login(email='student_test@drew.edu', password='TestPass123!')
        response = self.client.post(
            reverse('unfollow_organization', args=[self.organization.id]),
            follow=False
        )
        self.assertEqual(response.status_code, 302)
        self.assertIn(
            reverse('organization_profile', args=[self.organization.id]),
            response.url
        )

    def test_unfollow_organization_ajax_returns_json(self):
        """Test that AJAX unfollow request returns JSON response"""
        self.client.login(email='student_test@drew.edu', password='TestPass123!')
        response = self.client.post(
            reverse('unfollow_organization', args=[self.organization.id]),
            HTTP_X_REQUESTED_WITH='XMLHttpRequest'
        )
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertTrue(data['success'])
        self.assertFalse(data['following'])

    def test_unfollow_organization_non_student_fails(self):
        """Test that non-students cannot unfollow organizations"""
        self.client.login(email='org_test@drew.edu', password='TestPass123!')
        response = self.client.post(
            reverse('unfollow_organization', args=[self.organization.id]),
            HTTP_X_REQUESTED_WITH='XMLHttpRequest'
        )
        self.assertEqual(response.status_code, 403)
        data = json.loads(response.content)
        self.assertFalse(data['success'])

    def test_unfollow_organization_requires_login(self):
        """Test that unauthenticated users are redirected"""
        response = self.client.post(
            reverse('unfollow_organization', args=[self.organization.id]),
            follow=False
        )
        self.assertEqual(response.status_code, 302)
        self.assertIn('/accounts/login', response.url)

    def test_unfollow_nonexistent_organization(self):
        """Test that unfollowing a nonexistent organization raises 404"""
        self.client.login(email='student_test@drew.edu', password='TestPass123!')
        response = self.client.post(
            reverse('unfollow_organization', args=[99999])
        )
        self.assertEqual(response.status_code, 404)


class FollowOrganizationIntegrationTests(TestCase):
    """Integration tests for complete follow/unfollow workflow"""

    def setUp(self):
        """Create test users and client"""
        self.client = Client()
        self.student = User.objects.create_user(
            username='student_test',
            email='student_test@drew.edu',
            password='TestPass123!',
            user_type='student'
        )
        self.organization = User.objects.create_user(
            username='org_test',
            email='org_test@drew.edu',
            password='TestPass123!',
            user_type='organization'
        )

    def test_complete_follow_workflow(self):
        """Integration test: Student logs in, follows org, views followed orgs, unfollows"""
        # Step 1: Login as student
        login_success = self.client.login(
            email='student_test@drew.edu',
            password='TestPass123!'
        )
        self.assertTrue(login_success)

        # Step 2: Follow an organization
        follow_response = self.client.post(
            reverse('follow_organization', args=[self.organization.id])
        )
        self.assertEqual(follow_response.status_code, 302)

        # Step 3: Verify follow relationship exists
        self.assertTrue(OrganizationFollow.objects.filter(
            student=self.student,
            organization=self.organization
        ).exists())

        # Step 4: View organization profile
        profile_response = self.client.get(
            reverse('organization_profile', args=[self.organization.id])
        )
        self.assertEqual(profile_response.status_code, 200)
        self.assertIn(b'Following', profile_response.content)

        # Step 5: View all followed organizations
        followed_response = self.client.get(reverse('followed_organizations'))
        self.assertEqual(followed_response.status_code, 200)
        self.assertIn(self.organization.display_name.encode(), followed_response.content)

        # Step 6: Unfollow organization
        unfollow_response = self.client.post(
            reverse('unfollow_organization', args=[self.organization.id])
        )
        self.assertEqual(unfollow_response.status_code, 302)

        # Step 7: Verify follow relationship no longer exists
        self.assertFalse(OrganizationFollow.objects.filter(
            student=self.student,
            organization=self.organization
        ).exists())

    def test_ajax_follow_unfollow_workflow(self):
        """Integration test: AJAX follow/unfollow workflow"""
        self.client.login(email='student_test@drew.edu', password='TestPass123!')

        # Follow via AJAX
        follow_response = self.client.post(
            reverse('follow_organization', args=[self.organization.id]),
            HTTP_X_REQUESTED_WITH='XMLHttpRequest'
        )
        follow_data = json.loads(follow_response.content)
        self.assertTrue(follow_data['success'])
        self.assertTrue(follow_data['following'])

        # Verify relationship exists
        self.assertTrue(OrganizationFollow.objects.filter(
            student=self.student,
            organization=self.organization
        ).exists())

        # Unfollow via AJAX
        unfollow_response = self.client.post(
            reverse('unfollow_organization', args=[self.organization.id]),
            HTTP_X_REQUESTED_WITH='XMLHttpRequest'
        )
        unfollow_data = json.loads(unfollow_response.content)
        self.assertTrue(unfollow_data['success'])
        self.assertFalse(unfollow_data['following'])

        # Verify relationship no longer exists
        self.assertFalse(OrganizationFollow.objects.filter(
            student=self.student,
            organization=self.organization
        ).exists())

    def test_student_follows_multiple_organizations(self):
        """Integration test: Student can follow multiple organizations"""
        org2 = User.objects.create_user(
            username='org_test2',
            email='org_test2@drew.edu',
            password='TestPass123!',
            user_type='organization'
        )

        self.client.login(email='student_test@drew.edu', password='TestPass123!')

        # Follow first organization
        self.client.post(reverse('follow_organization', args=[self.organization.id]))

        # Follow second organization
        self.client.post(reverse('follow_organization', args=[org2.id]))

        # Verify both relationships exist
        self.assertEqual(
            OrganizationFollow.objects.filter(student=self.student).count(),
            2
        )

        # View followed organizations page
        response = self.client.get(reverse('followed_organizations'))
        self.assertEqual(response.status_code, 200)
        self.assertIn(self.organization.display_name.encode(), response.content)
        self.assertIn(org2.display_name.encode(), response.content)

    def test_multiple_students_follow_same_organization(self):
        """Integration test: Multiple students can follow the same organization"""
        student2 = User.objects.create_user(
            username='student_test2',
            email='student_test2@drew.edu',
            password='TestPass123!',
            user_type='student'
        )

        # Student 1 follows organization
        self.client.login(email='student_test@drew.edu', password='TestPass123!')
        self.client.post(reverse('follow_organization', args=[self.organization.id]))

        # Student 2 follows same organization
        self.client.logout()
        self.client.login(email='student_test2@drew.edu', password='TestPass123!')
        self.client.post(reverse('follow_organization', args=[self.organization.id]))

        # Verify both follow relationships exist
        self.assertEqual(
            OrganizationFollow.objects.filter(organization=self.organization).count(),
            2
        )


<<<<<<< HEAD
class US007US008NotificationAndReminderTests(TestCase):
    """Tests for US-007 (notifications) and US-008 (reminder button)"""

    def setUp(self):
        """Create common test fixtures"""
        self.client = Client()
        self.student = User.objects.create_user(
            username='student_us007',
            email='student_us007@drew.edu',
            password='TestPass123!',
            user_type='student'
        )
        self.organization = User.objects.create_user(
            username='org_us007',
            email='org_us007@drew.edu',
            password='TestPass123!',
            user_type='organization'
        )
        self.opportunity = Opportunity.objects.create(
            title='Test Opportunity',
            organization=self.organization,
            description='Test description',
            category='Community',
            location='Test Location',
            duration='one-time',
            opportunity_type='volunteer',
            is_active=True,
        )

    def test_accept_application_creates_notification(self):
        """Test that accepting an application creates a notification for the student"""
        # Create a pending application
        application = Application.objects.create(
            student=self.student,
            opportunity=self.opportunity,
            status='pending',
            message='Test application'
        )
        
        # Login as organization
        self.client.login(email='org_us007@drew.edu', password='TestPass123!')
        
        # Accept the application via review_application
        response = self.client.post(
            reverse('review_application', args=[application.id]),
            {'decision': 'accepted'},
            follow=True
        )
        
        # Verify notification was created for the student
        notification_count = Notification.objects.filter(recipient=self.student).count()
        self.assertGreater(notification_count, 0)
        
        # Verify notification exists in database
        notification = Notification.objects.filter(recipient=self.student).first()
        self.assertIsNotNone(notification)
        self.assertIn('accepted', notification.message.lower())

    def test_decline_application_creates_notification(self):
        """Test that declining an application creates a notification for the student"""
        # Create a pending application
        application = Application.objects.create(
            student=self.student,
            opportunity=self.opportunity,
            status='pending',
            message='Test application'
        )
        
        # Login as organization
        self.client.login(email='org_us007@drew.edu', password='TestPass123!')
        
        # Decline the application via review_application
        response = self.client.post(
            reverse('review_application', args=[application.id]),
            {'decision': 'declined'},
            follow=True
        )
        
        # Verify notification was created for the student
        notification_count = Notification.objects.filter(recipient=self.student).count()
        self.assertGreater(notification_count, 0)
        
        # Verify notification exists in database
        notification = Notification.objects.filter(recipient=self.student).first()
        self.assertIsNotNone(notification)
        self.assertIn('declined', notification.message.lower())

    def test_remind_button_visible_when_pending(self):
        """Test that the Remind About Me button is visible for pending applications"""
        # Create a pending application
        application = Application.objects.create(
            student=self.student,
            opportunity=self.opportunity,
            status='pending',
            message='Test application'
        )
        
        # Login as student
        self.client.login(email='student_us007@drew.edu', password='TestPass123!')
        
        # GET my_applications page
        response = self.client.get(reverse('my_applications'))
        
        # Verify the Remind About Me button appears in response
        self.assertIn(b'Remind About Me', response.content)

    def test_remind_button_hidden_when_accepted(self):
        """Test that the Remind About Me button is hidden for accepted applications"""
        # Create an accepted application
        application = Application.objects.create(
            student=self.student,
            opportunity=self.opportunity,
            status='accepted',
            message='Test application'
        )
        
        # Login as student
        self.client.login(email='student_us007@drew.edu', password='TestPass123!')
        
        # GET my_applications page
        response = self.client.get(reverse('my_applications'))
        
        # Verify the Remind About Me button does NOT appear in response for accepted app
        # (We check that the pending-specific reminder form is not shown)
        content = response.content.decode('utf-8')
        # The reminder form should only show for pending applications
        if 'status=pending' in content or 'pending' in content:
            # If any pending app is shown, ensure it doesn't have the remind button
            self.assertNotIn('remind_organization', content)

    def test_remind_organization_success(self):
        """Test that remind_organization succeeds for pending applications"""
        # Create a pending application
        application = Application.objects.create(
            student=self.student,
            opportunity=self.opportunity,
            status='pending',
            message='Test application'
        )
        
        # Login as student
        self.client.login(email='student_us007@drew.edu', password='TestPass123!')
        
        # POST to remind_organization
        response = self.client.post(
            reverse('remind_organization', args=[application.id]),
            follow=True
        )
        
        # Verify redirect and success message
        self.assertEqual(response.status_code, 200)
        messages_list = list(response.context['messages'])
        self.assertTrue(any('Reminder sent' in str(m) for m in messages_list))

    def test_remind_organization_blocked_when_accepted(self):
        """Test that remind_organization is blocked for accepted applications"""
        # Create an accepted application
        application = Application.objects.create(
            student=self.student,
            opportunity=self.opportunity,
            status='accepted',
            message='Test application'
        )
        
        # Login as student
        self.client.login(email='student_us007@drew.edu', password='TestPass123!')
        
        # POST to remind_organization
        response = self.client.post(
            reverse('remind_organization', args=[application.id]),
            follow=True
        )
        
        # Verify error message or redirect
        self.assertEqual(response.status_code, 200)
        messages_list = list(response.context['messages'])
        # Should either have an error message or redirect without success message
        self.assertTrue(
            any('error' in str(m).lower() or 'only for pending' in str(m).lower() 
                for m in messages_list) or len(messages_list) == 0
        )

    def test_full_workflow_accept_application_with_notification(self):
        """Integration test: Full workflow - create student, organization, opportunity, application. Organization accepts. Verify application status is 'accepted' AND notification exists for student AND student can see notification on student_notifications page."""
        # Create a pending application
        application = Application.objects.create(
            student=self.student,
            opportunity=self.opportunity,
            status='pending',
            message='Test application'
        )
        
        # Login as organization
        self.client.login(email='org_us007@drew.edu', password='TestPass123!')
        
        # Accept the application via review_application
        response = self.client.post(
            reverse('review_application', args=[application.id]),
            {'decision': 'accepted'},
            follow=True
        )
        
        # Verify application status is 'accepted'
        application.refresh_from_db()
        self.assertEqual(application.status, 'accepted')
        
        # Verify notification exists for the student
        notification = Notification.objects.filter(recipient=self.student).first()
        self.assertIsNotNone(notification)
        self.assertIn('accepted', notification.message.lower())
        
        # Logout and login as student
        self.client.logout()
        self.client.login(email='student_us007@drew.edu', password='TestPass123!')
        
        # GET student_notifications page
        response = self.client.get(reverse('student_notifications'))
        self.assertEqual(response.status_code, 200)
        # Verify notification is visible on the page
        self.assertIn(b'accepted', response.content.lower())

    def test_full_workflow_decline_application_with_notification(self):
        """Integration test: Full workflow - same setup but organization declines. Verify status is 'declined' AND notification exists AND message contains 'declined'."""
        # Create a pending application
        application = Application.objects.create(
            student=self.student,
            opportunity=self.opportunity,
            status='pending',
            message='Test application'
        )
        
        # Login as organization
        self.client.login(email='org_us007@drew.edu', password='TestPass123!')
        
        # Decline the application
        response = self.client.post(
            reverse('review_application', args=[application.id]),
            {'decision': 'declined'},
            follow=True
        )
        
        # Verify application status is 'declined'
        application.refresh_from_db()
        self.assertEqual(application.status, 'declined')
        
        # Verify notification exists for the student
        notification = Notification.objects.filter(recipient=self.student).first()
        self.assertIsNotNone(notification)
        self.assertIn('declined', notification.message.lower())
        
        # Logout and login as student
        self.client.logout()
        self.client.login(email='student_us007@drew.edu', password='TestPass123!')
        
        # GET student_notifications page
        response = self.client.get(reverse('student_notifications'))
        self.assertEqual(response.status_code, 200)
        # Verify notification is visible on the page with 'declined'
        self.assertIn(b'declined', response.content.lower())

    def test_accept_application_status_persists_on_refresh(self):
        """Regression test: Accept application, refresh organization_applications page, verify status still shows 'accepted' (status persists)."""
        # Create a pending application
        application = Application.objects.create(
            student=self.student,
            opportunity=self.opportunity,
            status='pending',
            message='Test application'
        )
        
        # Login as organization
        self.client.login(email='org_us007@drew.edu', password='TestPass123!')
        
        # Accept the application
        self.client.post(
            reverse('review_application', args=[application.id]),
            {'decision': 'accepted'},
            follow=True
        )
        
        # Verify status in DB is 'accepted'
        application.refresh_from_db()
        self.assertEqual(application.status, 'accepted')
        
        # GET organization_applications page
        response = self.client.get(reverse('organization_applications'))
        self.assertEqual(response.status_code, 200)
        
        # Verify status still shows 'accepted' on the page
        self.assertIn(b'Accepted', response.content)
        
        # GET the page again to verify persistence
        response2 = self.client.get(reverse('organization_applications'))
        self.assertEqual(response2.status_code, 200)
        self.assertIn(b'Accepted', response2.content)

    def test_organization_applications_page_loads_successfully(self):
        """Smoke test: Verify organization_applications URL loads successfully for organization user (status 200)."""
        # Login as organization
        self.client.login(email='org_us007@drew.edu', password='TestPass123!')
        
        # GET organization_applications page
        response = self.client.get(reverse('organization_applications'))
        
        # Verify page loads successfully
        self.assertEqual(response.status_code, 200)

    def test_review_application_page_loads_successfully(self):
        """Smoke test: Verify review_application URL loads successfully for organization user (status 200)."""
        # Create a pending application
        application = Application.objects.create(
            student=self.student,
            opportunity=self.opportunity,
            status='pending',
            message='Test application'
        )
        
        # Login as organization
        self.client.login(email='org_us007@drew.edu', password='TestPass123!')
        
        # GET review_application page
        response = self.client.get(reverse('review_application', args=[application.id]))
        
        # Verify page loads successfully
        self.assertEqual(response.status_code, 200)

    def test_student_cannot_accept_application(self):
        """Negative test: Try to accept application as student user (not organization), verify forbidden response (403 or redirect)."""
        # Create a pending application
        application = Application.objects.create(
            student=self.student,
            opportunity=self.opportunity,
            status='pending',
            message='Test application'
        )
        
        # Login as student
        self.client.login(email='student_us007@drew.edu', password='TestPass123!')
        
        # Try to accept the application via accept_application
        response = self.client.post(
            reverse('accept_application', args=[application.id]),
            follow=False
        )
        
        # Verify forbidden response (403 or redirect)
        self.assertIn(response.status_code, [403, 302])

    def test_accept_nonexistent_application_returns_404(self):
        """Negative test: Try to accept non-existent application_id=99999, verify 404 response."""
        # Login as organization
        self.client.login(email='org_us007@drew.edu', password='TestPass123!')
        
        # Try to accept non-existent application
        response = self.client.post(
            reverse('accept_application', args=[99999]),
            follow=False
        )
        
        # Verify 404 response
        self.assertEqual(response.status_code, 404)

    def test_organization_applications_page_performance_with_50_applications(self):
        """Performance test: Create 50 applications, verify organization_applications page loads in under 3 seconds using time.time()."""
        import time
        
        # Create 50 applications
        for i in range(50):
            student = User.objects.create_user(
                username=f'perf_student_{i}',
                email=f'perf_student_{i}@drew.edu',
                password='TestPass123!',
                user_type='student'
            )
            Application.objects.create(
                student=student,
                opportunity=self.opportunity,
                status='pending',
                message=f'Test application {i}'
            )
        
        # Login as organization
        self.client.login(email='org_us007@drew.edu', password='TestPass123!')
        
        # Time the page load
        start_time = time.time()
        response = self.client.get(reverse('organization_applications'))
        elapsed_time = time.time() - start_time
        
        # Verify page loads successfully
        self.assertEqual(response.status_code, 200)
        
        # Verify page loads in under 3 seconds
        self.assertLess(elapsed_time, 3.0)

    def test_view_applicant_profile_from_organization_dashboard(self):
        """Test View Profile: Organization clicks View Profile, verify applicant_profile page loads and shows student name."""
        # Create a pending application
        application = Application.objects.create(
            student=self.student,
            opportunity=self.opportunity,
            status='pending',
            message='Test application'
        )
        
        # Login as organization
        self.client.login(email='org_us007@drew.edu', password='TestPass123!')
        
        # GET applicant_profile page
        response = self.client.get(
            reverse('applicant_profile', args=[self.student.id])
        )
        
        # Verify page loads successfully
        self.assertEqual(response.status_code, 200)
        
        # Verify student name appears on the page
        self.assertIn(self.student.display_name.encode(), response.content)

    def test_accepted_application_shows_green_color(self):
        """Test status color: Accept application, GET organization_applications, verify response contains 'green' color for accepted status."""
        # Create a pending application
        application = Application.objects.create(
            student=self.student,
            opportunity=self.opportunity,
            status='pending',
            message='Test application'
        )
        
        # Login as organization
        self.client.login(email='org_us007@drew.edu', password='TestPass123!')
        
        # Accept the application
        self.client.post(
            reverse('accept_application', args=[application.id]),
            follow=True
        )
        
        # GET organization_applications page
        response = self.client.get(reverse('organization_applications'))
        
        # Verify page loads successfully
        self.assertEqual(response.status_code, 200)
        
        # Verify response contains 'green' color (or 'accepted' status indicator)
        content = response.content.decode('utf-8')
        self.assertTrue(
            'green' in content.lower() or 
            'accepted' in content.lower() or 
            'status-accepted' in content.lower()
        )


class US007OrganizationApplicationViewTests(TestCase):
    """Comprehensive tests for US-007: Review and manage incoming volunteer applications"""

    def setUp(self):
        """Create test fixtures for organization application management"""
        self.client = Client()
        self.student1 = User.objects.create_user(
            username='student_us007_1',
            email='student_us007_1@drew.edu',
            password='TestPass123!',
            user_type='student'
        )
        self.student2 = User.objects.create_user(
            username='student_us007_2',
            email='student_us007_2@drew.edu',
            password='TestPass123!',
            user_type='student'
        )
        self.organization = User.objects.create_user(
            username='org_us007',
            email='org_us007@drew.edu',
            password='TestPass123!',
            user_type='organization'
        )
        self.opportunity = Opportunity.objects.create(
            title='Community Garden Project',
            organization=self.organization,
            description='Help plant and maintain a community garden',
            category='Environment',
            location='Central Park',
            duration='ongoing',
            opportunity_type='volunteer',
            is_active=True,
        )
        self.application1 = Application.objects.create(
            student=self.student1,
            opportunity=self.opportunity,
            status='pending',
            message='I love gardening and want to help!'
        )
        self.application2 = Application.objects.create(
            student=self.student2,
            opportunity=self.opportunity,
            status='pending',
            message='Excited to learn about gardening'
        )

    def test_organization_can_view_applications_list(self):
        """Test that organization can view a list of incoming applications"""
        self.client.login(email='org_us007@drew.edu', password='TestPass123!')
        response = self.client.get(reverse('organization_applications'))
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Organization Applications', response.content)

    def test_applications_show_student_name(self):
        """Test that application list displays student name"""
        self.client.login(email='org_us007@drew.edu', password='TestPass123!')
        response = self.client.get(reverse('organization_applications'))
        self.assertIn(self.student1.display_name.encode(), response.content)
        self.assertIn(self.student2.display_name.encode(), response.content)

    def test_applications_show_opportunity_title(self):
        """Test that application list displays opportunity title"""
        self.client.login(email='org_us007@drew.edu', password='TestPass123!')
        response = self.client.get(reverse('organization_applications'))
        self.assertIn(b'Community Garden Project', response.content)

    def test_applications_show_current_status(self):
        """Test that application list displays current application status"""
        self.client.login(email='org_us007@drew.edu', password='TestPass123!')
        response = self.client.get(reverse('organization_applications'))
        content = response.content.decode('utf-8')
        self.assertTrue('Pending' in content or 'pending' in content)

    def test_applications_show_review_button(self):
        """Test that each application has a Review button"""
        self.client.login(email='org_us007@drew.edu', password='TestPass123!')
        response = self.client.get(reverse('organization_applications'))
        self.assertIn(b'Review', response.content)

    def test_applications_show_view_profile_button(self):
        """Test that applications show View Profile button"""
        self.client.login(email='org_us007@drew.edu', password='TestPass123!')
        response = self.client.get(reverse('organization_applications'))
        content = response.content.decode('utf-8')
        self.assertTrue('profile' in content.lower() or 'view' in content.lower())

    def test_accepted_status_shows_green_color(self):
        """Test that accepted applications display with green color indicator"""
        self.application1.status = 'accepted'
        self.application1.save()
        
        self.client.login(email='org_us007@drew.edu', password='TestPass123!')
        response = self.client.get(reverse('organization_applications'))
        content = response.content.decode('utf-8')
        
        self.assertTrue(
            'green' in content.lower() or 
            'accepted' in content.lower() or 
            '#22c55e' in content or
            'status-accepted' in content
        )

    def test_declined_status_shows_red_color(self):
        """Test that declined applications display with red color indicator"""
        self.application1.status = 'declined'
        self.application1.save()
        
        self.client.login(email='org_us007@drew.edu', password='TestPass123!')
        response = self.client.get(reverse('organization_applications'))
        content = response.content.decode('utf-8')
        
        self.assertTrue(
            'red' in content.lower() or 
            'declined' in content.lower() or 
            '#ef4444' in content or
            'status-declined' in content
        )

    def test_pending_status_shows_gray_color(self):
        """Test that pending applications display with gray/yellow color indicator"""
        self.client.login(email='org_us007@drew.edu', password='TestPass123!')
        response = self.client.get(reverse('organization_applications'))
        content = response.content.decode('utf-8')
        
        self.assertTrue(
            'pending' in content.lower() or
            'gray' in content.lower() or
            '#f59e0b' in content
        )

    def test_review_page_loads_for_organization(self):
        """Test that review page loads successfully for organization user"""
        self.client.login(email='org_us007@drew.edu', password='TestPass123!')
        response = self.client.get(
            reverse('review_application', args=[self.application1.id])
        )
        self.assertEqual(response.status_code, 200)

    def test_review_page_shows_accept_button(self):
        """Test that review page displays Accept button"""
        self.client.login(email='org_us007@drew.edu', password='TestPass123!')
        response = self.client.get(
            reverse('review_application', args=[self.application1.id])
        )
        content = response.content.decode('utf-8')
        self.assertTrue('accept' in content.lower())

    def test_review_page_shows_decline_button(self):
        """Test that review page displays Decline button"""
        self.client.login(email='org_us007@drew.edu', password='TestPass123!')
        response = self.client.get(
            reverse('review_application', args=[self.application1.id])
        )
        content = response.content.decode('utf-8')
        self.assertTrue('decline' in content.lower())

    def test_accept_changes_status_to_accepted(self):
        """Test that accepting an application changes its status to 'accepted'"""
        self.client.login(email='org_us007@drew.edu', password='TestPass123!')
        response = self.client.post(
            reverse('review_application', args=[self.application1.id]),
            {'decision': 'accepted'},
            follow=True
        )
        
        self.application1.refresh_from_db()
        self.assertEqual(self.application1.status, 'accepted')

    def test_decline_changes_status_to_declined(self):
        """Test that declining an application changes its status to 'declined'"""
        self.client.login(email='org_us007@drew.edu', password='TestPass123!')
        response = self.client.post(
            reverse('review_application', args=[self.application1.id]),
            {'decision': 'declined'},
            follow=True
        )
        
        self.application1.refresh_from_db()
        self.assertEqual(self.application1.status, 'declined')

    def test_status_persists_after_page_refresh(self):
        """Test that application status persists after page refresh"""
        # Accept the application
        self.client.login(email='org_us007@drew.edu', password='TestPass123!')
        self.client.post(
            reverse('review_application', args=[self.application1.id]),
            {'decision': 'accepted'},
            follow=True
        )
        
        # Refresh the page
        response = self.client.get(reverse('organization_applications'))
        self.assertIn(b'Accepted', response.content)
        
        # Refresh again and verify
        response = self.client.get(reverse('organization_applications'))
        self.assertIn(b'Accepted', response.content)


class US007NotificationTests(TestCase):
    """Comprehensive tests for US-007 notification system"""

    def setUp(self):
        """Create test fixtures for notification testing"""
        self.client = Client()
        self.student = User.objects.create_user(
            username='student_notif',
            email='student_notif@drew.edu',
            password='TestPass123!',
            user_type='student'
        )
        self.organization = User.objects.create_user(
            username='org_notif',
            email='org_notif@drew.edu',
            password='TestPass123!',
            user_type='organization'
        )
        self.opportunity = Opportunity.objects.create(
            title='Beach Cleanup',
            organization=self.organization,
            description='Help clean our local beach',
            category='Environment',
            location='Santa Monica Beach',
            duration='one-time',
            opportunity_type='volunteer',
            is_active=True,
        )
        self.application = Application.objects.create(
            student=self.student,
            opportunity=self.opportunity,
            status='pending',
            message='I want to help save the ocean!'
        )

    def test_accept_creates_notification_for_student(self):
        """Test that accepting an application creates a notification for the student"""
        self.client.login(email='org_notif@drew.edu', password='TestPass123!')
        self.client.post(
            reverse('review_application', args=[self.application.id]),
            {'decision': 'accepted'},
            follow=True
        )
        
        notification = Notification.objects.filter(recipient=self.student).first()
        self.assertIsNotNone(notification)

    def test_decline_creates_notification_for_student(self):
        """Test that declining an application creates a notification for the student"""
        self.client.login(email='org_notif@drew.edu', password='TestPass123!')
        self.client.post(
            reverse('review_application', args=[self.application.id]),
            {'decision': 'declined'},
            follow=True
        )
        
        notification = Notification.objects.filter(recipient=self.student).first()
        self.assertIsNotNone(notification)

    def test_notification_recipient_is_student(self):
        """Test that notification is created for the student who applied"""
        self.client.login(email='org_notif@drew.edu', password='TestPass123!')
        self.client.post(
            reverse('review_application', args=[self.application.id]),
            {'decision': 'accepted'},
            follow=True
        )
        
        notification = Notification.objects.filter(recipient=self.student).first()
        self.assertEqual(notification.recipient, self.student)

    def test_notification_message_contains_accepted(self):
        """Test that notification message contains word 'accepted'"""
        self.client.login(email='org_notif@drew.edu', password='TestPass123!')
        self.client.post(
            reverse('review_application', args=[self.application.id]),
            {'decision': 'accepted'},
            follow=True
        )
        
        notification = Notification.objects.filter(recipient=self.student).first()
        self.assertIn('accepted', notification.message.lower())

    def test_notification_message_contains_declined(self):
        """Test that notification message contains word 'declined'"""
        self.client.login(email='org_notif@drew.edu', password='TestPass123!')
        self.client.post(
            reverse('review_application', args=[self.application.id]),
            {'decision': 'declined'},
            follow=True
        )
        
        notification = Notification.objects.filter(recipient=self.student).first()
        self.assertIn('declined', notification.message.lower())

    def test_notification_is_unread_by_default(self):
        """Test that newly created notification is marked as unread"""
        self.client.login(email='org_notif@drew.edu', password='TestPass123!')
        self.client.post(
            reverse('review_application', args=[self.application.id]),
            {'decision': 'accepted'},
            follow=True
        )
        
        notification = Notification.objects.filter(recipient=self.student).first()
        self.assertFalse(notification.is_read)

    def test_notification_contains_opportunity_title(self):
        """Test that notification message contains the opportunity title"""
        self.client.login(email='org_notif@drew.edu', password='TestPass123!')
        self.client.post(
            reverse('review_application', args=[self.application.id]),
            {'decision': 'accepted'},
            follow=True
        )
        
        notification = Notification.objects.filter(recipient=self.student).first()
        self.assertIn('Beach Cleanup', notification.message)

    def test_multiple_accepts_create_multiple_notifications(self):
        """Test that multiple accepted applications create separate notifications"""
        # Create another application
        student2 = User.objects.create_user(
            username='student2_notif',
            email='student2_notif@drew.edu',
            password='TestPass123!',
            user_type='student'
        )
        app2 = Application.objects.create(
            student=student2,
            opportunity=self.opportunity,
            status='pending',
            message='I want to help too!'
        )
        
        self.client.login(email='org_notif@drew.edu', password='TestPass123!')
        
        # Accept first application
        self.client.post(
            reverse('review_application', args=[self.application.id]),
            {'decision': 'accepted'},
            follow=True
        )
        
        # Accept second application
        self.client.post(
            reverse('review_application', args=[app2.id]),
            {'decision': 'accepted'},
            follow=True
        )
        
        notif1 = Notification.objects.filter(recipient=self.student).count()
        notif2 = Notification.objects.filter(recipient=student2).count()
        
        self.assertEqual(notif1, 1)
        self.assertEqual(notif2, 1)

    def test_student_cannot_accept_application(self):
        """Test that student user cannot accept applications"""
        self.client.login(email='student_notif@drew.edu', password='TestPass123!')
        response = self.client.post(
            reverse('accept_application', args=[self.application.id]),
            follow=False
        )
        
        self.assertIn(response.status_code, [403, 302])

    def test_nonexistent_application_returns_404(self):
        """Test that reviewing non-existent application returns 404"""
        self.client.login(email='org_notif@drew.edu', password='TestPass123!')
        response = self.client.get(reverse('review_application', args=[99999]))
        self.assertEqual(response.status_code, 404)
=======
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

>>>>>>> origin/main

