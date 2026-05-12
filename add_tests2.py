code = '''

# ============================================================
# 1. Code Coverage Analysis Tests
# ============================================================
class US008CodeCoverageTests(TestCase):
    def setUp(self):
        from django.contrib.auth import get_user_model
        User = get_user_model()
        self.student = User.objects.create_user(
            username='coverage_student', email='coverage_student@drew.edu',
            password='TestPass123!', user_type='student')
        self.organization = User.objects.create_user(
            username='coverage_org', email='coverage_org@drew.edu',
            password='TestPass123!', user_type='organization')
        from pages.models import Opportunity, Application
        self.opportunity = Opportunity.objects.create(
            title='Coverage Test Opportunity', organization=self.organization,
            description='Test', location='Test', duration='1 week')
        self.application = Application.objects.create(
            student=self.student, opportunity=self.opportunity,
            status='pending', message='Test')

    def test_coverage_remind_view_pending_path(self):
        """Coverage: Tests the pending/applied path in remind_organization"""
        self.client.login(email='coverage_student@drew.edu', password='TestPass123!')
        from django.urls import reverse
        response = self.client.post(reverse('remind_organization', args=[self.application.id]), follow=True)
        self.assertEqual(response.status_code, 200)

    def test_coverage_remind_view_accepted_path(self):
        """Coverage: Tests the accepted/declined path in remind_organization"""
        self.application.status = 'accepted'
        self.application.save()
        self.client.login(email='coverage_student@drew.edu', password='TestPass123!')
        from django.urls import reverse
        response = self.client.post(reverse('remind_organization', args=[self.application.id]), follow=True)
        self.assertEqual(response.status_code, 200)

    def test_coverage_remind_view_unauthorized_path(self):
        """Coverage: Tests the unauthorized path in remind_organization"""
        self.client.login(email='coverage_org@drew.edu', password='TestPass123!')
        from django.urls import reverse
        response = self.client.post(reverse('remind_organization', args=[self.application.id]), follow=True)
        self.assertNotEqual(response.status_code, 404)

    def test_coverage_my_applications_view(self):
        """Coverage: Tests my_applications view renders correctly"""
        self.client.login(email='coverage_student@drew.edu', password='TestPass123!')
        from django.urls import reverse
        response = self.client.get(reverse('my_applications'), follow=True)
        self.assertEqual(response.status_code, 200)


# ============================================================
# 2. Negative Testing & Input Validation Tests
# ============================================================
class US008NegativeTests(TestCase):
    def setUp(self):
        from django.contrib.auth import get_user_model
        User = get_user_model()
        self.student = User.objects.create_user(
            username='negative_student', email='negative_student@drew.edu',
            password='TestPass123!', user_type='student')
        self.organization = User.objects.create_user(
            username='negative_org', email='negative_org@drew.edu',
            password='TestPass123!', user_type='organization')
        from pages.models import Opportunity, Application
        self.opportunity = Opportunity.objects.create(
            title='Negative Test Opportunity', organization=self.organization,
            description='Test', location='Test', duration='1 week')
        self.application = Application.objects.create(
            student=self.student, opportunity=self.opportunity,
            status='pending', message='Test')

    def test_negative_remind_without_login(self):
        """Negative: Cannot remind without being logged in"""
        from django.urls import reverse
        response = self.client.post(reverse('remind_organization', args=[self.application.id]))
        self.assertEqual(response.status_code, 302)
        self.assertIn('login', response.url)

    def test_negative_remind_invalid_id(self):
        """Negative: Cannot remind with non-existent application ID"""
        self.client.login(email='negative_student@drew.edu', password='TestPass123!')
        from django.urls import reverse
        response = self.client.post(reverse('remind_organization', args=[99999]), follow=True)
        self.assertEqual(response.status_code, 404)

    def test_negative_remind_get_method(self):
        """Negative: Remind endpoint does not accept GET requests"""
        self.client.login(email='negative_student@drew.edu', password='TestPass123!')
        from django.urls import reverse
        response = self.client.get(reverse('remind_organization', args=[self.application.id]))
        self.assertEqual(response.status_code, 405)

    def test_negative_remind_accepted_application(self):
        """Negative: Cannot remind for accepted application"""
        self.application.status = 'accepted'
        self.application.save()
        self.client.login(email='negative_student@drew.edu', password='TestPass123!')
        from django.urls import reverse
        response = self.client.post(reverse('remind_organization', args=[self.application.id]), follow=True)
        messages = list(response.context['messages'])
        self.assertFalse(any('Reminder sent' in str(m) for m in messages))

    def test_negative_remind_declined_application(self):
        """Negative: Cannot remind for declined application"""
        self.application.status = 'declined'
        self.application.save()
        self.client.login(email='negative_student@drew.edu', password='TestPass123!')
        from django.urls import reverse
        response = self.client.post(reverse('remind_organization', args=[self.application.id]), follow=True)
        messages = list(response.context['messages'])
        self.assertFalse(any('Reminder sent' in str(m) for m in messages))

    def test_negative_organization_cannot_remind(self):
        """Negative: Organization user cannot send reminder"""
        self.client.login(email='negative_org@drew.edu', password='TestPass123!')
        from django.urls import reverse
        response = self.client.post(reverse('remind_organization', args=[self.application.id]), follow=True)
        self.assertNotIn(b'Reminder sent', response.content)


# ============================================================
# 3. Regression Tests
# ============================================================
class US008RegressionTests(TestCase):
    def setUp(self):
        from django.contrib.auth import get_user_model
        User = get_user_model()
        self.student = User.objects.create_user(
            username='regression_student', email='regression_student@drew.edu',
            password='TestPass123!', user_type='student')
        self.organization = User.objects.create_user(
            username='regression_org', email='regression_org@drew.edu',
            password='TestPass123!', user_type='organization')
        from pages.models import Opportunity, Application
        self.opportunity = Opportunity.objects.create(
            title='Regression Test Opportunity', organization=self.organization,
            description='Test', location='Test', duration='1 week')
        self.application = Application.objects.create(
            student=self.student, opportunity=self.opportunity,
            status='pending', message='Test')

    def test_regression_remind_button_visible_pending(self):
        """Regression: Remind button always visible for pending status"""
        self.client.login(email='regression_student@drew.edu', password='TestPass123!')
        from django.urls import reverse
        response = self.client.get(reverse('my_applications'), follow=True)
        self.assertIn(b'Remind About Me', response.content)

    def test_regression_remind_button_hidden_after_accept(self):
        """Regression: Remind button hidden after application accepted"""
        self.application.status = 'accepted'
        self.application.save()
        self.client.login(email='regression_student@drew.edu', password='TestPass123!')
        from django.urls import reverse
        response = self.client.get(reverse('my_applications'), follow=True)
        self.assertNotIn(b'Remind About Me', response.content)

    def test_regression_status_not_changed_after_remind(self):
        """Regression: Application status stays pending after remind"""
        self.client.login(email='regression_student@drew.edu', password='TestPass123!')
        from django.urls import reverse
        self.client.post(reverse('remind_organization', args=[self.application.id]), follow=True)
        self.application.refresh_from_db()
        self.assertEqual(self.application.status, 'pending')

    def test_regression_remind_multiple_times(self):
        """Regression: Can send reminder multiple times for pending application"""
        self.client.login(email='regression_student@drew.edu', password='TestPass123!')
        from django.urls import reverse
        for _ in range(3):
            response = self.client.post(reverse('remind_organization', args=[self.application.id]), follow=True)
            self.assertEqual(response.status_code, 200)


# ============================================================
# 4. Performance & Load Tests
# ============================================================
class US008PerformanceTests(TestCase):
    def setUp(self):
        from django.contrib.auth import get_user_model
        User = get_user_model()
        self.student = User.objects.create_user(
            username='perf_student', email='perf_student@drew.edu',
            password='TestPass123!', user_type='student')
        self.organization = User.objects.create_user(
            username='perf_org', email='perf_org@drew.edu',
            password='TestPass123!', user_type='organization')
        from pages.models import Opportunity, Application
        self.opportunity = Opportunity.objects.create(
            title='Performance Test Opportunity', organization=self.organization,
            description='Test', location='Test', duration='1 week')
        self.applications = []
        for i in range(20):
            app = Application.objects.create(
                student=self.student, opportunity=self.opportunity,
                status='pending', message=f'Test message {i}')
            self.applications.append(app)

    def test_performance_my_applications_load_time(self):
        """Performance: My applications page loads within 3 seconds with 20 applications"""
        import time
        self.client.login(email='perf_student@drew.edu', password='TestPass123!')
        from django.urls import reverse
        start = time.time()
        response = self.client.get(reverse('my_applications'), follow=True)
        end = time.time()
        self.assertEqual(response.status_code, 200)
        self.assertLess(end - start, 3.0)

    def test_performance_remind_response_time(self):
        """Performance: Remind endpoint responds within 2 seconds"""
        import time
        self.client.login(email='perf_student@drew.edu', password='TestPass123!')
        from django.urls import reverse
        start = time.time()
        response = self.client.post(reverse('remind_organization', args=[self.applications[0].id]), follow=True)
        end = time.time()
        self.assertEqual(response.status_code, 200)
        self.assertLess(end - start, 2.0)


# ============================================================
# 5. Integration Tests
# ============================================================
class US008IntegrationTests(TestCase):
    def setUp(self):
        from django.contrib.auth import get_user_model
        User = get_user_model()
        self.student = User.objects.create_user(
            username='integration_student', email='integration_student@drew.edu',
            password='TestPass123!', user_type='student')
        self.organization = User.objects.create_user(
            username='integration_org', email='integration_org@drew.edu',
            password='TestPass123!', user_type='organization')
        from pages.models import Opportunity, Application
        self.opportunity = Opportunity.objects.create(
            title='Integration Test Opportunity', organization=self.organization,
            description='Test', location='Test', duration='1 week')
        self.application = Application.objects.create(
            student=self.student, opportunity=self.opportunity,
            status='pending', message='Test')

    def test_integration_full_remind_workflow(self):
        """Integration: Full remind workflow - view applications, send reminder, verify"""
        self.client.login(email='integration_student@drew.edu', password='TestPass123!')
        from django.urls import reverse
        response = self.client.get(reverse('my_applications'), follow=True)
        self.assertIn(b'Remind About Me', response.content)
        response = self.client.post(reverse('remind_organization', args=[self.application.id]), follow=True)
        self.assertEqual(response.status_code, 200)
        self.application.refresh_from_db()
        self.assertEqual(self.application.status, 'pending')

    def test_integration_apply_and_remind(self):
        """Integration: Student applies and can send reminder"""
        self.client.login(email='integration_student@drew.edu', password='TestPass123!')
        from django.urls import reverse
        response = self.client.get(reverse('my_applications'), follow=True)
        self.assertEqual(response.status_code, 200)
        response = self.client.post(reverse('remind_organization', args=[self.application.id]), follow=True)
        self.assertEqual(response.status_code, 200)

    def test_integration_remind_then_status_change(self):
        """Integration: After remind, org accepts, button disappears"""
        self.client.login(email='integration_student@drew.edu', password='TestPass123!')
        from django.urls import reverse
        self.client.post(reverse('remind_organization', args=[self.application.id]), follow=True)
        self.application.status = 'accepted'
        self.application.save()
        response = self.client.get(reverse('my_applications'), follow=True)
        self.assertNotIn(b'Remind About Me', response.content)


# ============================================================
# 6. Smoke Tests
# ============================================================
class US008SmokeTests(TestCase):
    def setUp(self):
        from django.contrib.auth import get_user_model
        User = get_user_model()
        self.student = User.objects.create_user(
            username='smoke_student', email='smoke_student@drew.edu',
            password='TestPass123!', user_type='student')
        self.organization = User.objects.create_user(
            username='smoke_org', email='smoke_org@drew.edu',
            password='TestPass123!', user_type='organization')
        from pages.models import Opportunity, Application
        self.opportunity = Opportunity.objects.create(
            title='Smoke Test Opportunity', organization=self.organization,
            description='Test', location='Test', duration='1 week')
        self.application = Application.objects.create(
            student=self.student, opportunity=self.opportunity,
            status='pending', message='Test')

    def test_smoke_my_applications_url_exists(self):
        """Smoke: my_applications URL is registered and accessible"""
        self.client.login(email='smoke_student@drew.edu', password='TestPass123!')
        from django.urls import reverse
        response = self.client.get(reverse('my_applications'), follow=True)
        self.assertEqual(response.status_code, 200)

    def test_smoke_remind_url_exists(self):
        """Smoke: remind_organization URL is registered"""
        from django.urls import reverse, NoReverseMatch
        try:
            url = reverse('remind_organization', args=[1])
            self.assertIsNotNone(url)
        except NoReverseMatch:
            self.fail('remind_organization URL not registered')

    def test_smoke_remind_endpoint_responds(self):
        """Smoke: remind endpoint responds without server error"""
        self.client.login(email='smoke_student@drew.edu', password='TestPass123!')
        from django.urls import reverse
        response = self.client.post(reverse('remind_organization', args=[self.application.id]), follow=True)
        self.assertNotEqual(response.status_code, 500)

    def test_smoke_my_applications_returns_html(self):
        """Smoke: my_applications returns HTML content"""
        self.client.login(email='smoke_student@drew.edu', password='TestPass123!')
        from django.urls import reverse
        response = self.client.get(reverse('my_applications'), follow=True)
        self.assertIn(b'html', response.content.lower())
'''

with open('pages/tests.py', 'a', encoding='utf-8') as f:
    f.write(code)
print('Done - added 6 test categories')