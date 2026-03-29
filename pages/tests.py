from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from django.urls import reverse


class OrganizationScreen1Tests(TestCase):

    def setUp(self):
        self.client = Client()
        User = get_user_model()
        self.user = User.objects.create_user(
            username="orguser",
            password="testpass123"
        )
        self.user.user_type = "organization"
        self.user.save()

    def test_screen1_loads_for_authenticated_user(self):
        """Unit Test: authenticated user can access screen1."""
        self.client.force_login(self.user)
        response = self.client.get(reverse("screen1"))
        self.assertEqual(response.status_code, 200)

    def test_screen1_contains_organization_dashboard_content(self):
        """Unit Test: screen1 renders organization dashboard content."""
        self.client.force_login(self.user)
        response = self.client.get(reverse("screen1"))
        self.assertContains(response, "Organization Dashboard")
        self.assertContains(response, "Incoming Applications")

    def test_screen1_post_request_returns_success(self):
        """Integration Test: POST request to screen1 returns 200."""
        self.client.force_login(self.user)
        response = self.client.post(reverse("screen1"), {
            "index": "0",
            "action": "accept"
        })
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Organization Dashboard")