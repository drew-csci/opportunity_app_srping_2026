from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.messages import get_messages
from accounts.models import User
from pages.models import Message


class SendMessageViewStudentAccessTest(TestCase):
    """Test Test #7: send_message View - Student Access"""

    def setUp(self):
        """Set up test data before each test method."""
        # Create test student user
        self.student = User.objects.create_user(
            username='student_test',
            email='student_test@example.com',
            password='testpass123',
            user_type='student',
            first_name='Test',
            last_name='Student'
        )

        # Create test organization user (for recipient dropdown)
        self.organization = User.objects.create_user(
            username='org_test',
            email='org_test@example.com',
            password='testpass123',
            user_type='organization',
            first_name='Test',
            last_name='Organization'
        )

        # Create another organization for testing multiple options
        self.organization2 = User.objects.create_user(
            username='org2_test',
            email='org2_test@example.com',
            password='testpass123',
            user_type='organization',
            first_name='Another',
            last_name='Organization'
        )

        # Initialize test client
        self.client = Client()

    def test_send_message_get_request_displays_form(self):
        """Test that GET request to /send-message/ displays the form."""
        # Login as student
        self.client.force_login(self.student)

        # Make GET request
        response = self.client.get(reverse('send_message'))

        # Verify response status is 200 (OK)
        self.assertEqual(response.status_code, 200)

        # Verify correct template is used
        self.assertTemplateUsed(response, 'pages/send_message.html')

        # Verify form is in context
        self.assertIn('form', response.context)

        # Verify form fields are present
        form = response.context['form']
        self.assertIn('recipient', form.fields)
        self.assertIn('subject', form.fields)
        self.assertIn('body', form.fields)

    def test_send_message_form_includes_both_organizations(self):
        """Test that recipient dropdown includes all organizations."""
        # Login as student
        self.client.force_login(self.student)

        # Make GET request
        response = self.client.get(reverse('send_message'))

        # Get form
        form = response.context['form']

        # Get recipient field choices
        recipient_choices = [choice[1] for choice in form.fields['recipient'].choices]

        # Verify both organizations are in choices
        self.assertIn(str(self.organization), recipient_choices)
        self.assertIn(str(self.organization2), recipient_choices)

    def test_send_message_post_request_creates_message(self):
        """Test that POST request with valid data creates message in database."""
        # Login as student
        self.client.force_login(self.student)

        # Verify no messages exist initially
        initial_message_count = Message.objects.count()
        self.assertEqual(initial_message_count, 0)

        # Prepare POST data
        post_data = {
            'recipient': self.organization.id,
            'subject': 'Test Message Subject',
            'body': 'This is a test message body for the organization.'
        }

        # Make POST request
        response = self.client.post(reverse('send_message'), post_data)

        # Verify message was created in database
        self.assertEqual(Message.objects.count(), 1)

        # Get the created message
        created_message = Message.objects.first()

        # Verify message details
        self.assertEqual(created_message.sender, self.student)
        self.assertEqual(created_message.recipient, self.organization)
        self.assertEqual(created_message.subject, 'Test Message Subject')
        self.assertEqual(created_message.body, 'This is a test message body for the organization.')

    def test_send_message_post_redirects_after_success(self):
        """Test that POST request redirects after successful message creation."""
        # Login as student
        self.client.force_login(self.student)

        # Prepare POST data
        post_data = {
            'recipient': self.organization.id,
            'subject': 'Test Subject',
            'body': 'Test body'
        }

        # Make POST request
        response = self.client.post(reverse('send_message'), post_data)

        # Verify redirect (302 status code)
        self.assertEqual(response.status_code, 302)

        # Verify redirect is to the same page (send_message)
        self.assertRedirects(response, reverse('send_message'))

    def test_send_message_displays_success_message(self):
        """Test that success message is displayed after message sent."""
        # Login as student
        self.client.force_login(self.student)

        # Prepare POST data
        post_data = {
            'recipient': self.organization.id,
            'subject': 'Test Subject',
            'body': 'Test body'
        }

        # Make POST request - follow redirect to see messages
        response = self.client.post(
            reverse('send_message'),
            post_data,
            follow=True  # Follow the redirect
        )

        # Get messages from response
        messages_list = list(get_messages(response.wsgi_request))

        # Verify success message was added
        self.assertEqual(len(messages_list), 1)

        # Verify message content
        success_message = str(messages_list[0])
        self.assertEqual(success_message, 'Message sent successfully!')

        # Verify message level is success
        self.assertEqual(messages_list[0].level_tag, 'success')

    def test_send_message_form_validation_missing_recipient(self):
        """Test that form validation fails when recipient is missing."""
        # Login as student
        self.client.force_login(self.student)

        # Prepare POST data WITHOUT recipient
        post_data = {
            'subject': 'Test Subject',
            'body': 'Test body'
        }

        # Make POST request
        response = self.client.post(reverse('send_message'), post_data)

        # Verify no message was created
        self.assertEqual(Message.objects.count(), 0)

        # Verify response status is 200 (form re-displayed)
        self.assertEqual(response.status_code, 200)

        # Verify form has errors
        form = response.context['form']
        self.assertTrue(form.errors)
        self.assertIn('recipient', form.errors)

    def test_send_message_form_validation_missing_subject(self):
        """Test that form validation fails when subject is missing."""
        # Login as student
        self.client.force_login(self.student)

        # Prepare POST data WITHOUT subject
        post_data = {
            'recipient': self.organization.id,
            'body': 'Test body'
        }

        # Make POST request
        response = self.client.post(reverse('send_message'), post_data)

        # Verify no message was created
        self.assertEqual(Message.objects.count(), 0)

        # Verify response status is 200 (form re-displayed)
        self.assertEqual(response.status_code, 200)

        # Verify form has errors
        form = response.context['form']
        self.assertTrue(form.errors)
        self.assertIn('subject', form.errors)

    def test_send_message_form_validation_missing_body(self):
        """Test that form validation fails when body is missing."""
        # Login as student
        self.client.force_login(self.student)

        # Prepare POST data WITHOUT body
        post_data = {
            'recipient': self.organization.id,
            'subject': 'Test Subject'
        }

        # Make POST request
        response = self.client.post(reverse('send_message'), post_data)

        # Verify no message was created
        self.assertEqual(Message.objects.count(), 0)

        # Verify response status is 200 (form re-displayed)
        self.assertEqual(response.status_code, 200)

        # Verify form has errors
        form = response.context['form']
        self.assertTrue(form.errors)
        self.assertIn('body', form.errors)

    def test_send_message_sets_correct_sender(self):
        """Test that the logged-in student is set as sender."""
        # Login as student
        self.client.force_login(self.student)

        # Prepare POST data
        post_data = {
            'recipient': self.organization.id,
            'subject': 'Test Subject',
            'body': 'Test body'
        }

        # Make POST request
        self.client.post(reverse('send_message'), post_data)

        # Get created message
        message = Message.objects.first()

        # Verify sender is the logged-in student
        self.assertEqual(message.sender, self.student)
        self.assertEqual(message.sender.email, 'student_test@example.com')

    def test_send_message_timestamp_auto_generated(self):
        """Test that created_at timestamp is automatically generated."""
        # Login as student
        self.client.force_login(self.student)

        # Prepare POST data
        post_data = {
            'recipient': self.organization.id,
            'subject': 'Test Subject',
            'body': 'Test body'
        }

        # Make POST request
        self.client.post(reverse('send_message'), post_data)

        # Get created message
        message = Message.objects.first()

        # Verify created_at timestamp is set
        self.assertIsNotNone(message.created_at)

    def test_send_multiple_messages_in_sequence(self):
        """Test that student can send multiple messages."""
        # Login as student
        self.client.force_login(self.student)

        # Send first message
        post_data1 = {
            'recipient': self.organization.id,
            'subject': 'First Message',
            'body': 'First body'
        }
        self.client.post(reverse('send_message'), post_data1)

        # Send second message to different organization
        post_data2 = {
            'recipient': self.organization2.id,
            'subject': 'Second Message',
            'body': 'Second body'
        }
        self.client.post(reverse('send_message'), post_data2)

        # Verify both messages were created
        self.assertEqual(Message.objects.count(), 2)

        # Verify first message details
        first_msg = Message.objects.filter(subject='First Message').first()
        self.assertEqual(first_msg.recipient, self.organization)

        # Verify second message details
        second_msg = Message.objects.filter(subject='Second Message').first()
        self.assertEqual(second_msg.recipient, self.organization2)


class EndToEndStudentMessageFlowTest(TestCase):
    """Test #1 Integration: End-to-End Student Message Flow
    
    Validates the complete user journey: student sends message through form,
    message persists to database, and organization immediately sees it in inbox.
    """

    def setUp(self):
        """Set up test data before each test method."""
        # Create test student user
        self.student = User.objects.create_user(
            username='e2e_student',
            email='e2e_student@example.com',
            password='testpass123',
            user_type='student',
            first_name='EndToEnd',
            last_name='Student'
        )

        # Create test organization user
        self.organization = User.objects.create_user(
            username='e2e_org',
            email='e2e_org@example.com',
            password='testpass123',
            user_type='organization',
            first_name='EndToEnd',
            last_name='Organization'
        )

        # Initialize test clients (one for student, one for organization)
        self.student_client = Client()
        self.org_client = Client()

    def test_end_to_end_student_message_flow(self):
        """Test complete flow: send message → persist → view in inbox"""
        
        # Step 1: Student navigates to send message form
        self.student_client.force_login(self.student)
        response = self.student_client.get(reverse('send_message'))
        self.assertEqual(response.status_code, 200)
        self.assertIn('form', response.context)
        
        # Step 2: Student fills out and submits message form
        message_data = {
            'recipient': self.organization.id,
            'subject': 'Test Integration Message',
            'body': 'This is a complete end-to-end test of the messaging system.'
        }
        
        initial_message_count = Message.objects.count()
        
        # POST with follow=True to capture both redirect AND messages on landing page
        response = self.student_client.post(reverse('send_message'), message_data, follow=True)
        
        # Step 3: Verify message is saved to database with correct data
        final_message_count = Message.objects.count()
        self.assertEqual(final_message_count, initial_message_count + 1, 
                         "Message was not created in database")
        
        created_message = Message.objects.filter(
            subject='Test Integration Message'
        ).first()
        self.assertIsNotNone(created_message, "Message not found in database")
        self.assertEqual(created_message.sender, self.student, 
                         "Sender is not the student who submitted the form")
        self.assertEqual(created_message.recipient, self.organization, 
                         "Recipient is not the selected organization")
        self.assertEqual(created_message.body, 'This is a complete end-to-end test of the messaging system.',
                         "Message body does not match submitted data")
        self.assertIsNotNone(created_message.created_at, 
                             "Timestamp was not auto-generated")
        
        # Step 4: Verify student is redirected after submission
        # With follow=True, response.status_code will be 200 (final landing page)
        self.assertEqual(response.status_code, 200, 
                         "Student was not redirected properly (final response status should be 200)")
        
        # Step 5: Verify success message is displayed (from followed redirect)
        messages_list = list(get_messages(response.wsgi_request))
        self.assertGreater(len(messages_list), 0, "No success message was displayed")
        self.assertEqual(str(messages_list[0]), 'Message sent successfully!',
                         "Success message text is incorrect")
        
        # Step 6: Organization logs in and accesses inbox
        self.org_client.force_login(self.organization)
        inbox_response = self.org_client.get(reverse('organization_inbox'))
        
        self.assertEqual(inbox_response.status_code, 200,
                         "Organization cannot access inbox")
        self.assertIn('messages', inbox_response.context,
                      "Inbox context missing 'messages'")
        self.assertIn('message_count', inbox_response.context,
                      "Inbox context missing 'message_count'")
        
        # Step 7: Verify message appears in organization's inbox
        inbox_messages = inbox_response.context['messages']
        message_subjects = [msg.subject for msg in inbox_messages]
        self.assertIn('Test Integration Message', message_subjects,
                      "Sent message does not appear in organization's inbox")
        
        # Step 8: Verify message_count is correct
        self.assertEqual(inbox_response.context['message_count'], 1,
                         "Message count in context does not match actual messages")
        
        # Step 9: Verify message displays with correct data
        inbox_message = Message.objects.get(subject='Test Integration Message')
        self.assertEqual(inbox_message.sender.display_name, 'EndToEnd Student',
                         "Sender display name is incorrect")
        self.assertEqual(inbox_message.subject, 'Test Integration Message',
                         "Subject in inbox differs from sent message")
        self.assertIsNotNone(inbox_message.created_at,
                             "Message missing created_at timestamp for display")
        
        # Verify message is in correct order (newest first)
        first_message_in_inbox = list(inbox_messages)[0]
        self.assertEqual(first_message_in_inbox.id, inbox_message.id,
                         "Message not appearing as newest in inbox")

    def test_message_not_visible_to_other_organizations(self):
        """Verify message sent to Org A is not visible to Org B (data privacy)"""
        
        # Create a second organization
        org_b = User.objects.create_user(
            username='e2e_org_b',
            email='e2e_org_b@example.com',
            password='testpass123',
            user_type='organization',
            first_name='Organization',
            last_name='B'
        )
        
        # Student sends message to Org A
        self.student_client.force_login(self.student)
        message_data = {
            'recipient': self.organization.id,
            'subject': 'Private Message to Org A',
            'body': 'This should only be visible to Org A'
        }
        self.student_client.post(reverse('send_message'), message_data)
        
        # Organization A verifies message is in their inbox
        org_a_client = Client()
        org_a_client.force_login(self.organization)
        org_a_inbox = org_a_client.get(reverse('organization_inbox'))
        org_a_messages = list(org_a_inbox.context['messages'])
        
        self.assertEqual(len(org_a_messages), 1,
                         "Organization A should see exactly 1 message")
        self.assertEqual(org_a_messages[0].subject, 'Private Message to Org A',
                         "Organization A message subject is incorrect")
        
        # Organization B verifies message is NOT in their inbox
        org_b_client = Client()
        org_b_client.force_login(org_b)
        org_b_inbox = org_b_client.get(reverse('organization_inbox'))
        org_b_messages = list(org_b_inbox.context['messages'])
        
        self.assertEqual(len(org_b_messages), 0,
                         "Organization B should not see any messages")
        
        message_subjects_visible_to_b = [msg.subject for msg in org_b_messages]
        self.assertNotIn('Private Message to Org A', message_subjects_visible_to_b,
                         "Organization B can see messages sent to Organization A!")

