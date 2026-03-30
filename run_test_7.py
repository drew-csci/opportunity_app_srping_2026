#!/usr/bin/env python
"""
Run Test #7: send_message View - Student Access
Tests the send_message view functionality with direct database and test client
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'opportunity_app.settings')
django.setup()

from django.test import Client, override_settings
from django.urls import reverse
from django.contrib.messages import get_messages
from accounts.models import User
from pages.models import Message

# Colors for output
GREEN = '\033[92m'
RED = '\033[91m'
RESET = '\033[0m'
BOLD = '\033[1m'

class TestRunner:
    def __init__(self):
        self.passed = 0
        self.failed = 0
        self.errors = []
    
    def add_pass(self, test_name):
        self.passed += 1
        print(f"  {GREEN}✓ PASS{RESET}: {test_name}")
    
    def add_fail(self, test_name, error):
        self.failed += 1
        self.errors.append((test_name, error))
        print(f"  {RED}✗ FAIL{RESET}: {test_name}")
        print(f"    Error: {error}")
    
    def print_summary(self):
        print(f"\n{BOLD}{'='*70}{RESET}")
        print(f"{BOLD}TEST SUMMARY{RESET}")
        print(f"{BOLD}{'='*70}{RESET}")
        print(f"Passed: {GREEN}{self.passed}{RESET}")
        print(f"Failed: {RED}{self.failed}{RESET}")
        print(f"Total:  {self.passed + self.failed}")
        print(f"{BOLD}{'='*70}{RESET}\n")
        
        if self.failed == 0:
            print(f"{GREEN}✓ ALL TESTS PASSED!{RESET}\n")
            return True
        else:
            print(f"{RED}✗ {self.failed} test(s) failed{RESET}\n")
            for test_name, error in self.errors:
                print(f"  • {test_name}: {error}")
            print()
            return False

def setup_test_users():
    """Create test users."""
    # Clear existing test users
    User.objects.filter(email__in=[
        'test_student@example.com',
        'test_org1@example.com',
        'test_org2@example.com'
    ]).delete()
    
    # Create student
    student = User.objects.create_user(
        username='test_student',
        email='test_student@example.com',
        password='testpass123',
        user_type='student',
        first_name='Test',
        last_name='Student'
    )
    
    # Create organizations
    org1 = User.objects.create_user(
        username='test_org1',
        email='test_org1@example.com',
        password='testpass123',
        user_type='organization',
        first_name='Test Org',
        last_name='One'
    )
    
    org2 = User.objects.create_user(
        username='test_org2',
        email='test_org2@example.com',
        password='testpass123',
        user_type='organization',
        first_name='Test Org',
        last_name='Two'
    )
    
    return student, org1, org2

def cleanup_messages(student):
    """Clean up messages created by test student."""
    Message.objects.filter(sender=student).delete()

def run_tests():
    """Run all 11 tests."""
    runner = TestRunner()
    
    # Setup
    print(f"\n{BOLD}TEST #7: SEND_MESSAGE VIEW - STUDENT ACCESS{RESET}\n")
    print("Setting up test data...")
    student, org1, org2 = setup_test_users()
    print(f"  {GREEN}✓{RESET} Test users created\n")
    
    print(f"{BOLD}Running tests...{RESET}\n")
    
    # Test 1: GET request displays form
    try:
        cleanup_messages(student)
        client = Client()
        client.force_login(student)
        response = client.get(reverse('send_message'))
        
        assert response.status_code == 200, f"Status {response.status_code}"
        assert response.context is not None, "Context is None"
        assert 'form' in response.context, "Form not in context"
        form = response.context['form']
        assert 'recipient' in form.fields
        assert 'subject' in form.fields
        assert 'body' in form.fields
        
        runner.add_pass("GET request displays form")
    except Exception as e:
        runner.add_fail("GET request displays form", str(e))
    
    # Test 2: Form includes both organizations
    try:
        cleanup_messages(student)
        client = Client()
        client.force_login(student)
        response = client.get(reverse('send_message'))
        
        form = response.context['form']
        recipient_queryset = form.fields['recipient'].queryset
        recipient_list = list(recipient_queryset)
        
        assert org1 in recipient_list, "Org1 not in recipients"
        assert org2 in recipient_list, "Org2 not in recipients"
        
        runner.add_pass("Form includes both organizations in dropdown")
    except Exception as e:
        runner.add_fail("Form includes both organizations in dropdown", str(e))
    
    # Test 3: POST creates message
    try:
        cleanup_messages(student)
        client = Client()
        client.force_login(student)
        
        initial_count = Message.objects.count()
        
        post_data = {
            'recipient': org1.id,
            'subject': 'Test Message',
            'body': 'Test body content'
        }
        
        response = client.post(reverse('send_message'), post_data)
        
        final_count = Message.objects.count()
        assert final_count == initial_count + 1, f"Count: {initial_count} -> {final_count}"
        
        msg = Message.objects.filter(subject='Test Message').first()
        assert msg is not None
        assert msg.sender == student
        assert msg.recipient == org1
        
        runner.add_pass("POST request creates message in database")
    except Exception as e:
        runner.add_fail("POST request creates message in database", str(e))
    
    # Test 4: POST redirects
    try:
        cleanup_messages(student)
        client = Client()
        client.force_login(student)
        
        post_data = {
            'recipient': org1.id,
            'subject': 'Test',
            'body': 'Test'
        }
        
        response = client.post(reverse('send_message'), post_data)
        assert response.status_code == 302, f"Status {response.status_code}"
        
        runner.add_pass("POST request redirects after success")
    except Exception as e:
        runner.add_fail("POST request redirects after success", str(e))
    
    # Test 5: Success message
    try:
        cleanup_messages(student)
        client = Client()
        client.force_login(student)
        
        post_data = {
            'recipient': org1.id,
            'subject': 'Test',
            'body': 'Test'
        }
        
        response = client.post(reverse('send_message'), post_data, follow=True)
        messages_list = list(get_messages(response.wsgi_request))
        
        assert len(messages_list) > 0, "No messages"
        assert str(messages_list[0]) == 'Message sent successfully!', f"Wrong message: {str(messages_list[0])}"
        
        runner.add_pass("Success message displayed after sending")
    except Exception as e:
        runner.add_fail("Success message displayed after sending", str(e))
    
    # Test 6: Validation - missing recipient
    try:
        cleanup_messages(student)
        client = Client()
        client.force_login(student)
        
        post_data = {
            'subject': 'Test',
            'body': 'Test'
        }
        
        response = client.post(reverse('send_message'), post_data)
        
        assert Message.objects.count() == 0
        assert response.status_code == 200
        assert 'recipient' in response.context['form'].errors
        
        runner.add_pass("Form validation fails when recipient missing")
    except Exception as e:
        runner.add_fail("Form validation fails when recipient missing", str(e))
    
    # Test 7: Validation - missing subject
    try:
        cleanup_messages(student)
        client = Client()
        client.force_login(student)
        
        post_data = {
            'recipient': org1.id,
            'body': 'Test'
        }
        
        response = client.post(reverse('send_message'), post_data)
        
        assert Message.objects.count() == 0
        assert response.status_code == 200
        assert 'subject' in response.context['form'].errors
        
        runner.add_pass("Form validation fails when subject missing")
    except Exception as e:
        runner.add_fail("Form validation fails when subject missing", str(e))
    
    # Test 8: Validation - missing body
    try:
        cleanup_messages(student)
        client = Client()
        client.force_login(student)
        
        post_data = {
            'recipient': org1.id,
            'subject': 'Test'
        }
        
        response = client.post(reverse('send_message'), post_data)
        
        assert Message.objects.count() == 0
        assert response.status_code == 200
        assert 'body' in response.context['form'].errors
        
        runner.add_pass("Form validation fails when body missing")
    except Exception as e:
        runner.add_fail("Form validation fails when body missing", str(e))
    
    # Test 9: Correct sender
    try:
        cleanup_messages(student)
        client = Client()
        client.force_login(student)
        
        post_data = {
            'recipient': org1.id,
            'subject': 'Test',
            'body': 'Test'
        }
        
        client.post(reverse('send_message'), post_data)
        msg = Message.objects.first()
        
        assert msg.sender == student
        assert msg.sender.email == 'test_student@example.com'
        
        runner.add_pass("Correct student set as sender")
    except Exception as e:
        runner.add_fail("Correct student set as sender", str(e))
    
    # Test 10: Timestamp auto-generated
    try:
        cleanup_messages(student)
        client = Client()
        client.force_login(student)
        
        post_data = {
            'recipient': org1.id,
            'subject': 'Test',
            'body': 'Test'
        }
        
        client.post(reverse('send_message'), post_data)
        msg = Message.objects.first()
        
        assert msg.created_at is not None
        
        runner.add_pass("Timestamp auto-generated on message creation")
    except Exception as e:
        runner.add_fail("Timestamp auto-generated on message creation", str(e))
    
    # Test 11: Multiple messages
    try:
        cleanup_messages(student)
        client = Client()
        client.force_login(student)
        
        post_data1 = {
            'recipient': org1.id,
            'subject': 'First',
            'body': 'Body1'
        }
        client.post(reverse('send_message'), post_data1)
        
        post_data2 = {
            'recipient': org2.id,
            'subject': 'Second',
            'body': 'Body2'
        }
        client.post(reverse('send_message'), post_data2)
        
        assert Message.objects.count() == 2
        
        msg1 = Message.objects.filter(subject='First').first()
        assert msg1.recipient == org1
        
        msg2 = Message.objects.filter(subject='Second').first()
        assert msg2.recipient == org2
        
        runner.add_pass("Student can send multiple messages in sequence")
    except Exception as e:
        runner.add_fail("Student can send multiple messages in sequence", str(e))
    
    # Cleanup
    cleanup_messages(student)
    User.objects.filter(email__in=['test_student@example.com', 'test_org1@example.com', 'test_org2@example.com']).delete()
    
    # Summary
    return runner.print_summary()

if __name__ == '__main__':
    import sys
    success = run_tests()
    sys.exit(0 if success else 1)
