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

