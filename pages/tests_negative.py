from django.test import TestCase, Client
from django.urls import reverse
from accounts.models import User
from pages.models import Opportunity
from pages.forms import VolunteerProfileForm


class NegativeTests(TestCase):
    def setUp(self):
        self.client = Client()
        
        # Test users
        self.student = User.objects.create_user(
            email='student_neg@test.com', username='student_neg', password='pass', user_type='student'
        )
        self.org = User.objects.create_user(
            email='org_neg@test.com', username='org_neg', password='pass', user_type='organization'
        )

    def test_apply_to_invalid_opportunity(self):
        """Negative Test: Try applying to an opportunity ID that doesn't exist out of range."""
        self.client.force_login(self.student)
        response = self.client.get(reverse('apply_to_opportunity', args=[9999999]))
        
        # Must return Graceful 404 block instead of system trace 500 error
        self.assertEqual(response.status_code, 404)

    def test_empty_application_form_submission(self):
        """Negative Test: Submitting an Application without message argument."""
        self.client.force_login(self.student)
        opp = Opportunity.objects.create(title='Testing', organization=self.org, is_active=True)
        
        response = self.client.post(
            reverse('apply_to_opportunity', args=[opp.id]), 
            {'message': '', 'action': 'submit'}
        )
        
        # Validation failure should reload form page with 200 OK and error message 
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'This field is required.')

    def test_profile_form_malformed_phone(self):
        """Negative Test: Supplying a wildly overlength string to boundary limit form inputs."""
        form = VolunteerProfileForm(data={
            'first_name': 'Bad',
            'last_name': 'Actor',
            'email': 'badactor@test.com',
            'phone': '1' * 50, # Database model max_length constraints typically bounds around 20
        })
        
        self.assertFalse(form.is_valid())
        self.assertIn('phone', form.errors)
        self.assertTrue(any('Ensure this value has at most' in e for e in form.errors['phone']))

    def test_screen1_missing_and_invalid_index(self):
        """Negative Test: Pushing malformed POST requests to screen array modification logic."""
        self.client.force_login(self.org)
        
        # Missing index completely (None->int() triggers TypeError)
        response = self.client.post(reverse('screen1'), {'action': 'accept'})
        self.assertEqual(response.status_code, 200) # Survives gracefully

        # Invalid index type (String->int() triggers ValueError)
        response_invalid = self.client.post(reverse('screen1'), {'index': 'word', 'action': 'accept'})
        self.assertEqual(response_invalid.status_code, 200)

        # Out of bounds index
        response_bounds = self.client.post(reverse('screen1'), {'index': '99', 'action': 'accept'})
        self.assertEqual(response_bounds.status_code, 200) 
