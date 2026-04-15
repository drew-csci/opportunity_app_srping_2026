from pathlib import Path

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

User = get_user_model()

"""Integration Tests used for UI validation of the newly designed authentication templates (login and register)."""
class AuthUiTemplateTests(TestCase):
	def setUp(self):
		self.login_url = reverse('login')
		self.register_url = reverse('register')
		self.screen1_url = reverse('screen1')

	def test_login_template_contains_new_ui_sections(self):
		response = self.client.get(self.login_url)
		self.assertEqual(response.status_code, 200)
		self.assertContains(response, 'class="auth-shell"')
		self.assertContains(response, 'class="auth-card"')
		self.assertContains(response, 'class="auth-badge"')
		self.assertContains(response, 'class="auth-subtitle"')
		self.assertContains(response, 'class="auth-links"')
		self.assertContains(response, 'class="auth-note"')
		self.assertContains(response, 'href="#"')

	def test_login_with_type_renders_role_heading_and_register_link_query(self):
		response = self.client.get(f'{self.login_url}?type=organization')
		self.assertEqual(response.status_code, 200)
		self.assertContains(response, 'Sign in as Organization')
		self.assertContains(response, f'{self.register_url}?type=organization')

	def test_register_template_contains_new_ui_sections(self):
		response = self.client.get(self.register_url)
		self.assertEqual(response.status_code, 200)
		self.assertContains(response, 'class="auth-shell"')
		self.assertContains(response, 'class="auth-card"')
		self.assertContains(response, 'class="auth-badge"')
		self.assertContains(response, 'class="auth-subtitle"')
		self.assertContains(response, 'class="auth-links"')
		self.assertContains(response, 'class="auth-note"')
		self.assertContains(response, 'Create Account')

	def test_register_prefills_user_type_from_query_param(self):
		response = self.client.get(f'{self.register_url}?type=student')
		self.assertEqual(response.status_code, 200)
		self.assertEqual(response.context['form'].initial.get('user_type'), 'student')

	def test_register_prefills_user_type_from_session_set_by_login(self):
		self.client.get(f'{self.login_url}?type=administrator')
		response = self.client.get(self.register_url)
		self.assertEqual(response.status_code, 200)
		self.assertEqual(response.context['form'].initial.get('user_type'), 'administrator')

	def test_register_creates_user_logs_in_and_redirects(self):
		payload = {
			'email': 'ui-register-test@example.com',
			'user_type': 'student',
			'password1': 'StrongPass123!',
			'password2': 'StrongPass123!',
		}
		response = self.client.post(self.register_url, data=payload)
		self.assertRedirects(response, self.screen1_url)

		user = User.objects.get(email='ui-register-test@example.com')
		self.assertEqual(str(self.client.session.get('_auth_user_id')), str(user.pk))

	def test_login_success_redirects_to_screen1(self):
		User.objects.create_user(
			email='ui-login-test@example.com',
			username='ui-login-test',
			password='StrongPass123!',
			user_type='organization',
		)
		response = self.client.post(
			self.login_url,
			data={'username': 'ui-login-test@example.com', 'password': 'StrongPass123!'},
		)
		self.assertRedirects(response, self.screen1_url)

"""Verifies if the expected CSS selectors for the new auth UI are present in the styles.css file (through Smoke Unit tests)."""
class AuthCssSmokeTests(TestCase):
	def test_auth_css_selectors_exist(self):
		css_path = Path('static/css/styles.css')
		css = css_path.read_text(encoding='utf-8')

		expected_selectors = [
			':root',
			'.auth-shell',
			'.auth-shell::before',
			'.auth-card',
			'.auth-subtitle',
			'.auth-badge',
			'.auth-links',
			'.auth-note',
		]
		for selector in expected_selectors:
			self.assertIn(selector, css)
