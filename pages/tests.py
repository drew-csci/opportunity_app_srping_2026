from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from django.urls import reverse


class OrganizationScreen1Tests(TestCase):

    def setUp(self):
        """
        Set up a test client and create a user for screen1 testing.
        Update the user role field if the custom user model requires it.
        """
        self.client = Client()
        User = get_user_model()

        self.user = User.objects.create_user(
            username="orguser",
            password="testpass123"
        )

    def test_screen1_loads_for_authenticated_user(self):
        """
        Unit Test:
        Verify that an authenticated user can access screen1 successfully.
        Expected result: HTTP 200 status code.
        """
        self.client.force_login(self.user)
        response = self.client.get(reverse("screen1"))
        self.assertEqual(response.status_code, 200)

    def test_screen1_contains_expected_content(self):
        """
        Unit Test:
        Verify that screen1 renders expected content for the current implementation.
        Expected result: Response contains the current screen heading and text.
        """
        self.client.force_login(self.user)
        response = self.client.get(reverse("screen1"))

        self.assertContains(response, "Screen 1 Student")
        self.assertContains(response, "This is a placeholder page.")

    def test_screen1_post_request_returns_success(self):
        """
        Integration Test:
        Verify that a POST request to screen1 returns a successful response
        for an authenticated user.
        """
        self.client.force_login(self.user)
        response = self.client.post(reverse("screen1"), {
            "index": 0,
            "action": "accept"
        })

        self.assertEqual(response.status_code, 200)