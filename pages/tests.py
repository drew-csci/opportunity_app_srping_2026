from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model

# Happy path Unit Test for loading a user's specific dashboard view based on their user type, also testing if Dashboard
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

# Simple edge case test that attempts to see if an anonymous user (not logged in) can access the dashboard, 
# which should not be allowed and should redirect to login page instead by default.
class DashboardEdgeCaseTests(TestCase):
    # Edge case: anonymous users should not access dashboard directly.
    def test_dashboard_redirects_anonymous_user_to_login(self):
        response = self.client.get(reverse("dashboard"))
        expected_login_url = f"{reverse('login')}?next={reverse('dashboard')}"
        self.assertRedirects(response, expected_login_url)

# An integration test that tests the whole flow of the pathing that the logging-in system partakes in, testing
# multiple methods that contribute towards it to ensure that everything works as intended (incorporating the
# first unit test from above as well as something else into one big test).
class AuthDashboardIntegrationTests(TestCase):
    """
    Integration test:
    login view + auth backend + redirect logic + dashboard view/template
    (Tests the entire flow of the pathing that we have been working on from the start, essentially).
    """

    # Mock user account is setup.
    def setUp(self):
        User = get_user_model()
        self.password = "TestPass123!"
        self.user = User.objects.create_user(
            email="org_integration@example.com",
            username="org_integration@example.com",
            password=self.password,
            user_type="organization",
            first_name="Org",
            last_name="Owner",
        )

    # Tests the login process, its redirect, and sees if the dashboard renders properly.
    def test_login_redirects_and_renders_org_dashboard(self):
        response = self.client.post(
            reverse("login"),
            {"username": self.user.email, "password": self.password},
            follow=True,
        )

        # Final destination should be dashboard
        self.assertEqual(response.request["PATH_INFO"], reverse("dashboard"))
        self.assertEqual(response.status_code, 200)

        # Confirms dashboard page rendered with expected personalized content
        self.assertTemplateUsed(response, "pages/dashboard.html")
        self.assertContains(response, "Organization Dashboard")
        self.assertContains(response, self.user.display_name)
