code = '''

class US008ReminderTests(TestCase):
    def setUp(self):
        from django.contrib.auth import get_user_model
        User = get_user_model()
        self.student = User.objects.create_user(
            username='student_us008',
            email='student_us008@drew.edu',
            password='TestPass123!',
            user_type='student'
        )
        self.organization = User.objects.create_user(
            username='org_us008',
            email='org_us008@drew.edu',
            password='TestPass123!',
            user_type='organization'
        )
        from pages.models import Opportunity, Application
        self.opportunity = Opportunity.objects.create(
            title='Test Opportunity US008',
            organization=self.organization,
            description='Test',
            location='Test',
            duration='1 week'
        )
        self.application = Application.objects.create(
            student=self.student,
            opportunity=self.opportunity,
            status='pending',
            message='Test message'
        )

    def test_remind_button_visible_when_pending(self):
        self.client.login(email='student_us008@drew.edu', password='TestPass123!')
        from django.urls import reverse
        response = self.client.get(reverse('my_applications'), follow=True)
        self.assertIn(b'Remind About Me', response.content)

    def test_remind_button_hidden_when_accepted(self):
        self.application.status = 'accepted'
        self.application.save()
        self.client.login(email='student_us008@drew.edu', password='TestPass123!')
        from django.urls import reverse
        response = self.client.get(reverse('my_applications'), follow=True)
        self.assertNotIn(b'Remind About Me', response.content)

    def test_remind_button_hidden_when_declined(self):
        self.application.status = 'declined'
        self.application.save()
        self.client.login(email='student_us008@drew.edu', password='TestPass123!')
        from django.urls import reverse
        response = self.client.get(reverse('my_applications'), follow=True)
        self.assertNotIn(b'Remind About Me', response.content)

    def test_remind_organization_success(self):
        self.client.login(email='student_us008@drew.edu', password='TestPass123!')
        from django.urls import reverse
        response = self.client.post(
            reverse('remind_organization', args=[self.application.id]),
            follow=True
        )
        self.assertEqual(response.status_code, 200)

    def test_remind_requires_login(self):
        from django.urls import reverse
        response = self.client.post(
            reverse('remind_organization', args=[self.application.id])
        )
        self.assertEqual(response.status_code, 302)
        self.assertIn('login', response.url)

    def test_remind_requires_post(self):
        self.client.login(email='student_us008@drew.edu', password='TestPass123!')
        from django.urls import reverse
        response = self.client.get(
            reverse('remind_organization', args=[self.application.id])
        )
        self.assertEqual(response.status_code, 405)
'''

with open('pages/tests.py', 'a', encoding='utf-8') as f:
    f.write(code)
print('Done')