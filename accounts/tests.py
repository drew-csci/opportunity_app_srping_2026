from django.core import mail
from django.test import TestCase
from django.test import override_settings
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes


@override_settings(EMAIL_BACKEND='django.core.mail.backends.locmem.EmailBackend')
class AuthFlowTests(TestCase):
	def setUp(self):
		self.user_model = get_user_model()
		self.email = 'student@example.com'
		self.password = 'StrongPass123!'
		self.user = self.user_model.objects.create_user(
			email=self.email,
			username=self.email,
			password=self.password,
		)

	def test_login_with_email_succeeds(self):
		response = self.client.post(
			reverse('login'),
			{'username': self.email, 'password': self.password},
			follow=True,
		)
		self.assertTrue(response.context['user'].is_authenticated)

	def test_password_reset_request_sends_email_for_existing_user(self):
		response = self.client.post(reverse('password_reset'), {'email': self.email}, follow=True)

		self.assertRedirects(response, reverse('password_reset_done'))
		self.assertEqual(len(mail.outbox), 1)
		self.assertIn('Opportunity App password reset', mail.outbox[0].subject)

	def test_password_reset_request_is_non_enumerating_for_unknown_email(self):
		response = self.client.post(reverse('password_reset'), {'email': 'unknown@example.com'}, follow=True)

		self.assertRedirects(response, reverse('password_reset_done'))
		self.assertEqual(len(mail.outbox), 0)

	def test_password_reset_confirm_with_valid_token_updates_password(self):
		uid = urlsafe_base64_encode(force_bytes(self.user.pk))
		token = default_token_generator.make_token(self.user)
		reset_url = reverse('password_reset_confirm', kwargs={'uidb64': uid, 'token': token})
		new_password = 'BrandNew123!'

		response = self.client.get(reset_url, follow=True)
		post_url = response.request['PATH_INFO']

		response = self.client.post(
			post_url,
			{'new_password1': new_password, 'new_password2': new_password},
			follow=True,
		)

		self.assertRedirects(response, reverse('password_reset_complete'))
		self.user.refresh_from_db()
		self.assertTrue(self.user.check_password(new_password))
		self.assertFalse(self.user.check_password(self.password))

	def test_password_reset_confirm_with_invalid_token_shows_error(self):
		uid = urlsafe_base64_encode(force_bytes(self.user.pk))
		url = reverse('password_reset_confirm', kwargs={'uidb64': uid, 'token': 'invalid-token'})

		response = self.client.get(url)

		self.assertContains(response, 'invalid or has expired')

	def test_custom_set_password_form_requires_matching_passwords(self):
		"""
		Test that CustomSetPasswordForm rejects mismatched passwords.
		This prevents user error where copy-paste or typos result in
		a password set that the user can't log in with.
		"""
		from accounts.forms import CustomSetPasswordForm

		# Create a test user
		test_user = self.user_model.objects.create_user(
			email='mismatch@example.com',
			username='mismatch@example.com',
			password='OldPassword123!'
		)

		# Attempt to set mismatched passwords
		form = CustomSetPasswordForm(user=test_user, data={
			'new_password1': 'NewPassword123!',
			'new_password2': 'DifferentPassword456!'  # Doesn't match
		})

		# Form should be invalid
		self.assertFalse(form.is_valid())
		# Error should be on new_password2 field
		self.assertIn('new_password2', form.errors)
		# Error message should mention passwords don't match
		error_msg = str(form.errors['new_password2'][0]).lower()
		self.assertIn('match', error_msg)

	def test_complete_password_reset_flow_returns_to_login(self):
		"""
		Integration test: Complete flow from reset request through successful login.
		Tests: Form → Email sending → Token validation → Password update → Login
		
		This is a critical end-to-end test that verifies all password reset 
		components work together correctly.
		"""
		user_email = 'complete@example.com'
		user = self.user_model.objects.create_user(
			email=user_email,
			username=user_email,
			password='OldPassword123!'
		)

		# Step 1: Request password reset
		response = self.client.post(reverse('password_reset'), {'email': user_email}, follow=True)
		self.assertRedirects(response, reverse('password_reset_done'))

		# Step 2: Verify email was sent
		self.assertEqual(len(mail.outbox), 1)
		reset_email = mail.outbox[0]
		self.assertIn('Opportunity App password reset', reset_email.subject)

		# Step 3: Extract token from email (simulate clicking link)
		uid = urlsafe_base64_encode(force_bytes(user.pk))
		token = default_token_generator.make_token(user)
		reset_url = reverse('password_reset_confirm', kwargs={'uidb64': uid, 'token': token})

		# Step 4: Access the reset link
		response = self.client.get(reset_url, follow=True)
		self.assertEqual(response.status_code, 200)

		# Step 5: Submit new password
		new_password = 'BrandNewPassword123!'
		response = self.client.post(
			reset_url,
			{'new_password1': new_password, 'new_password2': new_password},
			follow=True
		)
		self.assertRedirects(response, reverse('password_reset_complete'))

		# Step 6: Verify password was actually changed in database
		user.refresh_from_db()
		self.assertTrue(user.check_password(new_password))
		self.assertFalse(user.check_password('OldPassword123!'))

		# Step 7: Log in with new password
		login_success = self.client.login(email=user_email, password=new_password)
		self.assertTrue(login_success)

		# Step 8: Verify user is authenticated and can access dashboard
		response = self.client.get(reverse('dashboard'))
		self.assertEqual(response.status_code, 200)
		self.assertTrue(response.context['user'].is_authenticated)
