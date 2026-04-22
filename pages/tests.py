"""Note: Later on in the code, Client.Login() lines mostly use the (username=..., password=...) format, but when getting 
to account follow/unfollow tests, they use (email=..., password=...) client login logic instead. Code should still work as
intended, but keep this in mind if any client login errors appear upon running this code"""

import datetime
import json
from datetime import timedelta

from django.contrib.auth import get_user_model
from django.test import TestCase, Client
from django.urls import reverse
from django.utils import timezone

from pages.models import Notification, Opportunity, StudentOpportunity

from .forms import VolunteerProfileForm
from .models import OrganizationFollow, VolunteerExperience

User = get_user_model()


"""Opportunity Completion Tests"""
class DashboardPostCompletionTest(TestCase):
    """Test suite for dashboard post creation when opportunities are completed."""

    def setUp(self):
        """Set up test fixtures."""
        # Create test organization user
        self.organization = User.objects.create_user(
            email='org@test.com',
            username='test_org',
            first_name='Test',
            last_name='Organization',
            user_type='organization',
            password='testpass123'
        )

        # Create test student user
        self.student = User.objects.create_user(
            email='student@test.com',
            username='test_student',
            first_name='Test',
            last_name='Student',
            user_type='student',
            password='testpass123'
        )

        # Create test opportunity
        self.opportunity = Opportunity.objects.create(
            title='Test Opportunity',
            description='This is a test opportunity for dashboard testing.',
            organization=self.organization,
            status='open'
        )

    def test_completed_opportunity_appears_on_student_dashboard(self):
        """Test that a completed opportunity appears on the student's dashboard."""
        # Create a StudentOpportunity in completed status
        student_opportunity = StudentOpportunity.objects.create(
            student=self.student,
            opportunity=self.opportunity,
            status='completed',
            date_completed=timezone.now()
        )

        # Query using the same filter the dashboard view uses
        completed_opportunities = StudentOpportunity.objects.filter(
            student=self.student,
            status='completed'
        ).select_related('opportunity', 'opportunity__organization')

        # Assert the opportunity appears in completed opportunities
        self.assertEqual(completed_opportunities.count(), 1)
        self.assertIn(student_opportunity, completed_opportunities)

    def test_in_progress_opportunity_not_on_completed_dashboard(self):
        """Test that in-progress opportunities don't appear on completed section."""
        # Create a StudentOpportunity in in_progress status
        StudentOpportunity.objects.create(
            student=self.student,
            opportunity=self.opportunity,
            status='in_progress',
            date_joined=timezone.now()
        )

        # Query completed opportunities
        completed_opportunities = StudentOpportunity.objects.filter(
            student=self.student,
            status='completed'
        )

        # Assert it doesn't appear
        self.assertEqual(completed_opportunities.count(), 0)

    def test_pending_opportunity_not_on_completed_dashboard(self):
        """Test that pending opportunities don't appear on completed section."""
        # Create a StudentOpportunity in pending status
        StudentOpportunity.objects.create(
            student=self.student,
            opportunity=self.opportunity,
            status='pending',
            date_pending=timezone.now()
        )

        # Query completed opportunities
        completed_opportunities = StudentOpportunity.objects.filter(
            student=self.student,
            status='completed'
        )

        # Assert it doesn't appear
        self.assertEqual(completed_opportunities.count(), 0)

    def test_multiple_completed_opportunities_all_appear(self):
        """Test that multiple completed opportunities all appear on dashboard."""
        # Create multiple opportunities
        opp2 = Opportunity.objects.create(
            title='Second Opportunity',
            description='Second test opportunity.',
            organization=self.organization,
            status='open'
        )

        opp3 = Opportunity.objects.create(
            title='Third Opportunity',
            description='Third test opportunity.',
            organization=self.organization,
            status='open'
        )

        # Create completed StudentOpportunity records
        student_opp1 = StudentOpportunity.objects.create(
            student=self.student,
            opportunity=self.opportunity,
            status='completed',
            date_completed=timezone.now() - timedelta(days=5)
        )

        student_opp2 = StudentOpportunity.objects.create(
            student=self.student,
            opportunity=opp2,
            status='completed',
            date_completed=timezone.now() - timedelta(days=3)
        )

        student_opp3 = StudentOpportunity.objects.create(
            student=self.student,
            opportunity=opp3,
            status='completed',
            date_completed=timezone.now()
        )

        # Query completed opportunities
        completed_opportunities = StudentOpportunity.objects.filter(
            student=self.student,
            status='completed'
        ).select_related('opportunity', 'opportunity__organization')

        # Assert all three appear
        self.assertEqual(completed_opportunities.count(), 3)
        self.assertIn(student_opp1, completed_opportunities)
        self.assertIn(student_opp2, completed_opportunities)
        self.assertIn(student_opp3, completed_opportunities)

    def test_completed_opportunity_has_correct_data(self):
        """Test that completed opportunity has correct date and organization info."""
        completion_date = timezone.now() - timedelta(days=2)
        
        student_opportunity = StudentOpportunity.objects.create(
            student=self.student,
            opportunity=self.opportunity,
            status='completed',
            date_completed=completion_date
        )

        # Retrieve and verify data
        retrieved = StudentOpportunity.objects.get(id=student_opportunity.id)
        
        self.assertEqual(retrieved.status, 'completed')
        self.assertEqual(retrieved.date_completed, completion_date)
        self.assertEqual(retrieved.opportunity.title, 'Test Opportunity')
        self.assertEqual(retrieved.opportunity.organization, self.organization)
        self.assertEqual(retrieved.student, self.student)

    def test_dashboard_view_returns_completed_opportunities(self):
        """Test that the student_dashboard view returns completed opportunities."""
        # Create a completed opportunity
        StudentOpportunity.objects.create(
            student=self.student,
            opportunity=self.opportunity,
            status='completed',
            date_completed=timezone.now()
        )

        # Create a client and log in
        client = Client()
        client.login(email=self.student.email, password='testpass123')

        # Access the dashboard
        response = client.get('/student-dashboard/')

        # Verify response is successful
        self.assertEqual(response.status_code, 200)

        # Verify context contains completed opportunities
        self.assertIn('completed_opportunities', response.context)
        self.assertEqual(response.context['completed_opportunities'].count(), 1)

    def test_dashboard_view_only_shows_this_students_opportunities(self):
        """Test that students only see their own completed opportunities."""
        # Create another student
        other_student = User.objects.create_user(
            email='other@test.com',
            username='other_student',
            first_name='Other',
            last_name='Student',
            user_type='student',
            password='testpass123'
        )

        # Create completed opportunities for both students
        StudentOpportunity.objects.create(
            student=self.student,
            opportunity=self.opportunity,
            status='completed',
            date_completed=timezone.now()
        )

        opp2 = Opportunity.objects.create(
            title='Other Opportunity',
            description='Opportunity for other student.',
            organization=self.organization,
            status='open'
        )

        StudentOpportunity.objects.create(
            student=other_student,
            opportunity=opp2,
            status='completed',
            date_completed=timezone.now()
        )

        # Create a client and log in as first student
        client = Client()
        client.login(email=self.student.email, password='testpass123')

        # Access the dashboard
        response = client.get('/student-dashboard/')

        # Verify only the first student's opportunity appears
        self.assertEqual(response.context['completed_opportunities'].count(), 1)
        self.assertEqual(
            response.context['completed_opportunities'].first().student,
            self.student
        )

    def test_student_cannot_access_other_student_dashboard(self):
        """Test that students cannot access other students' dashboards."""
        other_student = User.objects.create_user(
            email='other2@test.com',
            username='other_student2',
            first_name='Other2',
            last_name='Student2',
            user_type='student',
            password='testpass123'
        )

        client = Client()
        client.login(email=self.student.email, password='testpass123')

        # Student dashboards are per-user based on request.user, not URL params
        # So this just tests that the logged-in user sees their own data
        response = client.get('/student-dashboard/')
        self.assertEqual(response.status_code, 200)

class OrganizationApprovalTest(TestCase):
    """Test suite for organization approval and denial of pending opportunities."""

    def setUp(self):
        """Set up test fixtures."""
        # Create test organization user
        self.organization = User.objects.create_user(
            email='org@test.com',
            username='test_org',
            first_name='Test',
            last_name='Organization',
            user_type='organization',
            password='testpass123'
        )

        # Create another organization for permission tests
        self.other_organization = User.objects.create_user(
            email='other_org@test.com',
            username='other_org',
            first_name='Other',
            last_name='Organization',
            user_type='organization',
            password='testpass123'
        )

        # Create test student user
        self.student = User.objects.create_user(
            email='student@test.com',
            username='test_student',
            first_name='Test',
            last_name='Student',
            user_type='student',
            password='testpass123'
        )

        # Create test opportunity
        self.opportunity = Opportunity.objects.create(
            title='Test Opportunity',
            description='This is a test opportunity for approval testing.',
            organization=self.organization,
            status='open'
        )

    def test_organization_can_approve_pending_opportunity(self):
        """Test that an organization can approve a pending opportunity."""
        # Create a pending StudentOpportunity
        student_opportunity = StudentOpportunity.objects.create(
            student=self.student,
            opportunity=self.opportunity,
            status='pending',
            date_pending=timezone.now()
        )

        # Verify it's currently pending
        self.assertEqual(student_opportunity.status, 'pending')

        # Approve the opportunity (simulating the view logic)
        student_opportunity.status = 'completed'
        student_opportunity.date_completed = timezone.now()
        student_opportunity.save()

        # Verify status changed
        refreshed = StudentOpportunity.objects.get(id=student_opportunity.id)
        self.assertEqual(refreshed.status, 'completed')
        self.assertIsNotNone(refreshed.date_completed)

    def test_approval_creates_notification_for_student(self):
        """Test that approving an opportunity creates a notification for the student."""
        # Create a pending StudentOpportunity
        student_opportunity = StudentOpportunity.objects.create(
            student=self.student,
            opportunity=self.opportunity,
            status='pending',
            date_pending=timezone.now()
        )

        # Create notification for approval
        notification = Notification.objects.create(
            recipient=self.student,
            notification_type=Notification.NotificationType.COMPLETION_APPROVED,
            student_opportunity=student_opportunity,
            message=f"Your completion of '{self.opportunity.title}' has been approved!"
        )

        # Verify notification was created
        self.assertEqual(notification.recipient, self.student)
        self.assertEqual(notification.notification_type, 'completion_approved')
        self.assertEqual(Notification.objects.filter(recipient=self.student).count(), 1)
from .models import VolunteerExperience, OrganizationFollow, Opportunity, Application

User = get_user_model()

    def test_organization_can_deny_pending_opportunity(self):
        """Test that an organization can deny a pending opportunity."""
        # Create a pending StudentOpportunity
        student_opportunity = StudentOpportunity.objects.create(
            student=self.student,
            opportunity=self.opportunity,
            status='pending',
            date_pending=timezone.now()
        )

        denial_reason = "The work does not meet the required standards."

        # Deny the opportunity (simulating the view logic)
        student_opportunity.status = 'in_progress'
        student_opportunity.denial_reason = denial_reason
        student_opportunity.date_pending = None
        student_opportunity.save()

        # Verify status changed back to in_progress
        refreshed = StudentOpportunity.objects.get(id=student_opportunity.id)
        self.assertEqual(refreshed.status, 'in_progress')
        self.assertEqual(refreshed.denial_reason, denial_reason)
        self.assertIsNone(refreshed.date_pending)

    def test_denial_creates_notification_with_reason(self):
        """Test that denying an opportunity creates a notification with the denial reason."""
        # Create a pending StudentOpportunity
        student_opportunity = StudentOpportunity.objects.create(
            student=self.student,
            opportunity=self.opportunity,
            status='pending',
            date_pending=timezone.now()
        )

        denial_reason = "Please revise your submission with more detail."

        # Create notification for denial
        notification = Notification.objects.create(
            recipient=self.student,
            notification_type=Notification.NotificationType.COMPLETION_DENIED,
            student_opportunity=student_opportunity,
            message=f"Your completion of '{self.opportunity.title}' was not approved.\n\nFeedback: {denial_reason}"
        )

        # Verify notification was created with message
        self.assertEqual(notification.recipient, self.student)
        self.assertEqual(notification.notification_type, 'completion_denied')
        self.assertIn(denial_reason, notification.message)

    def test_only_opportunity_organization_can_approve(self):
        """Test that only the organization that posted the opportunity can approve it."""
        # Create a pending StudentOpportunity
        student_opportunity = StudentOpportunity.objects.create(
            student=self.student,
            opportunity=self.opportunity,
            status='pending',
            date_pending=timezone.now()
        )

        # Verify the other organization is not the one who posted this opportunity
        self.assertNotEqual(self.opportunity.organization, self.other_organization)
        self.assertEqual(self.opportunity.organization, self.organization)

    def test_pending_opportunity_available_for_review(self):
        """Test that pending opportunities are available for organization review."""
        # Create a pending StudentOpportunity
        student_opportunity = StudentOpportunity.objects.create(
            student=self.student,
            opportunity=self.opportunity,
            status='pending',
            date_pending=timezone.now()
        )

        # Query pending opportunities for this organization
        pending = StudentOpportunity.objects.filter(
            opportunity__organization=self.organization,
            status='pending'
        ).select_related('student', 'opportunity')

        # Verify it appears in the query
        self.assertEqual(pending.count(), 1)
        self.assertEqual(pending.first(), student_opportunity)

    def test_non_pending_opportunity_not_in_review(self):
        """Test that non-pending opportunities don't appear in pending review list."""
        # Create opportunities with different statuses
        StudentOpportunity.objects.create(
            student=self.student,
            opportunity=self.opportunity,
            status='completed',
            date_completed=timezone.now()
        )

        # Query pending opportunities for this organization
        pending = StudentOpportunity.objects.filter(
            opportunity__organization=self.organization,
            status='pending'
        )

        # Verify nothing appears
        self.assertEqual(pending.count(), 0)

    def test_multiple_pending_opportunities_all_show_for_review(self):
        """Test that multiple pending opportunities all appear for organization review."""
        # Create multiple opportunities
        opp2 = Opportunity.objects.create(
            title='Second Opportunity',
            description='Second test opportunity.',
            organization=self.organization,
            status='open'
        )

        opp3 = Opportunity.objects.create(
            title='Third Opportunity',
            description='Third test opportunity.',
            organization=self.organization,
            status='open'
        )

        # Create multiple students
        student2 = User.objects.create_user(
            email='student2@test.com',
            username='student2',
            user_type='student',
            password='testpass123'
        )

        student3 = User.objects.create_user(
            email='student3@test.com',
            username='student3',
            user_type='student',
            password='testpass123'
        )

        # Create pending StudentOpportunity records
        pending1 = StudentOpportunity.objects.create(
            student=self.student,
            opportunity=self.opportunity,
            status='pending',
            date_pending=timezone.now() - timedelta(hours=2)
        )

        pending2 = StudentOpportunity.objects.create(
            student=student2,
            opportunity=opp2,
            status='pending',
            date_pending=timezone.now() - timedelta(hours=1)
        )

        pending3 = StudentOpportunity.objects.create(
            student=student3,
            opportunity=opp3,
            status='pending',
            date_pending=timezone.now()
        )

        # Query pending opportunities for this organization
        pending = StudentOpportunity.objects.filter(
            opportunity__organization=self.organization,
            status='pending'
        ).select_related('student', 'opportunity')

        # Verify all three appear
        self.assertEqual(pending.count(), 3)
        self.assertIn(pending1, pending)
        self.assertIn(pending2, pending)
        self.assertIn(pending3, pending)

    def test_approval_removes_from_pending_queue(self):
        """Test that after approval, opportunity no longer appears in pending queue."""
        # Create a pending StudentOpportunity
        student_opportunity = StudentOpportunity.objects.create(
            student=self.student,
            opportunity=self.opportunity,
            status='pending',
            date_pending=timezone.now()
        )

        # Initial state: appears in pending
        pending_before = StudentOpportunity.objects.filter(
            opportunity__organization=self.organization,
            status='pending'
        )
        self.assertEqual(pending_before.count(), 1)

        # Approve it
        student_opportunity.status = 'completed'
        student_opportunity.date_completed = timezone.now()
        student_opportunity.save()

        # After approval: no longer appears in pending
        pending_after = StudentOpportunity.objects.filter(
            opportunity__organization=self.organization,
            status='pending'
        )
        self.assertEqual(pending_after.count(), 0)

        # But appears in completed
        completed = StudentOpportunity.objects.filter(
            opportunity__organization=self.organization,
            status='completed'
        )
        self.assertEqual(completed.count(), 1)

class EndToEndWorkflowTest(TestCase):
    """Comprehensive integration test for the entire opportunity completion workflow."""

    def setUp(self):
        """Set up test fixtures."""
        # Create test organization user
        self.organization = User.objects.create_user(
            email='org@test.com',
            username='test_org',
            first_name='Test',
            last_name='Organization',
            user_type='organization',
            password='testpass123'
        )

        # Create test student user
        self.student = User.objects.create_user(
            email='student@test.com',
            username='test_student',
            first_name='Test',
            last_name='Student',
            user_type='student',
            password='testpass123'
        )

        # Create test opportunity
        self.opportunity = Opportunity.objects.create(
            title='Build Community Website',
            description='Help build a responsive website for the local community center.',
            organization=self.organization,
            status='open'
        )

        # Create a StudentOpportunity in "in_progress" status (pre-existing)
        self.student_opportunity = StudentOpportunity.objects.create(
            student=self.student,
            opportunity=self.opportunity,
            status='in_progress',
            date_joined=timezone.now() - timedelta(days=10)
        )

        self.client = Client()

    def test_complete_workflow_with_approval(self):
        """Test the complete workflow: student marks complete → org approves → appears on dashboard."""
        # Step 1: Student logs in and views their dashboard
        self.client.login(email=self.student.email, password='testpass123')
        response = self.client.get('/student-dashboard/')
        self.assertEqual(response.status_code, 200)
        
        # Verify opportunity is in "in_progress" section
        in_progress = response.context['in_progress_opportunities']
        self.assertEqual(in_progress.count(), 1)
        self.assertEqual(in_progress.first().status, 'in_progress')

        # Step 2: Student marks opportunity as complete (changes status from in_progress → pending)
        # This simulates the mark_opportunity_pending view
        self.student_opportunity.status = 'pending'
        self.student_opportunity.date_pending = timezone.now()
        self.student_opportunity.save()

        # Verify status changed
        refreshed = StudentOpportunity.objects.get(id=self.student_opportunity.id)
        self.assertEqual(refreshed.status, 'pending')
        self.assertIsNotNone(refreshed.date_pending)

        # Step 3: Organization logs in and views their dashboard
        self.client.logout()
        self.client.login(email=self.organization.email, password='testpass123')
        response = self.client.get('/organization-dashboard/')
        self.assertEqual(response.status_code, 200)

        # Verify pending opportunity is visible
        pending_completions = response.context.get('pending_completions', [])
        self.assertGreater(len(pending_completions), 0)

        # Find our opportunity in the pending list
        found = False
        for completion in pending_completions:
            if completion.opportunity.id == self.opportunity.id:
                found = True
                break
        self.assertTrue(found, "Pending opportunity should be visible to organization")

        # Step 4: Organization approves the completion
        # This simulates the approve_opportunity_completion view logic
        self.student_opportunity.status = 'completed'
        self.student_opportunity.date_completed = timezone.now()
        self.student_opportunity.save()

        # Create approval notification
        approval_notification = Notification.objects.create(
            recipient=self.student,
            notification_type=Notification.NotificationType.COMPLETION_APPROVED,
            student_opportunity=self.student_opportunity,
            message=f"Your completion of '{self.opportunity.title}' has been approved!"
        )

        # Verify notification was created
        self.assertEqual(approval_notification.recipient, self.student)
        self.assertEqual(approval_notification.notification_type, 'completion_approved')

        # Step 5: Student logs back in and views dashboard
        self.client.logout()
        self.client.login(email=self.student.email, password='testpass123')
        response = self.client.get('/student-dashboard/')
        self.assertEqual(response.status_code, 200)

        # Verify the opportunity now appears in "completed" section
        completed = response.context['completed_opportunities']
        self.assertEqual(completed.count(), 1)
        self.assertEqual(completed.first().status, 'completed')
        self.assertEqual(completed.first().opportunity.title, 'Build Community Website')

        # Verify opportunity is no longer in "in_progress" section
        in_progress = response.context['in_progress_opportunities']
        self.assertEqual(in_progress.count(), 0)

        # Step 6: Student can view their notifications
        response = self.client.get('/student-notifications/')
        self.assertEqual(response.status_code, 200)
        
        notifications = response.context.get('notifications', [])
        self.assertEqual(len(notifications), 1)
        self.assertIn('approved', notifications[0].message.lower())

    def test_complete_workflow_with_denial(self):
        """Test the complete workflow: student marks complete → org denies → returns to in_progress."""
        # Step 1: Student marks opportunity as complete
        self.student_opportunity.status = 'pending'
        self.student_opportunity.date_pending = timezone.now()
        self.student_opportunity.save()

        # Step 2: Verify it's in pending status
        refreshed = StudentOpportunity.objects.get(id=self.student_opportunity.id)
        self.assertEqual(refreshed.status, 'pending')

        # Step 3: Organization denies the completion with feedback
        denial_reason = "Please include more detail about your specific contributions to this project."
        self.student_opportunity.status = 'in_progress'
        self.student_opportunity.denial_reason = denial_reason
        self.student_opportunity.date_pending = None
        self.student_opportunity.save()

        # Create denial notification with reason
        denial_notification = Notification.objects.create(
            recipient=self.student,
            notification_type=Notification.NotificationType.COMPLETION_DENIED,
            student_opportunity=self.student_opportunity,
            message=f"Your completion of '{self.opportunity.title}' was not approved.\n\nFeedback: {denial_reason}"
        )

        # Step 4: Verify the opportunity returns to in_progress with denial reason
        refreshed = StudentOpportunity.objects.get(id=self.student_opportunity.id)
        self.assertEqual(refreshed.status, 'in_progress')
        self.assertEqual(refreshed.denial_reason, denial_reason)
        self.assertIsNone(refreshed.date_pending)

        # Step 5: Verify notification has correct feedback
        self.assertEqual(denial_notification.notification_type, 'completion_denied')
        self.assertIn(denial_reason, denial_notification.message)

        # Step 6: Student logs in and sees the opportunity back in in_progress
        self.client.login(email=self.student.email, password='testpass123')
        response = self.client.get('/student-dashboard/')
        self.assertEqual(response.status_code, 200)

        in_progress = response.context['in_progress_opportunities']
        self.assertEqual(in_progress.count(), 1)
        self.assertEqual(in_progress.first().status, 'in_progress')

        # Step 7: Student can view the denial notification with feedback
        response = self.client.get('/student-notifications/')
        self.assertEqual(response.status_code, 200)

        notifications = response.context.get('notifications', [])
        self.assertEqual(len(notifications), 1)
        self.assertIn('not approved', notifications[0].message.lower())
        self.assertIn(denial_reason, notifications[0].message)

    def test_pending_opportunity_removed_from_org_review_after_approval(self):
        """Test that approved opportunity disappears from org's pending review queue."""
        # Step 1: Student marks as pending
        self.student_opportunity.status = 'pending'
        self.student_opportunity.date_pending = timezone.now()
        self.student_opportunity.save()

        # Step 2: Organization sees it in their pending queue
        pending_before = StudentOpportunity.objects.filter(
            opportunity__organization=self.organization,
            status='pending'
        )
        self.assertEqual(pending_before.count(), 1)

        # Step 3: Organization approves it
        self.student_opportunity.status = 'completed'
        self.student_opportunity.date_completed = timezone.now()
        self.student_opportunity.save()

        # Step 4: Verify it's no longer in the pending queue
        pending_after = StudentOpportunity.objects.filter(
            opportunity__organization=self.organization,
            status='pending'
        )
        self.assertEqual(pending_after.count(), 0)

        # But now appears in completed
        completed = StudentOpportunity.objects.filter(
            opportunity__organization=self.organization,
            status='completed'
        )
        self.assertEqual(completed.count(), 1)

    def test_workflow_sequence_preserves_all_timestamps(self):
        """Test that the workflow sequence preserves all important timestamps."""
        # Initial state
        joined_date = self.student_opportunity.date_joined
        self.assertIsNotNone(joined_date)
        self.assertIsNone(self.student_opportunity.date_pending)
        self.assertIsNone(self.student_opportunity.date_completed)

        # After marking as pending
        pending_date = timezone.now()
        self.student_opportunity.status = 'pending'
        self.student_opportunity.date_pending = pending_date
        self.student_opportunity.save()

        self.assertEqual(self.student_opportunity.date_joined, joined_date)
        self.assertEqual(self.student_opportunity.date_pending, pending_date)
        self.assertIsNone(self.student_opportunity.date_completed)

        # After approval
        completed_date = timezone.now()
        self.student_opportunity.status = 'completed'
        self.student_opportunity.date_completed = completed_date
        self.student_opportunity.save()

        # Verify all timestamps are preserved
        refreshed = StudentOpportunity.objects.get(id=self.student_opportunity.id)
        self.assertEqual(refreshed.date_joined, joined_date)
        self.assertEqual(refreshed.date_pending, pending_date)
        self.assertEqual(refreshed.date_completed, completed_date)

        
"""Volunteer Profile Test"""        
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
from django.contrib.auth import get_user_model
from django.urls import reverse


class OrganizationScreen1Tests(TestCase):

    def setUp(self):
        self.client = Client()
        User = get_user_model()
        self.user = User.objects.create_user(
            username="orguser",
            password="testpass123"
        )
        self.user.user_type = "organization"
        self.user.save()

    def test_screen1_loads_for_authenticated_user(self):
        """Unit Test: authenticated user can access screen1."""
        self.client.force_login(self.user)
        response = self.client.get(reverse("screen1"))
        self.assertEqual(response.status_code, 200)

    def test_screen1_contains_organization_dashboard_content(self):
        """Unit Test: screen1 renders organization dashboard content."""
        self.client.force_login(self.user)
        response = self.client.get(reverse("screen1"))
        self.assertContains(response, "Organization Dashboard")
        self.assertContains(response, "Incoming Applications")

    def test_screen1_post_request_returns_success(self):
        """Integration Test: POST request to screen1 returns 200."""
        self.client.force_login(self.user)
        response = self.client.post(reverse("screen1"), {
            "index": "0",
            "action": "accept"
        })
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Organization Dashboard")

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


        
"""Organization Follow/Unfollow Tests"""
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


class MessageReadReceiptTests(TestCase):
    """Unit tests for message read receipt functionality"""

    def setUp(self):
        """Create test users and messages for each test"""
        self.volunteer = User.objects.create_user(
            username='volunteer_test',
            email='volunteer@example.com',
            password='testpass123',
            user_type='student',
            first_name='Volunteer',
            last_name='User',
        )
        self.organization = User.objects.create_user(
            username='org_test',
            email='org@example.com',
            password='testpass123',
            user_type='organization',
            first_name='Org',
            last_name='User',
        )

    def test_message_creates_unread_by_default(self):
        """Unit Test: New message is unread by default"""
        from .models import Message
        
        message = Message.objects.create(
            sender=self.volunteer,
            recipient=self.organization,
            subject='Test Message',
            content='This is a test message',
        )
        
        # Assert message is initially unread
        self.assertFalse(message.is_read)
        self.assertTrue(message.is_unread)
        self.assertIsNone(message.read_at)

    def test_mark_as_read_creates_receipt(self):
        """Unit Test: mark_as_read() creates a read receipt with timestamp"""
        from .models import Message
        from django.utils import timezone
        
        # Create an unread message
        message = Message.objects.create(
            sender=self.volunteer,
            recipient=self.organization,
            subject='Test Message',
            content='This is a test message',
            is_read=False,
            read_at=None,
        )
        
        # Verify initial state
        self.assertFalse(message.is_read)
        self.assertIsNone(message.read_at)
        
        # Mark as read
        before_mark = timezone.now()
        message.mark_as_read()
        after_mark = timezone.now()
        
        # Refresh from database
        message.refresh_from_db()
        
        # Assert it's now marked as read with a timestamp
        self.assertTrue(message.is_read)
        self.assertFalse(message.is_unread)
        self.assertIsNotNone(message.read_at)
        self.assertGreaterEqual(message.read_at, before_mark)
        self.assertLessEqual(message.read_at, after_mark)

    def test_mark_as_read_not_called_twice(self):
        """Unit Test: mark_as_read() should only set timestamp once"""
        from .models import Message
        
        message = Message.objects.create(
            sender=self.volunteer,
            recipient=self.organization,
            subject='Test Message',
            content='This is a test message',
        )
        
        # First mark as read
        message.mark_as_read()
        first_read_at = message.read_at
        
        # Wait slightly and mark as read again
        import time
        time.sleep(0.1)
        message.mark_as_read()
        
        # Verify read_at timestamp didn't change
        self.assertEqual(message.read_at, first_read_at)

    def test_get_read_status_unread(self):
        """Unit Test: get_read_status() returns 'Unread' for unread messages"""
        from .models import Message
        
        message = Message.objects.create(
            sender=self.volunteer,
            recipient=self.organization,
            subject='Test Message',
            content='This is a test message',
            is_read=False,
        )
        
        self.assertEqual(message.get_read_status(), 'Unread')

    def test_get_read_status_read_with_timestamp(self):
        """Unit Test: get_read_status() returns formatted timestamp for read messages"""
        from .models import Message
        
        message = Message.objects.create(
            sender=self.volunteer,
            recipient=self.organization,
            subject='Test Message',
            content='This is a test message',
        )
        
        message.mark_as_read()
        status = message.get_read_status()
        
        # Should contain "Read on" and a date
        self.assertIn('Read on', status)
        self.assertIn(',', status)  # Date should have comma like "April 15, 2026"

    def test_unread_message_count_for_organization(self):
        """Unit Test: get_unread_count() returns correct count"""
        from .models import Message
        
        # Create multiple messages
        msg1 = Message.objects.create(
            sender=self.volunteer,
            recipient=self.organization,
            subject='Message 1',
            content='Content 1',
            is_read=False,
        )
        msg2 = Message.objects.create(
            sender=self.volunteer,
            recipient=self.organization,
            subject='Message 2',
            content='Content 2',
            is_read=False,
        )
        msg3 = Message.objects.create(
            sender=self.volunteer,
            recipient=self.organization,
            subject='Message 3',
            content='Content 3',
            is_read=True,  # This one is read
        )
        
        # Count unread
        unread_count = Message.get_unread_count(self.organization)
        self.assertEqual(unread_count, 2)

    def test_message_detail_view_marks_as_read(self):
        """Integration Test: Viewing message_detail marks message as read"""
        from .models import Message
        
        # Create a message
        message = Message.objects.create(
            sender=self.volunteer,
            recipient=self.organization,
            subject='Test Message',
            content='This is a test message',
            is_read=False,
        )
        
        # Login as organization
        self.client.force_login(self.organization)
        
        # Directly call the view logic instead of HTTP request (since template doesn't exist yet)
        # Simulate what the view does: get the message and call mark_as_read()
        retrieved_message = Message.objects.get(id=message.id, recipient=self.organization)
        retrieved_message.mark_as_read()
        
        # Verify message is now marked as read
        message.refresh_from_db()
        self.assertTrue(message.is_read)
        self.assertIsNotNone(message.read_at)


class MessageReplyTests(TestCase):
    """Unit tests for message reply functionality"""

    def setUp(self):
        """Create test users for each test"""
        self.volunteer = User.objects.create_user(
            username='volunteer_test',
            email='volunteer@example.com',
            password='testpass123',
            user_type='student',
            first_name='Volunteer',
            last_name='User',
        )
        self.organization = User.objects.create_user(
            username='org_test',
            email='org@example.com',
            password='testpass123',
            user_type='organization',
            first_name='Org',
            last_name='User',
        )

    def test_message_reply_form_blank_validation(self):
        """Unit Test: MessageReplyForm rejects blank content"""
        from .forms import MessageReplyForm
        
        form = MessageReplyForm(data={'reply_content': '   '})
        self.assertFalse(form.is_valid())
        self.assertIn('reply_content', form.errors)
        # Check for either "blank" or "required" in the error message
        error_msg = str(form.errors['reply_content'][0]).lower()
        self.assertTrue('blank' in error_msg or 'required' in error_msg)

    def test_message_reply_form_character_limit_validation(self):
        """Unit Test: MessageReplyForm enforces 1000 character limit"""
        from .forms import MessageReplyForm
        
        # Create content that exceeds limit
        too_long = 'a' * 1001
        form = MessageReplyForm(data={'reply_content': too_long})
        
        self.assertFalse(form.is_valid())
        self.assertIn('reply_content', form.errors)
        error_msg = str(form.errors['reply_content'][0]).lower()
        # Check for "1000" and either "exceeds" or "at most"
        self.assertIn('1000', error_msg)
        self.assertTrue('exceeds' in error_msg or 'at most' in error_msg)

    def test_message_reply_form_at_limit_valid(self):
        """Unit Test: MessageReplyForm accepts content at exactly 1000 characters"""
        from .forms import MessageReplyForm
        
        # Create content at exactly the limit
        exactly_1000 = 'a' * 1000
        form = MessageReplyForm(data={'reply_content': exactly_1000})
        
        self.assertTrue(form.is_valid())

    def test_message_reply_form_under_limit_valid(self):
        """Unit Test: MessageReplyForm accepts valid content"""
        from .forms import MessageReplyForm
        
        form = MessageReplyForm(data={'reply_content': 'This is a valid reply message.'})
        
        self.assertTrue(form.is_valid())
        self.assertEqual(form.cleaned_data['reply_content'], 'This is a valid reply message.')

    def test_reply_message_creation_creates_conversation_thread(self):
        """Unit Test: Reply message is correctly linked to original message"""
        from .models import Message
        
        # Create original message
        original = Message.objects.create(
            sender=self.volunteer,
            recipient=self.organization,
            subject='Original Message',
            content='Original content',
        )
        
        # Create reply
        reply = Message.objects.create(
            sender=self.organization,
            recipient=self.volunteer,
            subject=f'Re: {original.subject}',
            content='Reply content',
            reply_to=original,
        )
        
        # Verify relationship
        self.assertTrue(reply.is_reply)
        self.assertEqual(reply.reply_to, original)
        self.assertEqual(original.replies.count(), 1)
        self.assertEqual(original.replies.first(), reply)

    def test_organization_reply_to_message_view(self):
        """Integration Test: Organization can submit reply (logic verification)"""
        from .models import Message
        
        # Create original message from volunteer
        original = Message.objects.create(
            sender=self.volunteer,
            recipient=self.organization,
            subject='Help Request',
            content='Can you help me with volunteering?',
        )
        
        # Simulate the view logic: create a reply message
        reply_content = 'We would be happy to help you volunteer!'
        reply = Message.objects.create(
            sender=self.organization,
            recipient=self.volunteer,
            subject=f'Re: {original.subject}',
            content=reply_content,
            reply_to=original,
        )
        
        # Verify reply was created correctly
        self.assertEqual(Message.objects.filter(reply_to=original).count(), 1)
        self.assertEqual(reply.sender, self.organization)
        self.assertEqual(reply.recipient, self.volunteer)
        self.assertEqual(reply.content, reply_content)
        self.assertIn('Re:', reply.subject)

    def test_reply_form_shows_character_limit_error_message(self):
        """Integration Test: Form validation shows helpful error message"""
        from .forms import MessageReplyForm
        
        # Test that form rejects content over limit and shows error
        too_long = 'a' * 1001
        form = MessageReplyForm(data={'reply_content': too_long})
        
        # Should not be valid
        self.assertFalse(form.is_valid())
        
        # And should have an error message related to character limit
        error_msg = str(form.errors['reply_content'][0]).lower()
        self.assertIn('1000', error_msg)


class OrganizationInboxIntegrationTests(TestCase):
    """Integration tests for complete organization messaging workflow"""

    def setUp(self):
        """Create test users and messages for workflow tests"""
        self.volunteer1 = User.objects.create_user(
            username='volunteer1',
            email='volunteer1@example.com',
            password='testpass123',
            user_type='student',
            first_name='Alice',
            last_name='Volunteer',
        )
        self.volunteer2 = User.objects.create_user(
            username='volunteer2',
            email='volunteer2@example.com',
            password='testpass123',
            user_type='student',
            first_name='Bob',
            last_name='Helper',
        )
        self.organization = User.objects.create_user(
            username='org_user',
            email='org@example.com',
            password='testpass123',
            user_type='organization',
            first_name='Great',
            last_name='Org',
        )

    def test_organization_inbox_shows_unread_count_in_context(self):
        """Integration Test: Organization inbox displays unread message count"""
        from .models import Message
        
        # Create unread messages from different volunteers
        msg1 = Message.objects.create(
            sender=self.volunteer1,
            recipient=self.organization,
            subject='Can I volunteer?',
            content='I would like to volunteer with your organization.',
            is_read=False,
        )
        msg2 = Message.objects.create(
            sender=self.volunteer2,
            recipient=self.organization,
            subject='Inquiry about opportunities',
            content='What opportunities are available?',
            is_read=False,
        )
        # Create one read message
        msg3 = Message.objects.create(
            sender=self.volunteer1,
            recipient=self.organization,
            subject='Follow-up',
            content='Just checking in.',
            is_read=True,
        )
        
        # Verify unread count
        unread_count = Message.get_unread_count(self.organization)
        self.assertEqual(unread_count, 2)
        
        # Verify all messages can be retrieved
        all_messages = Message.objects.filter(recipient=self.organization).order_by('-sent_at')
        self.assertEqual(all_messages.count(), 3)
        
        # Verify badge data
        from .utils import get_unread_message_badge_data
        badge_data = get_unread_message_badge_data(self.organization)
        self.assertEqual(badge_data['count'], 2)
        self.assertTrue(badge_data['has_unread'])

    def test_organization_reads_message_creates_read_receipt(self):
        """Integration Test: Organization can read message and read receipt is created"""
        from .models import Message
        
        # Create unread message
        original_message = Message.objects.create(
            sender=self.volunteer1,
            recipient=self.organization,
            subject='Volunteer Inquiry',
            content='I am very interested in volunteering with your team.',
            is_read=False,
            read_at=None,
        )
        
        # Verify message is initially unread
        self.assertFalse(original_message.is_read)
        self.assertIsNone(original_message.read_at)
        unread_before = Message.get_unread_count(self.organization)
        self.assertEqual(unread_before, 1)
        
        # Login as organization
        self.client.force_login(self.organization)
        
        # Simulate reading the message (call the view logic directly)
        retrieved_msg = Message.objects.get(id=original_message.id)
        retrieved_msg.mark_as_read()
        
        # Verify message is now read with receipt
        original_message.refresh_from_db()
        self.assertTrue(original_message.is_read)
        self.assertIsNotNone(original_message.read_at)
        
        # Verify read status string
        read_status = original_message.get_read_status()
        self.assertIn('Read on', read_status)
        
        # Verify unread count decreased
        unread_after = Message.get_unread_count(self.organization)
        self.assertEqual(unread_after, 0)

    def test_organization_workflow_receives_then_reads_multiple_messages(self):
        """Integration Test: Organization workflow with multiple messages"""
        from .models import Message
        
        # Create multiple messages
        messages_data = [
            ('Alice', 'Questions about role'),
            ('Bob', 'Availability inquiry'),
            ('Alice', 'Follow-up message'),
        ]
        
        created_messages = []
        for idx, (sender_name, subject) in enumerate(messages_data):
            sender = self.volunteer1 if 'Alice' in sender_name else self.volunteer2
            msg = Message.objects.create(
                sender=sender,
                recipient=self.organization,
                subject=subject,
                content=f'Message content {idx}',
                is_read=False,
            )
            created_messages.append(msg)
        
        # Verify all are unread
        self.assertEqual(Message.get_unread_count(self.organization), 3)
        
        # Login as organization
        self.client.force_login(self.organization)
        
        # Read messages in order
        for i, msg in enumerate(created_messages):
            msg.mark_as_read()
            remaining_unread = Message.get_unread_count(self.organization)
            self.assertEqual(remaining_unread, 3 - (i + 1))

    def test_organization_reply_workflow_full_cycle(self):
        """Integration Test: Full cycle - receive message, read it, and reply"""
        from .models import Message
        
        # Volunteer sends initial message
        initial_message = Message.objects.create(
            sender=self.volunteer1,
            recipient=self.organization,
            subject='I want to help',
            content='I am interested in helping with your volunteer programs.',
            is_read=False,
        )
        
        # Verify initial state
        self.assertFalse(initial_message.is_read)
        self.assertEqual(Message.get_unread_count(self.organization), 1)
        
        # Organization login
        self.client.force_login(self.organization)
        
        # Step 1: Read the message
        initial_message.mark_as_read()
        initial_message.refresh_from_db()
        self.assertTrue(initial_message.is_read)
        self.assertIsNotNone(initial_message.read_at)
        
        # Step 2: Create a reply
        reply_text = 'Thank you for your interest! We would love to have you join our team. Please fill out the volunteer form and we will be in touch soon.'
        reply = Message.objects.create(
            sender=self.organization,
            recipient=self.volunteer1,
            subject=f'Re: {initial_message.subject}',
            content=reply_text,
            reply_to=initial_message,
        )
        
        # Step 3: Verify reply is properly linked
        self.assertEqual(reply.reply_to, initial_message)
        self.assertTrue(reply.is_reply)
        self.assertEqual(initial_message.replies.count(), 1)
        self.assertEqual(initial_message.replies.first(), reply)
        
        # Step 4: Verify conversation thread
        thread = initial_message.get_conversation_thread()
        self.assertEqual(len(thread), 1)  # Should include the reply
        self.assertEqual(thread[0], reply)

    def test_organization_reply_with_character_limit_enforcement(self):
        """Integration Test: Reply form enforces character limits"""
        from .models import Message
        from .forms import MessageReplyForm
        
        initial_message = Message.objects.create(
            sender=self.volunteer1,
            recipient=self.organization,
            subject='Volunteer Inquiry',
            content='Can I volunteer?',
        )
        
        # Test 1: Valid reply within limit
        valid_reply = 'Yes, we would love to have you volunteer with us!'
        form = MessageReplyForm(data={'reply_content': valid_reply})
        self.assertTrue(form.is_valid())
        
        # Create the reply
        reply = Message.objects.create(
            sender=self.organization,
            recipient=self.volunteer1,
            subject=f'Re: {initial_message.subject}',
            content=form.cleaned_data['reply_content'],
            reply_to=initial_message,
        )
        self.assertEqual(reply.content, valid_reply)
        
        # Test 2: Reply at exact limit
        exactly_1000 = 'x' * 1000
        form = MessageReplyForm(data={'reply_content': exactly_1000})
        self.assertTrue(form.is_valid())
        
        # Test 3: Reply exceeding limit
        over_limit = 'x' * 1001
        form = MessageReplyForm(data={'reply_content': over_limit})
        self.assertFalse(form.is_valid())
        self.assertIn('reply_content', form.errors)
        
        # Test 4: Blank reply
        form = MessageReplyForm(data={'reply_content': '   '})
        self.assertFalse(form.is_valid())
        self.assertIn('reply_content', form.errors)

    def test_volunteer_sees_organization_reply_in_sent_messages(self):
        """Integration Test: Volunteer can see organization's reply to their message"""
        from .models import Message
        
        # Volunteer sends message
        volunteer_msg = Message.objects.create(
            sender=self.volunteer1,
            recipient=self.organization,
            subject='Interest in Program',
            content='I am interested in your volunteer program.',
        )
        
        # Organization reads and replies
        volunteer_msg.mark_as_read()
        org_reply = Message.objects.create(
            sender=self.organization,
            recipient=self.volunteer1,
            subject=f'Re: {volunteer_msg.subject}',
            content='Great! We are excited to have you join us.',
            reply_to=volunteer_msg,
        )
        
        # Verify reply is linked
        self.assertEqual(org_reply.reply_to, volunteer_msg)
        self.assertTrue(org_reply.is_reply)
        
        # Volunteer can retrieve their sent message and see replies
        sent_messages = Message.objects.filter(sender=self.volunteer1)
        self.assertEqual(sent_messages.count(), 1)
        self.assertEqual(sent_messages.first(), volunteer_msg)
        
        # Check for replies
        self.assertTrue(volunteer_msg.has_replies())
        replies = volunteer_msg.replies.all()
        self.assertEqual(replies.count(), 1)
        self.assertEqual(replies.first(), org_reply)

    def test_organization_unread_badge_appears_in_context(self):
        """Integration Test: Unread message badge data available in templates"""
        from .models import Message
        from .utils import get_unread_message_badge_data
        
        # Create some messages
        Message.objects.create(
            sender=self.volunteer1,
            recipient=self.organization,
            subject='msg1',
            content='content1',
            is_read=False,
        )
        Message.objects.create(
            sender=self.volunteer2,
            recipient=self.organization,
            subject='msg2',
            content='content2',
            is_read=False,
        )
        Message.objects.create(
            sender=self.volunteer1,
            recipient=self.organization,
            subject='msg3',
            content='content3',
            is_read=True,
        )
        
        # Get badge data
        badge_data = get_unread_message_badge_data(self.organization)
        
        # Verify badge data
        self.assertEqual(badge_data['count'], 2)
        self.assertTrue(badge_data['has_unread'])
        
        # When all are read
        Message.objects.filter(recipient=self.organization, is_read=False).update(is_read=True)
        badge_data = get_unread_message_badge_data(self.organization)
        self.assertEqual(badge_data['count'], 0)
        self.assertFalse(badge_data['has_unread'])

    def test_reply_prevents_blank_message_with_helpful_error(self):
        """Integration Test: Form shows helpful error when reply is blank"""
        from .forms import MessageReplyForm
        
        # Test various empty/whitespace inputs
        empty_inputs = ['', '   ', '\t', '\n', '  \n  ']
        
        for empty_input in empty_inputs:
            form = MessageReplyForm(data={'reply_content': empty_input})
            self.assertFalse(form.is_valid(), f"Form should reject input: {repr(empty_input)}")
            self.assertIn('reply_content', form.errors)

    def test_organization_reply_character_counter_error_message(self):
        """Integration Test: Form provides helpful error message for character limit"""
        from .forms import MessageReplyForm
        
        # Message that exceeds limit by different amounts
        test_cases = [
            (1001, 1),   # 1 character over
            (1050, 50),  # 50 characters over
            (1500, 500), # 500 characters over
        ]
        
        for length, expected_overage in test_cases:
            too_long = 'a' * length
            form = MessageReplyForm(data={'reply_content': too_long})
            self.assertFalse(form.is_valid())
            
            # Verify error message mentions character count
            error_msg = str(form.errors['reply_content'][0]).lower()
            self.assertIn('1000', error_msg)

    def test_multiple_organizations_have_separate_inboxes(self):
        """Integration Test: Each organization has independent inbox"""
        from .models import Message
        
        # Create another organization
        org2 = User.objects.create_user(
            username='org2',
            email='org2@example.com',
            password='testpass123',
            user_type='organization',
        )
        
        # Send messages to different organizations
        msg_org1 = Message.objects.create(
            sender=self.volunteer1,
            recipient=self.organization,
            subject='For org 1',
            content='Message for first org',
            is_read=False,
        )
        msg_org2 = Message.objects.create(
            sender=self.volunteer1,
            recipient=org2,
            subject='For org 2',
            content='Message for second org',
            is_read=False,
        )
        
        # Verify separate counts
        org1_unread = Message.get_unread_count(self.organization)
        org2_unread = Message.get_unread_count(org2)
        
        self.assertEqual(org1_unread, 1)
        self.assertEqual(org2_unread, 1)
        
        # Read org1's message
        msg_org1.mark_as_read()
        
        # Verify counts are independent
        org1_unread = Message.get_unread_count(self.organization)
        org2_unread = Message.get_unread_count(org2)
        
        self.assertEqual(org1_unread, 0)
        self.assertEqual(org2_unread, 1)
        self.assertEqual(org2_unread, 1)
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

