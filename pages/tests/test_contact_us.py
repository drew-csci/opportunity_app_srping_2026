from django.test import TestCase
from django.urls import reverse

from accounts.models import User
from pages.models import ContactMessage
from pages.forms import ContactForm


class ContactFormUnitTest(TestCase):
    """Unit tests for ContactForm validation."""

    def _valid_data(self, **overrides):
        data = {
            'first_name': 'Jane',
            'last_name': 'Doe',
            'email': 'jane@example.com',
            'role': 'student',
            'inquiry_type': 'general',
            'subject': 'Test subject',
            'message': 'Test message body',
        }
        data.update(overrides)
        return data

    def test_contact_form_valid_data_is_valid(self):
        form = ContactForm(data=self._valid_data())
        self.assertTrue(form.is_valid(), form.errors)

    def test_contact_form_missing_first_name_is_invalid(self):
        form = ContactForm(data=self._valid_data(first_name=''))
        self.assertFalse(form.is_valid())
        self.assertIn('first_name', form.errors)

    def test_contact_form_missing_last_name_is_invalid(self):
        form = ContactForm(data=self._valid_data(last_name=''))
        self.assertFalse(form.is_valid())
        self.assertIn('last_name', form.errors)

    def test_contact_form_invalid_email_is_invalid(self):
        form = ContactForm(data=self._valid_data(email='not-an-email'))
        self.assertFalse(form.is_valid())
        self.assertIn('email', form.errors)

    def test_contact_form_missing_message_is_invalid(self):
        form = ContactForm(data=self._valid_data(message=''))
        self.assertFalse(form.is_valid())
        self.assertIn('message', form.errors)

    def test_contact_form_save_creates_contact_message(self):
        form = ContactForm(data=self._valid_data())
        self.assertTrue(form.is_valid())
        form.save()
        self.assertEqual(ContactMessage.objects.count(), 1)
        msg = ContactMessage.objects.first()
        self.assertEqual(msg.first_name, 'Jane')
        self.assertEqual(msg.email, 'jane@example.com')
        self.assertEqual(msg.inquiry_type, 'general')


class ContactUsIntegrationTest(TestCase):
    """Integration tests for the Contact Us page view."""

    def setUp(self):
        self.student = User.objects.create_user(
            username='contact_student',
            password='Pass123!',
            user_type='student',
            first_name='Jane',
            last_name='Doe',
            email='jane@example.com',
        )
        self.org = User.objects.create_user(
            username='contact_org',
            password='Pass123!',
            user_type='organization',
            email='org@example.com',
        )

    def test_contact_page_requires_login(self):
        response = self.client.get(reverse('contact_us'))
        self.assertNotEqual(response.status_code, 200)

    def test_contact_page_loads_for_student(self):
        self.client.login(email='jane@example.com', password='Pass123!')
        response = self.client.get(reverse('contact_us'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Contact Us')

    def test_contact_page_loads_for_organization(self):
        self.client.login(email='org@example.com', password='Pass123!')
        response = self.client.get(reverse('contact_us'))
        self.assertEqual(response.status_code, 200)

    def test_valid_post_saves_to_database(self):
        self.client.login(email='jane@example.com', password='Pass123!')
        self.client.post(reverse('contact_us'), {
            'first_name': 'Jane',
            'last_name': 'Doe',
            'email': 'jane@example.com',
            'role': 'student',
            'inquiry_type': 'general',
            'subject': 'Need help',
            'message': 'I have a question about my application.',
        })
        self.assertEqual(ContactMessage.objects.count(), 1)

    def test_valid_post_shows_success_confirmation(self):
        self.client.login(email='jane@example.com', password='Pass123!')
        response = self.client.post(reverse('contact_us'), {
            'first_name': 'Jane',
            'last_name': 'Doe',
            'email': 'jane@example.com',
            'role': 'student',
            'inquiry_type': 'technical',
            'subject': 'Login issue',
            'message': 'I cannot log in to my account.',
        })
        self.assertContains(response, 'success', msg_prefix='Success message not shown after valid submission')

    def test_invalid_post_does_not_save(self):
        self.client.login(email='jane@example.com', password='Pass123!')
        self.client.post(reverse('contact_us'), {
            'first_name': '',
            'last_name': '',
            'email': 'bad-email',
            'role': 'student',
            'inquiry_type': 'general',
            'subject': '',
            'message': '',
        })
        self.assertEqual(ContactMessage.objects.count(), 0)

    def test_invalid_post_redisplays_form_with_errors(self):
        self.client.login(email='jane@example.com', password='Pass123!')
        response = self.client.post(reverse('contact_us'), {
            'first_name': '',
            'last_name': '',
            'email': 'not-valid',
            'role': 'student',
            'inquiry_type': 'general',
            'subject': '',
            'message': '',
        })
        self.assertEqual(response.status_code, 200)
        self.assertFalse(response.context['success'])
