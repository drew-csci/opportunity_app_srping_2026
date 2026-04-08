from django.test import TestCase, Client
from django.urls import reverse
from accounts.models import User
from .models import OrganizationFollow
import json


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
