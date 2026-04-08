from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model

# Happy path test for loading a user's specific dashboard view based on their user type, also testing if Dashboard
# opens after login.
class DashboardHappyPathTests(TestCase):
    # Sets up mock user account, which in this case, is of the organization user type.
    def setUp(self):
        self.User = get_user_model()
        self.user = self.User.objects.create_user(
            email="org@example.com",
            username="org@example.com",
            password="TestPass123!",
            user_type="organization",
            first_name="Org",
            last_name="Owner",
        )

    # Tests the above credentials to see if, after implementing them, they lead to the correct dashboard page
    # meant for the given user type.
    def test_dashboard_renders_for_logged_in_user(self):
        self.client.login(username=self.user.email, password="TestPass123!")
        response = self.client.get(reverse("dashboard"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Organization Dashboard")
        self.assertContains(response, self.user.display_name)
