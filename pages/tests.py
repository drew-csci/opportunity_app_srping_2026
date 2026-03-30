from django.test import TestCase
from django.urls import reverse
from django.utils import timezone
from django.contrib.auth import get_user_model

from .models import Opportunity, Application

User = get_user_model()

class ApplicationTrackingTests(TestCase):
    def setUp(self):
        self.student = User.objects.create_user(
            email='student@example.com',
            password='testpass',
            username='studentuser',
            user_type='student',
            first_name='Student',
            last_name='One',
        )
        self.organization = User.objects.create_user(
            email='org@example.com',
            password='testpass',
            username='orguser',
            user_type='organization',
            first_name='Org',
            last_name='One',
        )

        self.opportunity = Opportunity.objects.create(
            organization=self.organization,
            title='Volunteer Tutor',
            description='Help K-12 students',
            cause='Education',
            location='Remote',
            duration='3 months',
            skills_required='Teaching',
            opportunity_type='Volunteer',
            is_active=True,
        )

    def test_application_auto_responded_date_on_accept_and_deny(self):
        app = Application.objects.create(
            student=self.student,
            opportunity=self.opportunity,
            status=Application.Status.PENDING,
            message='I would love to help',
        )

        self.assertIsNone(app.responded_date)

        app.status = Application.Status.ACCEPTED
        app.save()
        self.assertEqual(app.status, Application.Status.ACCEPTED)
        self.assertIsNotNone(app.responded_date)

        # Now for denied path
        app2 = Application.objects.create(
            student=self.student,
            opportunity=self.opportunity,
            status=Application.Status.PENDING,
            message='Another app',
        )
        app2.status = Application.Status.DENIED
        app2.save()
        self.assertEqual(app2.status, Application.Status.DENIED)
        self.assertIsNotNone(app2.responded_date)

    def test_apply_to_opportunity_submits_pending_and_save_draft(self):
        self.client.force_login(self.student)

        # submit as pending
        url = reverse('apply_to_opportunity', args=[self.opportunity.id])
        response = self.client.post(url, {'message': 'I am interested', 'action': 'submit'})

        application = Application.objects.get(student=self.student, opportunity=self.opportunity)
        self.assertRedirects(response, reverse('application_detail', args=[application.id]))
        self.assertEqual(application.status, Application.Status.PENDING)

        # create a new opportunity for draft test
        opp2 = Opportunity.objects.create(
            organization=self.organization,
            title='Community Clean-up',
            description='park clean-up',
            cause='Environment',
            location='Local',
            duration='1 day',
            skills_required='Physical',
            opportunity_type='Volunteer',
            is_active=True,
        )
        url2 = reverse('apply_to_opportunity', args=[opp2.id])
        response = self.client.post(url2, {'message': 'Draft message', 'action': 'save_draft'})
        draft_application = Application.objects.get(student=self.student, opportunity=opp2)
        self.assertEqual(draft_application.status, Application.Status.DRAFT)
        self.assertRedirects(response, reverse('application_detail', args=[draft_application.id]))

    def test_prevent_duplicate_apply_for_non_draft(self):
        existing = Application.objects.create(
            student=self.student,
            opportunity=self.opportunity,
            status=Application.Status.PENDING,
            message='Already applied',
        )
        self.client.force_login(self.student)
        url = reverse('apply_to_opportunity', args=[self.opportunity.id])
        response = self.client.get(url)
        self.assertRedirects(response, reverse('application_detail', args=[existing.id]))

        messages = list(response.wsgi_request._messages)
        self.assertTrue(any('already applied' in m.message.lower() for m in messages))

    def test_my_applications_student_only(self):
        Application.objects.create(student=self.student, opportunity=self.opportunity, status=Application.Status.PENDING, message='One')
        Application.objects.create(student=self.student, opportunity=self.opportunity, status=Application.Status.PENDING, message='Two')

        self.client.force_login(self.student)
        response = self.client.get(reverse('my_applications'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context['applications']), 2)

        self.client.force_login(self.organization)
        response = self.client.get(reverse('my_applications'))
        self.assertRedirects(response, reverse('screen1'))

    def test_organization_applications_filters_and_permission(self):
        Application.objects.create(student=self.student, opportunity=self.opportunity, status=Application.Status.DRAFT, message='Draft')
        Application.objects.create(student=self.student, opportunity=self.opportunity, status=Application.Status.PENDING, message='Pending')
        Application.objects.create(student=self.student, opportunity=self.opportunity, status=Application.Status.ACCEPTED, message='Accepted')

        self.client.force_login(self.organization)
        response = self.client.get(reverse('organization_applications'))
        self.assertEqual(response.status_code, 200)
        apps = response.context['applications']
        self.assertEqual(len(apps), 2)
        self.assertNotIn(Application.Status.DRAFT, [a.status for a in apps])

        self.client.force_login(self.student)
        response = self.client.get(reverse('organization_applications'))
        self.assertRedirects(response, reverse('screen1'))

    def test_review_application_status_change(self):
        app = Application.objects.create(student=self.student, opportunity=self.opportunity, status=Application.Status.PENDING, message='Review this')

        self.client.force_login(self.organization)
        response = self.client.post(reverse('review_application', args=[app.id]), {'decision': Application.Status.ACCEPTED})
        self.assertRedirects(response, reverse('organization_applications'))

        app.refresh_from_db()
        self.assertEqual(app.status, Application.Status.ACCEPTED)
        self.assertIsNotNone(app.responded_date)

        response_invalid = self.client.post(reverse('review_application', args=[app.id]), {'decision': 'notavalid'})
        self.assertEqual(response_invalid.status_code, 200)
        self.assertContains(response_invalid, 'Please choose a valid decision.')

    def test_opportunity_detail_shows_application_and_permission(self):
        app = Application.objects.create(student=self.student, opportunity=self.opportunity, status=Application.Status.PENDING, message='Detail test')

        self.client.force_login(self.student)
        response = self.client.get(reverse('opportunity_detail', args=[self.opportunity.id]))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['opportunity'], self.opportunity)
        self.assertEqual(response.context['application'], app)

        self.client.force_login(self.organization)
        response = self.client.get(reverse('opportunity_detail', args=[self.opportunity.id]))
        self.assertRedirects(response, reverse('screen1'))

    def test_draft_resubmit_lifecycle(self):
        self.client.force_login(self.student)

        # save draft
        response = self.client.post(
            reverse('apply_to_opportunity', args=[self.opportunity.id]),
            {'message': 'Draft entry', 'action': 'save_draft'},
            follow=True
        )
        app = Application.objects.get(student=self.student, opportunity=self.opportunity)
        self.assertEqual(app.status, Application.Status.DRAFT)
        self.assertContains(response, 'Application draft saved')

        # verify my applications shows draft entry
        response = self.client.get(reverse('my_applications'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context['applications']), 1)
        self.assertEqual(response.context['applications'][0].status, Application.Status.DRAFT)

        # resubmit from same opportunity
        response = self.client.post(
            reverse('apply_to_opportunity', args=[self.opportunity.id]),
            {'message': 'Final submission', 'action': 'submit'},
            follow=True
        )
        app.refresh_from_db()
        self.assertEqual(app.status, Application.Status.PENDING)
        self.assertEqual(app.message, 'Final submission')
        self.assertContains(response, 'Application submitted')
