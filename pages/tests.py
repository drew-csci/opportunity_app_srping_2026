from django.test import TestCase, Client
from django.urls import reverse
from django.utils import timezone
from django.contrib.auth import get_user_model
from datetime import timedelta
from .models import Application, ApplicationReminder

User = get_user_model()


class ApplicationModelTestCase(TestCase):
    """Unit tests for the Application model."""
    
    def setUp(self):
        """Set up test data."""
        self.student = User.objects.create_user(
            email='student@test.com',
            username='student@test.com',
            password='testpass123',
            user_type='student'
        )
        self.organization = User.objects.create_user(
            email='org@test.com',
            username='org@test.com',
            password='testpass123',
            user_type='organization'
        )
    
    def test_application_creation(self):
        """Test creating an application."""
        app = Application.objects.create(
            student=self.student,
            organization=self.organization,
            opportunity_title='Test Opportunity',
            status='applied',
            cover_letter='Test letter'
        )
        self.assertEqual(app.status, 'applied')
        self.assertEqual(app.student, self.student)
        self.assertEqual(app.organization, self.organization)
    
    def test_can_remind_applied_status(self):
        """Test that reminders can be sent for 'applied' status."""
        app = Application.objects.create(
            student=self.student,
            organization=self.organization,
            opportunity_title='Test Opportunity',
            status='applied'
        )
        self.assertTrue(app.can_remind)
    
    def test_cannot_remind_accepted_status(self):
        """Test that reminders cannot be sent for 'accepted' status."""
        app = Application.objects.create(
            student=self.student,
            organization=self.organization,
            opportunity_title='Test Opportunity',
            status='accepted'
        )
        self.assertFalse(app.can_remind)
    
    def test_cannot_remind_declined_status(self):
        """Test that reminders cannot be sent for 'declined' status."""
        app = Application.objects.create(
            student=self.student,
            organization=self.organization,
            opportunity_title='Test Opportunity',
            status='declined'
        )
        self.assertFalse(app.can_remind)
    
    def test_application_string_representation(self):
        """Test the string representation of an application."""
        app = Application.objects.create(
            student=self.student,
            organization=self.organization,
            opportunity_title='Test Opportunity',
            status='applied'
        )
        expected_str = f"{self.student.display_name} - Test Opportunity (applied)"
        self.assertEqual(str(app), expected_str)


class ApplicationReminderModelTestCase(TestCase):
    """Unit tests for the ApplicationReminder model."""
    
    def setUp(self):
        """Set up test data."""
        self.student = User.objects.create_user(
            email='student@test.com',
            username='student@test.com',
            password='testpass123',
            user_type='student'
        )
        self.organization = User.objects.create_user(
            email='org@test.com',
            username='org@test.com',
            password='testpass123',
            user_type='organization'
        )
        self.application = Application.objects.create(
            student=self.student,
            organization=self.organization,
            opportunity_title='Test Opportunity',
            status='applied'
        )
    
    def test_reminder_creation(self):
        """Test creating a reminder."""
        reminder = ApplicationReminder.objects.create(
            application=self.application,
            sent_by=self.student
        )
        self.assertEqual(reminder.application, self.application)
        self.assertEqual(reminder.sent_by, self.student)
    
    def test_can_send_reminder_first_time(self):
        """Test that a reminder can be sent when none have been sent before."""
        self.assertTrue(ApplicationReminder.can_send_reminder(self.application))
    
    def test_cannot_send_reminder_within_24_hours(self):
        """Test that reminders cannot be sent within 24 hours."""
        # Create a reminder
        ApplicationReminder.objects.create(
            application=self.application,
            sent_by=self.student
        )
        # Try to send another immediately
        self.assertFalse(ApplicationReminder.can_send_reminder(self.application))
    
    def test_can_send_reminder_after_24_hours(self):
        """Test that reminders can be sent after 24 hours."""
        # Create a reminder
        old_reminder = ApplicationReminder.objects.create(
            application=self.application,
            sent_by=self.student
        )
        # Manually set sent_at to 25 hours ago
        old_reminder.sent_at = timezone.now() - timedelta(hours=25)
        old_reminder.save()
        
        # Try to send another
        self.assertTrue(ApplicationReminder.can_send_reminder(self.application))
    
    def test_cannot_send_reminder_for_non_applied_status(self):
        """Test that reminders cannot be sent for non-'applied' status applications."""
        self.application.status = 'accepted'
        self.application.save()
        self.assertFalse(ApplicationReminder.can_send_reminder(self.application))


class SendReminderViewTestCase(TestCase):
    """Integration tests for the send_reminder view."""
    
    def setUp(self):
        """Set up test data."""
        self.client = Client()
        self.student = User.objects.create_user(
            email='student@test.com',
            username='student@test.com',
            password='testpass123',
            user_type='student'
        )
        self.other_student = User.objects.create_user(
            email='other@test.com',
            username='other@test.com',
            password='testpass123',
            user_type='student'
        )
        self.organization = User.objects.create_user(
            email='org@test.com',
            username='org@test.com',
            password='testpass123',
            user_type='organization'
        )
        self.application = Application.objects.create(
            student=self.student,
            organization=self.organization,
            opportunity_title='Test Opportunity',
            status='applied'
        )
    
    def test_send_reminder_as_owner(self):
        """Test that an application owner can send a reminder."""
        self.client.login(email='student@test.com', password='testpass123')
        response = self.client.post(
            reverse('send_reminder', args=[self.application.id])
        )
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('dashboard'))
        # Verify reminder was created
        self.assertTrue(ApplicationReminder.objects.filter(
            application=self.application,
            sent_by=self.student
        ).exists())
    
    def test_send_reminder_as_non_owner(self):
        """Test that a non-owner cannot send a reminder."""
        self.client.login(email='other@test.com', password='testpass123')
        response = self.client.post(
            reverse('send_reminder', args=[self.application.id])
        )
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('dashboard'))
    
    def test_send_reminder_as_organization(self):
        """Test that organizations cannot send reminders."""
        self.client.login(email='org@test.com', password='testpass123')
        response = self.client.post(
            reverse('send_reminder', args=[self.application.id])
        )
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('dashboard'), fetch_redirect_response=False)
    
    def test_send_reminder_not_logged_in(self):
        """Test that unauthenticated users are redirected to login."""
        response = self.client.post(
            reverse('send_reminder', args=[self.application.id])
        )
        # Redirect to login
        self.assertEqual(response.status_code, 302)
        self.assertIn('/accounts/login/', response['Location'])
    
    def test_send_reminder_for_accepted_application(self):
        """Test that reminders cannot be sent for accepted applications."""
        self.application.status = 'accepted'
        self.application.save()
        
        self.client.login(email='student@test.com', password='testpass123')
        response = self.client.post(
            reverse('send_reminder', args=[self.application.id])
        )
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('dashboard'))
    
    def test_send_reminder_for_declined_application(self):
        """Test that reminders cannot be sent for declined applications."""
        self.application.status = 'declined'
        self.application.save()
        
        self.client.login(email='student@test.com', password='testpass123')
        response = self.client.post(
            reverse('send_reminder', args=[self.application.id])
        )
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('dashboard'))
    
    def test_send_reminder_rate_limiting(self):
        """Test that rate limiting prevents multiple reminders within 24 hours."""
        self.client.login(email='student@test.com', password='testpass123')
        
        # Send first reminder
        response1 = self.client.post(
            reverse('send_reminder', args=[self.application.id])
        )
        self.assertEqual(response1.status_code, 302)
        self.assertRedirects(response1, reverse('dashboard'))
        
        # Try to send second reminder immediately
        response2 = self.client.post(
            reverse('send_reminder', args=[self.application.id])
        )
        self.assertEqual(response2.status_code, 302)
        self.assertRedirects(response2, reverse('dashboard'))
    
    def test_send_reminder_nonexistent_application(self):
        """Test sending reminder for non-existent application."""
        self.client.login(email='student@test.com', password='testpass123')
        response = self.client.post(
            reverse('send_reminder', args=[99999])
        )
        self.assertEqual(response.status_code, 404)


class DashboardViewTestCase(TestCase):
    """Integration tests for the dashboard view."""
    
    def setUp(self):
        """Set up test data."""
        self.client = Client()
        self.student = User.objects.create_user(
            email='student@test.com',
            username='student@test.com',
            password='testpass123',
            user_type='student'
        )
        self.organization = User.objects.create_user(
            email='org@test.com',
            username='org@test.com',
            password='testpass123',
            user_type='organization'
        )
        self.application = Application.objects.create(
            student=self.student,
            organization=self.organization,
            opportunity_title='Test Opportunity',
            status='applied'
        )
    
    def test_dashboard_displays_applications(self):
        """Test that the dashboard displays student applications."""
        self.client.login(email='student@test.com', password='testpass123')
        response = self.client.get(reverse('dashboard'))
        self.assertEqual(response.status_code, 200)
        self.assertIn('applications', response.context)
        self.assertIn(self.application, response.context['applications'])
    
    def test_dashboard_shows_reminder_button_for_applied(self):
        """Test that reminder button is shown for applied applications."""
        self.client.login(email='student@test.com', password='testpass123')
        response = self.client.get(reverse('dashboard'))
        self.assertEqual(response.status_code, 200)
        applications = response.context['applications']
        self.assertTrue(applications[0].can_send_reminder)
    
    def test_dashboard_hides_reminder_button_for_accepted(self):
        """Test that reminder button is hidden for accepted applications."""
        self.application.status = 'accepted'
        self.application.save()
        
        self.client.login(email='student@test.com', password='testpass123')
        response = self.client.get(reverse('dashboard'))
        self.assertEqual(response.status_code, 200)
        applications = response.context['applications']
        self.assertFalse(applications[0].can_send_reminder)
