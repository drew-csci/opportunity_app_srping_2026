#!/usr/bin/env python
"""
Comprehensive test script for Organization Inbox messaging system
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'opportunity_app.settings')
django.setup()

from pages.models import Message
from pages.forms import MessageForm
from accounts.models import User
from django.test.client import Client
from django.urls import reverse

def test_message_model():
    """Test Message model and querysets"""
    print("=" * 70)
    print("TEST 1: Message Model Functionality")
    print("=" * 70)
    try:
        message_count = Message.objects.all().count()
        print(f"✓ Message model queryset works. Total messages in DB: {message_count}")
        
        fields = [f.name for f in Message._meta.get_fields()]
        print(f"✓ Message fields: {fields}")
        
        required_fields = ['sender', 'recipient', 'subject', 'body', 'created_at', 'updated_at']
        for field in required_fields:
            if field in fields:
                print(f"  ✓ {field} present")
            else:
                print(f"  ✗ {field} MISSING")
        return True
    except Exception as e:
        print(f"✗ Error with Message model: {e}")
        return False

def test_message_form():
    """Test MessageForm instantiation and validation"""
    print("\n" + "=" * 70)
    print("TEST 2: MessageForm Functionality")
    print("=" * 70)
    try:
        form = MessageForm()
        print(f"✓ MessageForm instantiated successfully")
        form_fields = list(form.fields.keys())
        print(f"✓ Form fields: {form_fields}")
        
        required = ['recipient', 'subject', 'body']
        for field in required:
            if field in form_fields:
                print(f"  ✓ {field} present")
            else:
                print(f"  ✗ {field} MISSING")
        return True
    except Exception as e:
        print(f"✗ Error with MessageForm: {e}")
        return False

def test_users():
    """Test that test users exist"""
    print("\n" + "=" * 70)
    print("TEST 3: User Accounts")
    print("=" * 70)
    try:
        org_count = User.objects.filter(user_type='organization').count()
        student_count = User.objects.filter(user_type='student').count()
        admin_count = User.objects.filter(user_type='administrator').count()
        
        print(f"✓ Organization users: {org_count}")
        print(f"✓ Student users: {student_count}")
        print(f"✓ Administrator users: {admin_count}")
        
        if student_count > 0:
            student = User.objects.filter(user_type='student').first()
            print(f"  - Sample student: {student.display_name} ({student.email})")
        
        if org_count > 0:
            org = User.objects.filter(user_type='organization').first()
            print(f"  - Sample organization: {org.display_name} ({org.email})")
        
        return org_count > 0 and student_count > 0
    except Exception as e:
        print(f"✗ Error checking users: {e}")
        return False

def test_urls():
    """Test that URLs are registered"""
    print("\n" + "=" * 70)
    print("TEST 4: URL Routing")
    print("=" * 70)
    try:
        send_msg_url = reverse('send_message')
        inbox_url = reverse('organization_inbox')
        
        print(f"✓ send_message URL: {send_msg_url}")
        print(f"✓ organization_inbox URL: {inbox_url}")
        
        return True
    except Exception as e:
        print(f"✗ Error with URLs: {e}")
        return False

def test_views():
    """Test view imports and decorators are properly set"""
    print("\n" + "=" * 70)
    print("TEST 5: View Decorators and Access Control")
    print("=" * 70)
    
    try:
        from pages.views import send_message, organization_inbox
        import inspect
        
        # Check that views have login_required decorator
        send_msg_source = inspect.getsource(send_message)
        inbox_source = inspect.getsource(organization_inbox)
        
        has_login_check = '@login_required' in send_msg_source or 'login_required' in send_msg_source
        has_user_check = "user_type != 'student'" in send_msg_source
        
        print(f"✓ send_message view code:")
        print(f"  {'✓' if has_login_check else '✗'} Has @login_required decorator")
        print(f"  {'✓' if has_user_check else '✗'} Has user_type='student' check")
        
        has_login_check_inbox = 'login_required' in inbox_source
        has_user_check_inbox = "user_type != 'organization'" in inbox_source
        
        print(f"✓ organization_inbox view code:")
        print(f"  {'✓' if has_login_check_inbox else '✗'} Has @login_required decorator")
        print(f"  {'✓' if has_user_check_inbox else '✗'} Has user_type='organization' check")
        
        return all([has_login_check, has_user_check, has_login_check_inbox, has_user_check_inbox])
    except Exception as e:
        print(f"✗ Error testing views: {e}")
        return False

def test_message_creation():
    """Test creating a message in database"""
    print("\n" + "=" * 70)
    print("TEST 6: Message Creation")
    print("=" * 70)
    
    try:
        # Get or create test users
        students = User.objects.filter(user_type='student')
        orgs = User.objects.filter(user_type='organization')
        
        if not students.exists() or not orgs.exists():
            print("⚠ Not enough users to test message creation (need student and organization)")
            return False
        
        sender = students.first()
        recipient = orgs.first()
        
        # Create test message
        message = Message.objects.create(
            sender=sender,
            recipient=recipient,
            subject="Test Message",
            body="This is a test message for verification."
        )
        
        print(f"✓ Message created successfully")
        print(f"  - From: {message.sender.display_name}")
        print(f"  - To: {message.recipient.display_name}")
        print(f"  - Subject: {message.subject}")
        print(f"  - Created: {message.created_at}")
        
        # Test retrieval
        retrieved = Message.objects.get(pk=message.pk)
        print(f"✓ Message retrieved from database")
        
        # Test queryset filtering
        org_messages = Message.objects.filter(recipient=recipient)
        print(f"✓ Found {org_messages.count()} message(s) for organization")
        
        # Clean up
        message.delete()
        print(f"✓ Test message deleted")
        
        return True
    except Exception as e:
        print(f"✗ Error with message creation: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_templates_exist():
    """Test that template files exist"""
    print("\n" + "=" * 70)
    print("TEST 7: Template Files")
    print("=" * 70)
    
    template_files = [
        'templates/pages/send_message.html',
        'templates/pages/inbox.html',
        'templates/pages/message_detail.html',
    ]
    
    import os
    results = []
    for template in template_files:
        path = os.path.join(os.getcwd(), template)
        if os.path.exists(path):
            print(f"✓ {template} exists")
            results.append(True)
        else:
            print(f"✗ {template} NOT FOUND")
            results.append(False)
    
    return all(results)

def main():
    """Run all tests"""
    print("\n")
    print("╔" + "=" * 68 + "╗")
    print("║" + " " * 20 + "MESSAGING SYSTEM TEST SUITE" + " " * 21 + "║")
    print("╚" + "=" * 68 + "╝")
    
    tests = [
        ("Message Model", test_message_model),
        ("MessageForm", test_message_form),
        ("User Accounts", test_users),
        ("URL Routing", test_urls),
        ("View Access Control", test_views),
        ("Message Creation", test_message_creation),
        ("Template Files", test_templates_exist),
    ]
    
    results = {}
    for test_name, test_func in tests:
        results[test_name] = test_func()
    
    # Summary
    print("\n" + "=" * 70)
    print("TEST SUMMARY")
    print("=" * 70)
    
    passed = sum(1 for v in results.values() if v)
    total = len(results)
    
    for test_name, result in results.items():
        status = "✓ PASS" if result else "✗ FAIL"
        print(f"{status}: {test_name}")
    
    print("-" * 70)
    print(f"TOTAL: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n✓ ALL TESTS PASSED - System is ready!")
    else:
        print(f"\n⚠ {total - passed} test(s) failed - Review above for details")
    
    return passed == total

if __name__ == '__main__':
    success = main()
    exit(0 if success else 1)
