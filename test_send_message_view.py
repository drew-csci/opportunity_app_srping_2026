#!/usr/bin/env python
"""
Standalone test runner for Test #7: send_message View - Student Access
Tests the send_message view for proper functionality with student users
"""
import os
import django
import sys

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'opportunity_app.settings')
django.setup()

from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.messages import get_messages
from accounts.models import User
from pages.models import Message

# Colors for output
GREEN = '\033[92m'
RED = '\033[91m'
YELLOW = '\033[93m'
RESET = '\033[0m'
BOLD = '\033[1m'

class SendMessageViewStudentAccessTest(TestCase):
    """Test Suite for send_message view - Student Access"""
    
    def setUp(self):
        """Set up test client and test users."""
        self.client = Client()
        
        # Create test student
        self.student = User.objects.create_user(
            username='student_test_user',
            email='student_test@example.com',
            password='testpass123',
            user_type='student',
            first_name='Test',
            last_name='Student'
        )
        
        # Create test organizations
        self.org1 = User.objects.create_user(
            username='org_test_user',
            email='org_test@example.com',
            password='testpass123',
            user_type='organization',
            first_name='Test',
            last_name='Organization'
        )
        
        self.org2 = User.objects.create_user(
            username='org2_test_user',
            email='org2_test@example.com',
            password='testpass123',
            user_type='organization',
            first_name='Another',
            last_name='Organization'
        )
    
    def tearDown(self):
        """Clean up after each test."""
        Message.objects.filter(sender=self.student).delete()
    
    def test_1_get_request_displays_form(self):
        """Test 1: GET request to /send-message/ displays the form."""
        self.client.force_login(self.student)
        response = self.client.get(reverse('send_message'))
        
        self.assertEqual(response.status_code, 200)
        self.assertIn('form', response.context)
        self.assertIn('recipient', response.context['form'].fields)
        self.assertIn('subject', response.context['form'].fields)
        self.assertIn('body', response.context['form'].fields)
    
    def test_2_form_includes_organizations(self):
        """Test 2: Recipient dropdown includes all organizations."""
        self.client.force_login(self.student)
        response = self.client.get(reverse('send_message'))
        form = response.context['form']
        
        recipient_items = list(form.fields['recipient'].queryset)
        self.assertIn(self.org1, recipient_items)
        self.assertIn(self.org2, recipient_items)
    
    def test_3_post_creates_message(self):
        """Test 3: POST request with valid data creates message in database."""
        self.client.force_login(self.student)
        
        initial_count = Message.objects.count()
        
        post_data = {
            'recipient': self.org1.id,
            'subject': 'Test Message Subject',
            'body': 'This is a test message body for the organization.'
        }
        
        response = self.client.post(reverse('send_message'), post_data)
        final_count = Message.objects.count()
        
        self.assertEqual(final_count, initial_count + 1)
        
        created_message = Message.objects.filter(subject='Test Message Subject').first()
        self.assertIsNotNone(created_message)
        self.assertEqual(created_message.sender, self.student)
        self.assertEqual(created_message.recipient, self.org1)
        self.assertEqual(created_message.body, 'This is a test message body for the organization.')
    
    def test_4_post_redirects(self):
        """Test 4: POST request redirects after successful message creation."""
        self.client.force_login(self.student)
        
        post_data = {
            'recipient': self.org1.id,
            'subject': 'Test Subject',
            'body': 'Test body'
        }
        
        response = self.client.post(reverse('send_message'), post_data)
        self.assertEqual(response.status_code, 302)
    
    def test_5_success_message_displayed(self):
        """Test 5: Success message is displayed after message sent."""
        self.client.force_login(self.student)
        
        post_data = {
            'recipient': self.org1.id,
            'subject': 'Test Subject',
            'body': 'Test body'
        }
        
        response = self.client.post(reverse('send_message'), post_data, follow=True)
        messages_list = list(get_messages(response.wsgi_request))
        
        self.assertGreater(len(messages_list), 0)
        self.assertEqual(str(messages_list[0]), 'Message sent successfully!')
    
    def test_6_validation_missing_recipient(self):
        """Test 6: Form validation fails when recipient is missing."""
        self.client.force_login(self.student)
        
        post_data = {
            'subject': 'Test Subject',
            'body': 'Test body'
        }
        
        response = self.client.post(reverse('send_message'), post_data)
        
        self.assertEqual(Message.objects.count(), 0)
        self.assertEqual(response.status_code, 200)
        
        form = response.context['form']
        self.assertTrue(form.errors)
        self.assertIn('recipient', form.errors)
    
    def test_7_validation_missing_subject(self):
        """Test 7: Form validation fails when subject is missing."""
        self.client.force_login(self.student)
        
        post_data = {
            'recipient': self.org1.id,
            'body': 'Test body'
        }
        
        response = self.client.post(reverse('send_message'), post_data)
        
        self.assertEqual(Message.objects.count(), 0)
        self.assertEqual(response.status_code, 200)
        
        form = response.context['form']
        self.assertTrue(form.errors)
        self.assertIn('subject', form.errors)
    
    def test_8_validation_missing_body(self):
        """Test 8: Form validation fails when body is missing."""
        self.client.force_login(self.student)
        
        post_data = {
            'recipient': self.org1.id,
            'subject': 'Test Subject'
        }
        
        response = self.client.post(reverse('send_message'), post_data)
        
        self.assertEqual(Message.objects.count(), 0)
        self.assertEqual(response.status_code, 200)
        
        form = response.context['form']
        self.assertTrue(form.errors)
        self.assertIn('body', form.errors)
    
    def test_9_correct_sender_set(self):
        """Test 9: Logged-in student is set as sender."""
        self.client.force_login(self.student)
        
        post_data = {
            'recipient': self.org1.id,
            'subject': 'Test Subject',
            'body': 'Test body'
        }
        
        self.client.post(reverse('send_message'), post_data)
        
        message = Message.objects.filter(subject='Test Subject').first()
        self.assertEqual(message.sender, self.student)
        self.assertEqual(message.sender.email, 'student_test@example.com')
    
    def test_10_timestamp_auto_generated(self):
        """Test 10: Timestamp is automatically generated."""
        self.client.force_login(self.student)
        
        post_data = {
            'recipient': self.org1.id,
            'subject': 'Test Subject',
            'body': 'Test body'
        }
        
        self.client.post(reverse('send_message'), post_data)
        
        message = Message.objects.filter(subject='Test Subject').first()
        self.assertIsNotNone(message.created_at)
    
    def test_11_send_multiple_messages(self):
        """Test 11: Student can send multiple messages."""
        self.client.force_login(self.student)
        
        post_data1 = {
            'recipient': self.org1.id,
            'subject': 'First Message',
            'body': 'First body'
        }
        self.client.post(reverse('send_message'), post_data1)
        
        post_data2 = {
            'recipient': self.org2.id,
            'subject': 'Second Message',
            'body':' Second body'
        }
        self.client.post(reverse('send_message'), post_data2)
        
        self.assertEqual(Message.objects.count(), 2)
        
        first_msg = Message.objects.filter(subject='First Message').first()
        self.assertEqual(first_msg.recipient, self.org1)
        
        second_msg = Message.objects.filter(subject='Second Message').first()
        self.assertEqual(second_msg.recipient, self.org2)


if __name__ == '__main__':
    import unittest
    from django.test.utils import get_runner
    from django.conf import settings
    
    TestRunner = get_runner(settings)
    test_runner = TestRunner(verbosity=2, interactive=False, keepdb=False)
    failures = test_runner.run_tests(['test_send_message_view.SendMessageViewStudentAccessTest'])
    sys.exit(bool(failures))
