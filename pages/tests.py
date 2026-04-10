import datetime

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from .forms import VolunteerProfileForm
from .models import VolunteerExperience


class VolunteerProfileTests(TestCase):
    def test_volunteer_profile_form_valid_data(self):
        form = VolunteerProfileForm(data={
            'first_name': 'Jane',
            'last_name': 'Doe',
            'email': 'jane.doe@example.com',
            'phone': '555-1234',
            'bio': 'Experienced volunteer with a passion for community outreach.',
            'skills': 'Tutoring, Event Planning',
        })

        self.assertTrue(form.is_valid())
        self.assertEqual(form.cleaned_data['phone'], '555-1234')
        self.assertEqual(form.cleaned_data['email'], 'jane.doe@example.com')

    def test_volunteer_profile_form_missing_email_invalid(self):
        form = VolunteerProfileForm(data={
            'first_name': 'Jane',
            'last_name': 'Doe',
            'email': '',
            'phone': '555-1234',
            'bio': 'No email should fail validation.',
            'skills': 'Tutoring',
        })

        self.assertFalse(form.is_valid())
        self.assertIn('email', form.errors)

    def test_volunteer_profile_edit_and_experience_workflow_persists_after_logout(self):
        User = get_user_model()
        user = User.objects.create_user(
            username='jane',
            email='jane.doe@example.com',
            password='testpass123',
            first_name='Jane',
            last_name='Doe',
        )

        self.client.login(username=user.email, password='testpass123')

        profile_data = {
            'first_name': 'Jane',
            'last_name': 'Doe',
            'email': 'jane.doe@example.com',
            'phone': '555-9876',
            'bio': '',
            'skills': '',
        }
        response = self.client.post(reverse('volunteer_profile_edit'), profile_data)
        self.assertRedirects(response, reverse('volunteer_profile'))

        experience_data = {
            'organization_name': 'Helping Hands',
            'role': 'Volunteer Mentor',
            'description': 'Supporting community tutoring sessions.',
            'start_date': datetime.date.today().strftime('%Y-%m-%d'),
            'end_date': '',
            'is_current': 'on',
        }
        response = self.client.post(reverse('experience_add'), experience_data)
        self.assertRedirects(response, reverse('volunteer_profile_edit'))

        response = self.client.get(reverse('volunteer_profile'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Jane Doe')
        self.assertContains(response, 'jane.doe@example.com')
        self.assertContains(response, '555-9876')
        self.assertContains(response, 'Helping Hands')

        experience = VolunteerExperience.objects.filter(volunteer=user).first()
        self.assertIsNotNone(experience)

        response = self.client.post(reverse('experience_delete', args=[experience.pk]))
        self.assertRedirects(response, reverse('volunteer_profile_edit'))
        self.assertEqual(VolunteerExperience.objects.filter(volunteer=user).count(), 0)

        self.client.logout()
        self.assertFalse('_auth_user_id' in self.client.session)

        self.client.login(username=user.email, password='testpass123')
        response = self.client.get(reverse('volunteer_profile'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Jane Doe')
        self.assertContains(response, 'jane.doe@example.com')
        self.assertContains(response, '555-9876')
from django.test import TestCase, Client
from django.urls import reverse
from django.utils import timezone
from django.contrib.auth import get_user_model
from accounts.models import User
from .models import OrganizationFollow
from .models import Opportunity, Application
import json

User = get_user_model()

class ApplicationTrackingTests(TestCase): #$ Test case class for testing the application tracking functionality of the volunteer opportunity application
    def setUp(self):
        self.student = User.objects.create_user( # Create a test student user for the tests
            email='student@example.com',
            password='testpass',
            username='studentuser',
            user_type='student',
            first_name='Student',
            last_name='One',
        )
        self.organization = User.objects.create_user( # Create a test organization user for the tests
            email='org@example.com',
            password='testpass',
            username='orguser',
            user_type='organization',
            first_name='Org',
            last_name='One',
        )

        self.opportunity = Opportunity.objects.create( # Create a test volunteer opportunity linked to the organization user for the tests
            organization=self.organization,
            title='Volunteer Tutor',
            description='Help K-12 students',
            cause='Education',
            location='Remote',
            duration='3 months',
            skills_required='Teaching',
            opportunity_type='Volunteer',
            is_active=True,
        )

    def test_application_auto_responded_date_on_accept_and_deny(self): #$ Test that the responded_date is automatically set when an application status changes to accepted or denied
        app = Application.objects.create( # Create a test application with pending status for the student and opportunity
            student=self.student,
            opportunity=self.opportunity,
            status=Application.Status.PENDING,
            message='I would love to help',
        )

        self.assertIsNone(app.responded_date) # Initially, the responded_date should be None for a pending application

        app.status = Application.Status.ACCEPTED # Change the status to accepted and save the application
        app.save()
        self.assertEqual(app.status, Application.Status.ACCEPTED)
        self.assertIsNotNone(app.responded_date)

        # Now for denied path
        app2 = Application.objects.create( #    Create another test application with pending status for the student and opportunity
            student=self.student,
            opportunity=self.opportunity,
            status=Application.Status.PENDING,
            message='Another app',
        )
        app2.status = Application.Status.DENIED # Change the status to denied and save the application
        app2.save()
        self.assertEqual(app2.status, Application.Status.DENIED)
        self.assertIsNotNone(app2.responded_date)

    def test_apply_to_opportunity_submits_pending_and_save_draft(self): #$ Test that applying to an opportunity can submit an application as pending or save it as a draft based on the action taken
        self.client.force_login(self.student) # Log in as the test student user to perform the application actions

        # submit as pending
        url = reverse('apply_to_opportunity', args=[self.opportunity.id]) # Get the URL for applying to the opportunity
        response = self.client.post(url, {'message': 'I am interested', 'action': 'submit'}) # Post a request to apply to the opportunity with a message and action to submit

        application = Application.objects.get(student=self.student, opportunity=self.opportunity) # Retrieve the created application from the database for the student and opportunity
        self.assertRedirects(response, reverse('application_detail', args=[application.id])) # Assert that the response redirects to the application detail page for the created application
        self.assertEqual(application.status, Application.Status.PENDING)

        # create a new opportunity for draft test
        opp2 = Opportunity.objects.create(
            organization=self.organization,
            title='Community Clean-up',
            description='park clean-up',
            cause='Environment',
            location='Local',
            duration='1 day',
            skills_required='Physical',
            opportunity_type='Volunteer',
            is_active=True,
        )
        url2 = reverse('apply_to_opportunity', args=[opp2.id])
        response = self.client.post(url2, {'message': 'Draft message', 'action': 'save_draft'})
        draft_application = Application.objects.get(student=self.student, opportunity=opp2)
        self.assertEqual(draft_application.status, Application.Status.DRAFT)
        self.assertRedirects(response, reverse('application_detail', args=[draft_application.id]))

    def test_prevent_duplicate_apply_for_non_draft(self):
        existing = Application.objects.create(
            student=self.student,
            opportunity=self.opportunity,
            status=Application.Status.PENDING,
            message='Already applied',
        )
        self.client.force_login(self.student)
        url = reverse('apply_to_opportunity', args=[self.opportunity.id])
        response = self.client.get(url)
        self.assertRedirects(response, reverse('application_detail', args=[existing.id]))

        messages = list(response.wsgi_request._messages)
        self.assertTrue(any('already applied' in m.message.lower() for m in messages))

    def test_my_applications_student_only(self):
        Application.objects.create(student=self.student, opportunity=self.opportunity, status=Application.Status.PENDING, message='One')
        Application.objects.create(student=self.student, opportunity=self.opportunity, status=Application.Status.PENDING, message='Two')

        self.client.force_login(self.student)
        response = self.client.get(reverse('my_applications'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context['applications']), 2)

        self.client.force_login(self.organization)
        response = self.client.get(reverse('my_applications'))
        self.assertRedirects(response, reverse('screen1'))

    def test_organization_applications_filters_and_permission(self):
        Application.objects.create(student=self.student, opportunity=self.opportunity, status=Application.Status.DRAFT, message='Draft')
        Application.objects.create(student=self.student, opportunity=self.opportunity, status=Application.Status.PENDING, message='Pending')
        Application.objects.create(student=self.student, opportunity=self.opportunity, status=Application.Status.ACCEPTED, message='Accepted')

        self.client.force_login(self.organization)
        response = self.client.get(reverse('organization_applications'))
        self.assertEqual(response.status_code, 200)
        apps = response.context['applications']
        self.assertEqual(len(apps), 2)
        self.assertNotIn(Application.Status.DRAFT, [a.status for a in apps])

        self.client.force_login(self.student)
        response = self.client.get(reverse('organization_applications'))
        self.assertRedirects(response, reverse('screen1'))

    def test_review_application_status_change(self):
        app = Application.objects.create(student=self.student, opportunity=self.opportunity, status=Application.Status.PENDING, message='Review this')

        self.client.force_login(self.organization)
        response = self.client.post(reverse('review_application', args=[app.id]), {'decision': Application.Status.ACCEPTED})
        self.assertRedirects(response, reverse('organization_applications'))

        app.refresh_from_db()
        self.assertEqual(app.status, Application.Status.ACCEPTED)
        self.assertIsNotNone(app.responded_date)

        response_invalid = self.client.post(reverse('review_application', args=[app.id]), {'decision': 'notavalid'})
        self.assertEqual(response_invalid.status_code, 200)
        self.assertContains(response_invalid, 'Please choose a valid decision.')

    def test_opportunity_detail_shows_application_and_permission(self):
        app = Application.objects.create(student=self.student, opportunity=self.opportunity, status=Application.Status.PENDING, message='Detail test')

        self.client.force_login(self.student)
        response = self.client.get(reverse('opportunity_detail', args=[self.opportunity.id]))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['opportunity'], self.opportunity)
        self.assertEqual(response.context['application'], app)

        self.client.force_login(self.organization)
        response = self.client.get(reverse('opportunity_detail', args=[self.opportunity.id]))
        self.assertRedirects(response, reverse('screen1'))

    def test_draft_resubmit_lifecycle(self):
        self.client.force_login(self.student)

        # save draft
        response = self.client.post(
            reverse('apply_to_opportunity', args=[self.opportunity.id]),
            {'message': 'Draft entry', 'action': 'save_draft'},
            follow=True
        )
        app = Application.objects.get(student=self.student, opportunity=self.opportunity)
        self.assertEqual(app.status, Application.Status.DRAFT)
        self.assertContains(response, 'Application draft saved')

        # verify my applications shows draft entry
        response = self.client.get(reverse('my_applications'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context['applications']), 1)
        self.assertEqual(response.context['applications'][0].status, Application.Status.DRAFT)

        # resubmit from same opportunity
        response = self.client.post(
            reverse('apply_to_opportunity', args=[self.opportunity.id]),
            {'message': 'Final submission', 'action': 'submit'},
            follow=True
        )
        app.refresh_from_db()
        self.assertEqual(app.status, Application.Status.PENDING)
        self.assertEqual(app.message, 'Final submission')
        self.assertContains(response, 'Application submitted')


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
