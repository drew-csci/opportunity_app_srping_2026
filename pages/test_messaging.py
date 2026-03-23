from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.utils import timezone
from .models import Message, MessageReply

User = get_user_model()


class MessagingInboxTestCase(TestCase):
    """Test cases for organization messaging inbox functionality"""
    
    def setUp(self):
        """Set up test users and client"""
        self.client = Client()
        
        # Create a student user
        self.student = User.objects.create_user(
            email='student@test.com',
            username='student_user',
            password='testpass123',
            user_type='student',
            first_name='John',
            last_name='Doe'
        )
        
        # Create an organization user
        self.organization = User.objects.create_user(
            email='org@test.com',
            username='org_user',
            password='testpass123',
            user_type='organization',
            first_name='Test',
            last_name='Organization'
        )
        
        # Create another student for testing
        self.student2 = User.objects.create_user(
            email='student2@test.com',
            username='student_user2',
            password='testpass123',
            user_type='student',
            first_name='Jane',
            last_name='Smith'
        )
    
    def test_organization_can_access_inbox(self):
        """Test that organization users can access their inbox"""
        self.client.login(email='org@test.com', password='testpass123')
        response = self.client.get(reverse('organization_inbox'))
        
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'pages/inbox.html')
    
    def test_student_cannot_access_inbox(self):
        """Test that student users are redirected when accessing organization inbox"""
        self.client.login(email='student@test.com', password='testpass123')
        response = self.client.get(reverse('organization_inbox'), follow=False)
        
        self.assertEqual(response.status_code, 302)
        self.assertIn('screen1', response.url)
    
    def test_unauthenticated_user_redirected_to_login(self):
        """Test that unauthenticated users are redirected to login"""
        response = self.client.get(reverse('organization_inbox'), follow=False)
        
        self.assertEqual(response.status_code, 302)
        self.assertIn('login', response.url)
    
    def test_inbox_displays_messages_newest_first(self):
        """Test that messages are displayed newest first"""
        # Create messages at different times
        msg1 = Message.objects.create(
            sender=self.student,
            recipient=self.organization,
            subject='First Message',
            content='Content 1'
        )
        
        # Create second message (should be newer)
        msg2 = Message.objects.create(
            sender=self.student2,
            recipient=self.organization,
            subject='Second Message',
            content='Content 2'
        )
        
        self.client.login(email='org@test.com', password='testpass123')
        response = self.client.get(reverse('organization_inbox'))
        
        messages_list = response.context['messages']
        self.assertEqual(len(messages_list), 2)
        self.assertEqual(messages_list[0].id, msg2.id)
        self.assertEqual(messages_list[1].id, msg1.id)
    
    def test_unread_count_displayed_correctly(self):
        """Test that unread message count is displayed correctly"""
        # Create one unread message
        Message.objects.create(
            sender=self.student,
            recipient=self.organization,
            subject='Unread Message',
            content='Test content',
            is_read=False
        )
        
        # Create one read message
        Message.objects.create(
            sender=self.student2,
            recipient=self.organization,
            subject='Read Message',
            content='Test content',
            is_read=True
        )
        
        self.client.login(email='org@test.com', password='testpass123')
        response = self.client.get(reverse('organization_inbox'))
        
        self.assertEqual(response.context['unread_count'], 1)
    
    def test_inbox_shows_only_recipient_messages(self):
        """Test that organization only sees messages sent to them"""
        # Create message to this organization
        msg1 = Message.objects.create(
            sender=self.student,
            recipient=self.organization,
            subject='To Org',
            content='Content'
        )
        
        # Create another organization
        other_org = User.objects.create_user(
            email='other_org@test.com',
            username='other_org',
            password='testpass123',
            user_type='organization'
        )
        
        # Create message to other organization
        msg2 = Message.objects.create(
            sender=self.student2,
            recipient=other_org,
            subject='To Other Org',
            content='Content'
        )
        
        self.client.login(email='org@test.com', password='testpass123')
        response = self.client.get(reverse('organization_inbox'))
        
        messages_list = response.context['messages']
        self.assertEqual(len(messages_list), 1)
        self.assertEqual(messages_list[0].id, msg1.id)


class MessageDetailTestCase(TestCase):
    """Test cases for viewing message details and replying"""
    
    def setUp(self):
        """Set up test users and messages"""
        self.client = Client()
        
        self.student = User.objects.create_user(
            email='student@test.com',
            username='student_user',
            password='testpass123',
            user_type='student',
            first_name='John',
            last_name='Doe'
        )
        
        self.organization = User.objects.create_user(
            email='org@test.com',
            username='org_user',
            password='testpass123',
            user_type='organization',
            first_name='Test',
            last_name='Organization'
        )
        
        self.message = Message.objects.create(
            sender=self.student,
            recipient=self.organization,
            subject='Test Message',
            content='This is a test message',
            is_read=False
        )
    
    def test_can_view_message_detail(self):
        """Test that organization can view message details"""
        self.client.login(email='org@test.com', password='testpass123')
        response = self.client.get(reverse('message_detail', args=[self.message.id]))
        
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'pages/message_detail.html')
        self.assertEqual(response.context['message'].id, self.message.id)
    
    def test_viewing_message_marks_as_read(self):
        """Test that viewing a message marks it as read"""
        self.assertTrue(not self.message.is_read)
        
        self.client.login(email='org@test.com', password='testpass123')
        self.client.get(reverse('message_detail', args=[self.message.id]))
        
        self.message.refresh_from_db()
        self.assertTrue(self.message.is_read)
    
    def test_cannot_view_others_messages(self):
        """Test that organization cannot view messages not addressed to them"""
        other_org = User.objects.create_user(
            email='other_org@test.com',
            username='other_org',
            password='testpass123',
            user_type='organization'
        )
        
        self.client.login(email='other_org@test.com', password='testpass123')
        response = self.client.get(reverse('message_detail', args=[self.message.id]), follow=False)
        
        self.assertEqual(response.status_code, 404)
    
    def test_reply_form_displayed(self):
        """Test that reply form is displayed on message detail page"""
        self.client.login(email='org@test.com', password='testpass123')
        response = self.client.get(reverse('message_detail', args=[self.message.id]))
        
        self.assertIn('form', response.context)
        self.assertIn('content', response.context['form'].fields)


class MessageReplyTestCase(TestCase):
    """Test cases for sending replies to messages"""
    
    def setUp(self):
        """Set up test users and messages"""
        self.client = Client()
        
        self.student = User.objects.create_user(
            email='student@test.com',
            username='student_user',
            password='testpass123',
            user_type='student',
            first_name='John',
            last_name='Doe'
        )
        
        self.organization = User.objects.create_user(
            email='org@test.com',
            username='org_user',
            password='testpass123',
            user_type='organization',
            first_name='Test',
            last_name='Organization'
        )
        
        self.message = Message.objects.create(
            sender=self.student,
            recipient=self.organization,
            subject='Test Message',
            content='This is a test message'
        )
    
    def test_successful_reply(self):
        """Test that organization can successfully reply to a message"""
        self.client.login(email='org@test.com', password='testpass123')
        
        response = self.client.post(
            reverse('message_detail', args=[self.message.id]),
            {'content': 'This is a test reply'},
            follow=True
        )
        
        self.assertEqual(response.status_code, 200)
        self.assertEqual(self.message.replies.count(), 1)
        
        reply = self.message.replies.first()
        self.assertEqual(reply.content, 'This is a test reply')
        self.assertEqual(reply.sender.id, self.organization.id)
    
    def test_empty_reply_validation(self):
        """Test that empty reply shows validation error"""
        self.client.login(email='org@test.com', password='testpass123')
        
        response = self.client.post(
            reverse('message_detail', args=[self.message.id]),
            {'content': ''},
            follow=False
        )
        
        self.assertEqual(response.status_code, 200)
        self.assertFormError(response, 'form', 'content', 'Reply cannot be empty.')
        self.assertEqual(self.message.replies.count(), 0)
    
    def test_whitespace_only_reply_validation(self):
        """Test that whitespace-only reply shows validation error"""
        self.client.login(email='org@test.com', password='testpass123')
        
        response = self.client.post(
            reverse('message_detail', args=[self.message.id]),
            {'content': '   \n  \t  '},
            follow=False
        )
        
        self.assertEqual(response.status_code, 200)
        self.assertFormError(response, 'form', 'content', 'Reply cannot be empty.')
        self.assertEqual(self.message.replies.count(), 0)
    
    def test_multiple_replies(self):
        """Test that multiple replies can be added to a single message"""
        self.client.login(email='org@test.com', password='testpass123')
        
        # First reply
        self.client.post(
            reverse('message_detail', args=[self.message.id]),
            {'content': 'First reply'}
        )
        
        # Second reply
        self.client.post(
            reverse('message_detail', args=[self.message.id]),
            {'content': 'Second reply'}
        )
        
        self.assertEqual(self.message.replies.count(), 2)
    
    def test_replies_ordered_chronologically(self):
        """Test that replies are ordered by creation time"""
        # Create replies manually to control timing
        reply1 = MessageReply.objects.create(
            message=self.message,
            sender=self.organization,
            content='First reply'
        )
        
        reply2 = MessageReply.objects.create(
            message=self.message,
            sender=self.organization,
            content='Second reply'
        )
        
        self.client.login(email='org@test.com', password='testpass123')
        response = self.client.get(reverse('message_detail', args=[self.message.id]))
        
        replies = response.context['replies']
        self.assertEqual(replies[0].id, reply1.id)
        self.assertEqual(replies[1].id, reply2.id)
    
    def test_reply_contains_sender_info(self):
        """Test that reply displays sender information correctly"""
        self.client.login(email='org@test.com', password='testpass123')
        
        self.client.post(
            reverse('message_detail', args=[self.message.id]),
            {'content': 'Test reply'}
        )
        
        reply = self.message.replies.first()
        self.assertEqual(reply.sender.id, self.organization.id)
        self.assertIsNotNone(reply.created_at)


class SendMessageTestCase(TestCase):
    """Test cases for students sending messages to organizations"""
    
    def setUp(self):
        """Set up test users"""
        self.client = Client()
        
        self.student = User.objects.create_user(
            email='student@test.com',
            username='student_user',
            password='testpass123',
            user_type='student',
            first_name='John',
            last_name='Doe'
        )
        
        self.organization = User.objects.create_user(
            email='org@test.com',
            username='org_user',
            password='testpass123',
            user_type='organization',
            first_name='Test',
            last_name='Organization'
        )
    
    def test_student_can_send_message(self):
        """Test that student can send a message to organization"""
        self.client.login(email='student@test.com', password='testpass123')
        
        response = self.client.post(
            reverse('send_message', args=[self.organization.id]),
            {
                'subject': 'Test Subject',
                'content': 'This is a test message'
            },
            follow=True
        )
        
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'pages/message_sent_success.html')
        self.assertEqual(Message.objects.count(), 1)
        
        message = Message.objects.first()
        self.assertEqual(message.sender.id, self.student.id)
        self.assertEqual(message.recipient.id, self.organization.id)
        self.assertEqual(message.subject, 'Test Subject')
        self.assertEqual(message.content, 'This is a test message')
    
    def test_empty_message_content_validation(self):
        """Test that empty message content shows validation error"""
        self.client.login(email='student@test.com', password='testpass123')
        
        response = self.client.post(
            reverse('send_message', args=[self.organization.id]),
            {
                'subject': 'Test Subject',
                'content': ''
            }
        )
        
        self.assertFormError(response, 'form', 'content', 'Message content cannot be empty.')
        self.assertEqual(Message.objects.count(), 0)
    
    def test_message_with_optional_subject(self):
        """Test that message can be sent without subject"""
        self.client.login(email='student@test.com', password='testpass123')
        
        response = self.client.post(
            reverse('send_message', args=[self.organization.id]),
            {
                'subject': '',
                'content': 'Message without subject'
            },
            follow=True
        )
        
        self.assertEqual(response.status_code, 200)
        
        message = Message.objects.first()
        self.assertEqual(message.subject, '')
        self.assertEqual(message.content, 'Message without subject')


class UnreadCountAPITestCase(TestCase):
    """Test cases for unread message count API"""
    
    def setUp(self):
        """Set up test users and messages"""
        self.client = Client()
        
        self.student = User.objects.create_user(
            email='student@test.com',
            username='student_user',
            password='testpass123',
            user_type='student'
        )
        
        self.organization = User.objects.create_user(
            email='org@test.com',
            username='org_user',
            password='testpass123',
            user_type='organization'
        )
        
        # Create test messages
        Message.objects.create(
            sender=self.student,
            recipient=self.organization,
            content='Message 1',
            is_read=False
        )
        
        Message.objects.create(
            sender=self.student,
            recipient=self.organization,
            content='Message 2',
            is_read=False
        )
        
        Message.objects.create(
            sender=self.student,
            recipient=self.organization,
            content='Message 3',
            is_read=True
        )
    
    def test_get_unread_count_for_organization(self):
        """Test that API returns correct unread count for organization"""
        self.client.login(email='org@test.com', password='testpass123')
        response = self.client.get(reverse('get_unread_count'))
        
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['unread_count'], 2)
    
    def test_get_unread_count_for_student(self):
        """Test that API returns 0 for student users"""
        self.client.login(email='student@test.com', password='testpass123')
        response = self.client.get(reverse('get_unread_count'))
        
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['unread_count'], 0)
    
    def test_unread_count_updates_after_reading(self):
        """Test that unread count updates after reading messages"""
        self.client.login(email='org@test.com', password='testpass123')
        
        # Get initial count
        response = self.client.get(reverse('get_unread_count'))
        self.assertEqual(response.json()['unread_count'], 2)
        
        # Mark first message as read
        message = Message.objects.filter(is_read=False).first()
        message.is_read = True
        message.save()
        
        # Get updated count
        response = self.client.get(reverse('get_unread_count'))
        self.assertEqual(response.json()['unread_count'], 1)
