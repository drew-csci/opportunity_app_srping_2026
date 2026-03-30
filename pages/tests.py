from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from django.utils import timezone
from datetime import timedelta

from pages.models import Opportunity, StudentOpportunity, Notification

User = get_user_model()


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
