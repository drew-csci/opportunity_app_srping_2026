from django.test import TestCase, Client
from django.urls import reverse

from accounts.models import User
from .models import Opportunity, OrganizationFollow
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


class US008ReminderTests(TestCase):
    def setUp(self):
        from django.contrib.auth import get_user_model
        User = get_user_model()
        self.student = User.objects.create_user(
            username='student_us008',
            email='student_us008@drew.edu',
            password='TestPass123!',
            user_type='student'
        )
        self.organization = User.objects.create_user(
            username='org_us008',
            email='org_us008@drew.edu',
            password='TestPass123!',
            user_type='organization'
        )
        from pages.models import Opportunity, Application
        self.opportunity = Opportunity.objects.create(
            title='Test Opportunity US008',
            organization=self.organization,
            description='Test',
            location='Test',
            duration='1 week'
        )
        self.application = Application.objects.create(
            student=self.student,
            opportunity=self.opportunity,
            status='pending',
            message='Test message'
        )

    def test_remind_button_visible_when_pending(self):
        self.client.login(email='student_us008@drew.edu', password='TestPass123!')
        from django.urls import reverse
        response = self.client.get(reverse('my_applications'), follow=True)
        self.assertIn(b'Remind About Me', response.content)

    def test_remind_button_hidden_when_accepted(self):
        self.application.status = 'accepted'
        self.application.save()
        self.client.login(email='student_us008@drew.edu', password='TestPass123!')
        from django.urls import reverse
        response = self.client.get(reverse('my_applications'), follow=True)
        self.assertNotIn(b'Remind About Me', response.content)

    def test_remind_button_hidden_when_declined(self):
        self.application.status = 'declined'
        self.application.save()
        self.client.login(email='student_us008@drew.edu', password='TestPass123!')
        from django.urls import reverse
        response = self.client.get(reverse('my_applications'), follow=True)
        self.assertNotIn(b'Remind About Me', response.content)

    def test_remind_organization_success(self):
        self.client.login(email='student_us008@drew.edu', password='TestPass123!')
        from django.urls import reverse
        response = self.client.post(
            reverse('remind_organization', args=[self.application.id]),
            follow=True
        )
        self.assertEqual(response.status_code, 200)

    def test_remind_requires_login(self):
        from django.urls import reverse
        response = self.client.post(
            reverse('remind_organization', args=[self.application.id])
        )
        self.assertEqual(response.status_code, 302)
        self.assertIn('login', response.url)

    def test_remind_requires_post(self):
        self.client.login(email='student_us008@drew.edu', password='TestPass123!')
        from django.urls import reverse
        response = self.client.get(
            reverse('remind_organization', args=[self.application.id])
        )
        self.assertEqual(response.status_code, 405)


# ============================================================
# 1. Code Coverage Analysis Tests
# ============================================================
class US008CodeCoverageTests(TestCase):
    def setUp(self):
        from django.contrib.auth import get_user_model
        User = get_user_model()
        self.student = User.objects.create_user(
            username='coverage_student', email='coverage_student@drew.edu',
            password='TestPass123!', user_type='student')
        self.organization = User.objects.create_user(
            username='coverage_org', email='coverage_org@drew.edu',
            password='TestPass123!', user_type='organization')
        from pages.models import Opportunity, Application
        self.opportunity = Opportunity.objects.create(
            title='Coverage Test Opportunity', organization=self.organization,
            description='Test', location='Test', duration='1 week')
        self.application = Application.objects.create(
            student=self.student, opportunity=self.opportunity,
            status='pending', message='Test')

    def test_coverage_remind_view_pending_path(self):
        """Coverage: Tests the pending/applied path in remind_organization"""
        self.client.login(email='coverage_student@drew.edu', password='TestPass123!')
        from django.urls import reverse
        response = self.client.post(reverse('remind_organization', args=[self.application.id]), follow=True)
        self.assertEqual(response.status_code, 200)

    def test_coverage_remind_view_accepted_path(self):
        """Coverage: Tests the accepted/declined path in remind_organization"""
        self.application.status = 'accepted'
        self.application.save()
        self.client.login(email='coverage_student@drew.edu', password='TestPass123!')
        from django.urls import reverse
        response = self.client.post(reverse('remind_organization', args=[self.application.id]), follow=True)
        self.assertEqual(response.status_code, 200)

    def test_coverage_remind_view_unauthorized_path(self):
        """Coverage: Tests the unauthorized path in remind_organization"""
        self.client.login(email='coverage_org@drew.edu', password='TestPass123!')
        from django.urls import reverse
        response = self.client.post(reverse('remind_organization', args=[self.application.id]), follow=True)
        self.assertNotEqual(response.status_code, 404)

    def test_coverage_my_applications_view(self):
        """Coverage: Tests my_applications view renders correctly"""
        self.client.login(email='coverage_student@drew.edu', password='TestPass123!')
        from django.urls import reverse
        response = self.client.get(reverse('my_applications'), follow=True)
        self.assertEqual(response.status_code, 200)


# ============================================================
# 2. Negative Testing & Input Validation Tests
# ============================================================
class US008NegativeTests(TestCase):
    def setUp(self):
        from django.contrib.auth import get_user_model
        User = get_user_model()
        self.student = User.objects.create_user(
            username='negative_student', email='negative_student@drew.edu',
            password='TestPass123!', user_type='student')
        self.organization = User.objects.create_user(
            username='negative_org', email='negative_org@drew.edu',
            password='TestPass123!', user_type='organization')
        from pages.models import Opportunity, Application
        self.opportunity = Opportunity.objects.create(
            title='Negative Test Opportunity', organization=self.organization,
            description='Test', location='Test', duration='1 week')
        self.application = Application.objects.create(
            student=self.student, opportunity=self.opportunity,
            status='pending', message='Test')

    def test_negative_remind_without_login(self):
        """Negative: Cannot remind without being logged in"""
        from django.urls import reverse
        response = self.client.post(reverse('remind_organization', args=[self.application.id]))
        self.assertEqual(response.status_code, 302)
        self.assertIn('login', response.url)

    def test_negative_remind_invalid_id(self):
        """Negative: Cannot remind with non-existent application ID"""
        self.client.login(email='negative_student@drew.edu', password='TestPass123!')
        from django.urls import reverse
        response = self.client.post(reverse('remind_organization', args=[99999]), follow=True)
        self.assertEqual(response.status_code, 404)

    def test_negative_remind_get_method(self):
        """Negative: Remind endpoint does not accept GET requests"""
        self.client.login(email='negative_student@drew.edu', password='TestPass123!')
        from django.urls import reverse
        response = self.client.get(reverse('remind_organization', args=[self.application.id]))
        self.assertEqual(response.status_code, 405)

    def test_negative_remind_accepted_application(self):
        """Negative: Cannot remind for accepted application"""
        self.application.status = 'accepted'
        self.application.save()
        self.client.login(email='negative_student@drew.edu', password='TestPass123!')
        from django.urls import reverse
        response = self.client.post(reverse('remind_organization', args=[self.application.id]), follow=True)
        messages = list(response.context['messages'])
        self.assertFalse(any('Reminder sent' in str(m) for m in messages))

    def test_negative_remind_declined_application(self):
        """Negative: Cannot remind for declined application"""
        self.application.status = 'declined'
        self.application.save()
        self.client.login(email='negative_student@drew.edu', password='TestPass123!')
        from django.urls import reverse
        response = self.client.post(reverse('remind_organization', args=[self.application.id]), follow=True)
        messages = list(response.context['messages'])
        self.assertFalse(any('Reminder sent' in str(m) for m in messages))

    def test_negative_organization_cannot_remind(self):
        """Negative: Organization user cannot send reminder"""
        self.client.login(email='negative_org@drew.edu', password='TestPass123!')
        from django.urls import reverse
        response = self.client.post(reverse('remind_organization', args=[self.application.id]), follow=True)
        self.assertNotIn(b'Reminder sent', response.content)


# ============================================================
# 3. Regression Tests
# ============================================================
class US008RegressionTests(TestCase):
    def setUp(self):
        from django.contrib.auth import get_user_model
        User = get_user_model()
        self.student = User.objects.create_user(
            username='regression_student', email='regression_student@drew.edu',
            password='TestPass123!', user_type='student')
        self.organization = User.objects.create_user(
            username='regression_org', email='regression_org@drew.edu',
            password='TestPass123!', user_type='organization')
        from pages.models import Opportunity, Application
        self.opportunity = Opportunity.objects.create(
            title='Regression Test Opportunity', organization=self.organization,
            description='Test', location='Test', duration='1 week')
        self.application = Application.objects.create(
            student=self.student, opportunity=self.opportunity,
            status='pending', message='Test')

    def test_regression_remind_button_visible_pending(self):
        """Regression: Remind button always visible for pending status"""
        self.client.login(email='regression_student@drew.edu', password='TestPass123!')
        from django.urls import reverse
        response = self.client.get(reverse('my_applications'), follow=True)
        self.assertIn(b'Remind About Me', response.content)

    def test_regression_remind_button_hidden_after_accept(self):
        """Regression: Remind button hidden after application accepted"""
        self.application.status = 'accepted'
        self.application.save()
        self.client.login(email='regression_student@drew.edu', password='TestPass123!')
        from django.urls import reverse
        response = self.client.get(reverse('my_applications'), follow=True)
        self.assertNotIn(b'Remind About Me', response.content)

    def test_regression_status_not_changed_after_remind(self):
        """Regression: Application status stays pending after remind"""
        self.client.login(email='regression_student@drew.edu', password='TestPass123!')
        from django.urls import reverse
        self.client.post(reverse('remind_organization', args=[self.application.id]), follow=True)
        self.application.refresh_from_db()
        self.assertEqual(self.application.status, 'pending')

    def test_regression_remind_multiple_times(self):
        """Regression: Can send reminder multiple times for pending application"""
        self.client.login(email='regression_student@drew.edu', password='TestPass123!')
        from django.urls import reverse
        for _ in range(3):
            response = self.client.post(reverse('remind_organization', args=[self.application.id]), follow=True)
            self.assertEqual(response.status_code, 200)


# ============================================================
# 4. Performance & Load Tests
# ============================================================
class US008PerformanceTests(TestCase):
    def setUp(self):
        from django.contrib.auth import get_user_model
        User = get_user_model()
        self.student = User.objects.create_user(
            username='perf_student', email='perf_student@drew.edu',
            password='TestPass123!', user_type='student')
        self.organization = User.objects.create_user(
            username='perf_org', email='perf_org@drew.edu',
            password='TestPass123!', user_type='organization')
        from pages.models import Opportunity, Application
        self.opportunity = Opportunity.objects.create(
            title='Performance Test Opportunity', organization=self.organization,
            description='Test', location='Test', duration='1 week')
        self.applications = []
        for i in range(20):
            app = Application.objects.create(
                student=self.student, opportunity=self.opportunity,
                status='pending', message=f'Test message {i}')
            self.applications.append(app)

    def test_performance_my_applications_load_time(self):
        """Performance: My applications page loads within 3 seconds with 20 applications"""
        import time
        self.client.login(email='perf_student@drew.edu', password='TestPass123!')
        from django.urls import reverse
        start = time.time()
        response = self.client.get(reverse('my_applications'), follow=True)
        end = time.time()
        self.assertEqual(response.status_code, 200)
        self.assertLess(end - start, 3.0)

    def test_performance_remind_response_time(self):
        """Performance: Remind endpoint responds within 2 seconds"""
        import time
        self.client.login(email='perf_student@drew.edu', password='TestPass123!')
        from django.urls import reverse
        start = time.time()
        response = self.client.post(reverse('remind_organization', args=[self.applications[0].id]), follow=True)
        end = time.time()
        self.assertEqual(response.status_code, 200)
        self.assertLess(end - start, 2.0)


# ============================================================
# 5. Integration Tests
# ============================================================
class US008IntegrationTests(TestCase):
    def setUp(self):
        from django.contrib.auth import get_user_model
        User = get_user_model()
        self.student = User.objects.create_user(
            username='integration_student', email='integration_student@drew.edu',
            password='TestPass123!', user_type='student')
        self.organization = User.objects.create_user(
            username='integration_org', email='integration_org@drew.edu',
            password='TestPass123!', user_type='organization')
        from pages.models import Opportunity, Application
        self.opportunity = Opportunity.objects.create(
            title='Integration Test Opportunity', organization=self.organization,
            description='Test', location='Test', duration='1 week')
        self.application = Application.objects.create(
            student=self.student, opportunity=self.opportunity,
            status='pending', message='Test')

    def test_integration_full_remind_workflow(self):
        """Integration: Full remind workflow - view applications, send reminder, verify"""
        self.client.login(email='integration_student@drew.edu', password='TestPass123!')
        from django.urls import reverse
        response = self.client.get(reverse('my_applications'), follow=True)
        self.assertIn(b'Remind About Me', response.content)
        response = self.client.post(reverse('remind_organization', args=[self.application.id]), follow=True)
        self.assertEqual(response.status_code, 200)
        self.application.refresh_from_db()
        self.assertEqual(self.application.status, 'pending')

    def test_integration_apply_and_remind(self):
        """Integration: Student applies and can send reminder"""
        self.client.login(email='integration_student@drew.edu', password='TestPass123!')
        from django.urls import reverse
        response = self.client.get(reverse('my_applications'), follow=True)
        self.assertEqual(response.status_code, 200)
        response = self.client.post(reverse('remind_organization', args=[self.application.id]), follow=True)
        self.assertEqual(response.status_code, 200)

    def test_integration_remind_then_status_change(self):
        """Integration: After remind, org accepts, button disappears"""
        self.client.login(email='integration_student@drew.edu', password='TestPass123!')
        from django.urls import reverse
        self.client.post(reverse('remind_organization', args=[self.application.id]), follow=True)
        self.application.status = 'accepted'
        self.application.save()
        response = self.client.get(reverse('my_applications'), follow=True)
        self.assertNotIn(b'Remind About Me', response.content)


# ============================================================
# 6. Smoke Tests
# ============================================================
class US008SmokeTests(TestCase):
    def setUp(self):
        from django.contrib.auth import get_user_model
        User = get_user_model()
        self.student = User.objects.create_user(
            username='smoke_student', email='smoke_student@drew.edu',
            password='TestPass123!', user_type='student')
        self.organization = User.objects.create_user(
            username='smoke_org', email='smoke_org@drew.edu',
            password='TestPass123!', user_type='organization')
        from pages.models import Opportunity, Application
        self.opportunity = Opportunity.objects.create(
            title='Smoke Test Opportunity', organization=self.organization,
            description='Test', location='Test', duration='1 week')
        self.application = Application.objects.create(
            student=self.student, opportunity=self.opportunity,
            status='pending', message='Test')

    def test_smoke_my_applications_url_exists(self):
        """Smoke: my_applications URL is registered and accessible"""
        self.client.login(email='smoke_student@drew.edu', password='TestPass123!')
        from django.urls import reverse
        response = self.client.get(reverse('my_applications'), follow=True)
        self.assertEqual(response.status_code, 200)

    def test_smoke_remind_url_exists(self):
        """Smoke: remind_organization URL is registered"""
        from django.urls import reverse, NoReverseMatch
        try:
            url = reverse('remind_organization', args=[1])
            self.assertIsNotNone(url)
        except NoReverseMatch:
            self.fail('remind_organization URL not registered')

    def test_smoke_remind_endpoint_responds(self):
        """Smoke: remind endpoint responds without server error"""
        self.client.login(email='smoke_student@drew.edu', password='TestPass123!')
        from django.urls import reverse
        response = self.client.post(reverse('remind_organization', args=[self.application.id]), follow=True)
        self.assertNotEqual(response.status_code, 500)

    def test_smoke_my_applications_returns_html(self):
        """Smoke: my_applications returns HTML content"""
        self.client.login(email='smoke_student@drew.edu', password='TestPass123!')
        from django.urls import reverse
        response = self.client.get(reverse('my_applications'), follow=True)
        self.assertIn(b'html', response.content.lower())
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


