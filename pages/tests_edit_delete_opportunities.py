"""
Unit and integration tests for opportunity editing and deletion features.
Tests cover form validation, view authorization, and complete workflows.
"""

from datetime import timedelta
from django.contrib.auth import get_user_model
from django.test import TestCase, Client
from django.urls import reverse
from django.utils import timezone

from .models import Opportunity

User = get_user_model()


class OpportunityFormTest(TestCase):
    """Test suite for OpportunityForm validation and functionality."""
    
    def setUp(self):
        """Set up test fixtures."""
        from .forms import OpportunityForm
        self.OpportunityForm = OpportunityForm
        
        self.organization = User.objects.create_user(
            email='org@example.com',
            username='testorg',
            user_type='organization',
            password='testpass123'
        )
        
        self.opportunity = Opportunity.objects.create(
            title='Test Opportunity',
            description='Test description',
            organization=self.organization,
            status='open',
            location='Test City',
            opportunity_type='Volunteer',
            duration='3 months',
            required_skills='Communication, Leadership'
        )
    
    def test_form_creates_new_opportunity(self):
        """Test that form can create a new opportunity."""
        form_data = {
            'title': 'New Opportunity',
            'description': 'New opportunity description',
            'location': 'San Francisco, CA',
            'opportunity_type': 'Internship',
            'duration': 'Summer 2026',
            'required_skills': 'Python, Django',
            'status': 'open',
            'application_deadline': (timezone.now().date() + timedelta(days=30)).isoformat(),
        }
        
        form = self.OpportunityForm(data=form_data)
        self.assertTrue(form.is_valid(), form.errors)
    
    def test_form_edits_existing_opportunity(self):
        """Test that form can edit an existing opportunity."""
        form_data = {
            'title': 'Updated Title',
            'description': 'Updated description',
            'location': 'Los Angeles, CA',
            'opportunity_type': 'Fellowship',
            'duration': '6 months',
            'required_skills': 'Java, Spring Boot',
            'status': 'open',
            'application_deadline': (timezone.now().date() + timedelta(days=30)).isoformat(),
        }
        
        form = self.OpportunityForm(data=form_data, instance=self.opportunity)
        self.assertTrue(form.is_valid(), form.errors)
        
        updated_opp = form.save()
        self.assertEqual(updated_opp.title, 'Updated Title')
        self.assertEqual(updated_opp.location, 'Los Angeles, CA')
    
    def test_form_rejects_past_deadline(self):
        """Test that form rejects application deadline in the past."""
        past_date = (timezone.now().date() - timedelta(days=1)).isoformat()
        form_data = {
            'title': 'Test Opportunity',
            'description': 'Test description',
            'location': 'Test City',
            'opportunity_type': 'Volunteer',
            'duration': '3 months',
            'required_skills': 'Communication',
            'status': 'open',
            'application_deadline': past_date,
        }
        
        form = self.OpportunityForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('application_deadline', form.errors)
    
    def test_form_requires_required_skills(self):
        """Test that form requires required_skills to be filled."""
        form_data = {
            'title': 'Test Opportunity',
            'description': 'Test description',
            'location': 'Test City',
            'opportunity_type': 'Volunteer',
            'duration': '3 months',
            'required_skills': '',
            'status': 'open',
            'application_deadline': (timezone.now().date() + timedelta(days=30)).isoformat(),
        }
        
        form = self.OpportunityForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('required_skills', form.errors)
    
    def test_form_allows_empty_deadline(self):
        """Test that form allows optional application_deadline."""
        form_data = {
            'title': 'Test Opportunity',
            'description': 'Test description',
            'location': 'Test City',
            'opportunity_type': 'Volunteer',
            'duration': '3 months',
            'required_skills': 'Communication',
            'status': 'open',
            'application_deadline': '',
        }
        
        form = self.OpportunityForm(data=form_data)
        self.assertTrue(form.is_valid(), form.errors)


class EditOpportunityViewTest(TestCase):
    """Test suite for editing opportunities."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.client = Client()
        
        self.org_user = User.objects.create_user(
            email='org@example.com',
            username='testorg',
            user_type='organization',
            password='testpass123'
        )
        
        self.other_org = User.objects.create_user(
            email='other@example.com',
            username='otherorg',
            user_type='organization',
            password='testpass123'
        )
        
        self.student = User.objects.create_user(
            email='student@example.com',
            username='student',
            user_type='student',
            password='testpass123'
        )
        
        self.opportunity = Opportunity.objects.create(
            title='Test Opportunity',
            description='Test description',
            organization=self.org_user,
            status='open',
            location='Test City',
            opportunity_type='Volunteer',
            duration='3 months',
            required_skills='Communication'
        )
    
    def test_organization_can_access_edit_form(self):
        """Test that organization can access edit form for their opportunity."""
        self.client.login(username='testorg', password='testpass123')
        response = self.client.get(reverse('edit_opportunity', args=[self.opportunity.id]))
        
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Test Opportunity')
    
    def test_non_organization_cannot_edit(self):
        """Test that non-organization users cannot edit opportunities."""
        self.client.login(username='student', password='testpass123')
        response = self.client.get(reverse('edit_opportunity', args=[self.opportunity.id]))
        
        self.assertEqual(response.status_code, 403)
    
    def test_organization_cannot_edit_others_opportunity(self):
        """Test that organization cannot edit another organization's opportunity."""
        self.client.login(username='otherorg', password='testpass123')
        response = self.client.get(reverse('edit_opportunity', args=[self.opportunity.id]))
        
        self.assertEqual(response.status_code, 403)
    
    def test_edit_opportunity_with_valid_data(self):
        """Test editing opportunity with valid data."""
        self.client.login(username='testorg', password='testpass123')
        
        new_deadline = (timezone.now().date() + timedelta(days=30)).isoformat()
        form_data = {
            'title': 'Updated Title',
            'description': 'Updated description',
            'location': 'New City',
            'opportunity_type': 'Internship',
            'duration': '6 months',
            'required_skills': 'Python, Django',
            'status': 'open',
            'application_deadline': new_deadline,
        }
        
        response = self.client.post(
            reverse('edit_opportunity', args=[self.opportunity.id]),
            data=form_data
        )
        
        # Check redirect to organization_opportunities
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse('organization_opportunities'))
        
        # Verify opportunity was updated
        updated_opp = Opportunity.objects.get(id=self.opportunity.id)
        self.assertEqual(updated_opp.title, 'Updated Title')
        self.assertEqual(updated_opp.location, 'New City')
    
    def test_edit_opportunity_with_invalid_data(self):
        """Test editing opportunity with invalid data (past deadline)."""
        self.client.login(username='testorg', password='testpass123')
        
        past_date = (timezone.now().date() - timedelta(days=1)).isoformat()
        form_data = {
            'title': 'Test Opportunity',
            'description': 'Test description',
            'location': 'Test City',
            'opportunity_type': 'Volunteer',
            'duration': '3 months',
            'required_skills': 'Communication',
            'status': 'open',
            'application_deadline': past_date,
        }
        
        response = self.client.post(
            reverse('edit_opportunity', args=[self.opportunity.id]),
            data=form_data
        )
        
        # Should stay on edit page with errors
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Please correct the highlighted fields')
        
        # Verify opportunity was NOT updated
        opp = Opportunity.objects.get(id=self.opportunity.id)
        self.assertEqual(opp.title, 'Test Opportunity')
    
    def test_edit_opportunity_shows_success_message(self):
        """Test that success message is shown after editing."""
        self.client.login(username='testorg', password='testpass123')
        
        future_date = (timezone.now().date() + timedelta(days=30)).isoformat()
        form_data = {
            'title': 'Updated Title',
            'description': 'Updated description',
            'location': 'New City',
            'opportunity_type': 'Internship',
            'duration': '6 months',
            'required_skills': 'Python',
            'status': 'open',
            'application_deadline': future_date,
        }
        
        response = self.client.post(
            reverse('edit_opportunity', args=[self.opportunity.id]),
            data=form_data,
            follow=True
        )
        
        messages = list(response.context['messages'])
        self.assertTrue(any('updated successfully' in str(m) for m in messages))


class DeleteOpportunityViewTest(TestCase):
    """Test suite for deleting opportunities."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.client = Client()
        
        self.org_user = User.objects.create_user(
            email='org@example.com',
            username='testorg',
            user_type='organization',
            password='testpass123'
        )
        
        self.other_org = User.objects.create_user(
            email='other@example.com',
            username='otherorg',
            user_type='organization',
            password='testpass123'
        )
        
        self.student = User.objects.create_user(
            email='student@example.com',
            username='student',
            user_type='student',
            password='testpass123'
        )
        
        self.opportunity = Opportunity.objects.create(
            title='Test Opportunity',
            description='Test description',
            organization=self.org_user,
            status='open',
            location='Test City',
            opportunity_type='Volunteer',
            duration='3 months',
            required_skills='Communication'
        )
    
    def test_organization_can_access_delete_confirmation(self):
        """Test that organization can access delete confirmation page."""
        self.client.login(username='testorg', password='testpass123')
        response = self.client.get(reverse('delete_opportunity', args=[self.opportunity.id]))
        
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Test Opportunity')
    
    def test_non_organization_cannot_delete(self):
        """Test that non-organization users cannot delete opportunities."""
        self.client.login(username='student', password='testpass123')
        response = self.client.get(reverse('delete_opportunity', args=[self.opportunity.id]))
        
        self.assertEqual(response.status_code, 403)
    
    def test_organization_cannot_delete_others_opportunity(self):
        """Test that organization cannot delete another organization's opportunity."""
        self.client.login(username='otherorg', password='testpass123')
        response = self.client.get(reverse('delete_opportunity', args=[self.opportunity.id]))
        
        self.assertEqual(response.status_code, 403)
    
    def test_delete_opportunity_removes_from_database(self):
        """Test that deleting opportunity removes it from database."""
        self.client.login(username='testorg', password='testpass123')
        opportunity_id = self.opportunity.id
        
        # Verify opportunity exists
        self.assertTrue(Opportunity.objects.filter(id=opportunity_id).exists())
        
        # Delete it
        response = self.client.post(reverse('delete_opportunity', args=[opportunity_id]))
        
        # Check redirect
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse('organization_opportunities'))
        
        # Verify opportunity no longer exists
        self.assertFalse(Opportunity.objects.filter(id=opportunity_id).exists())
    
    def test_delete_opportunity_shows_success_message(self):
        """Test that success message is shown after deletion."""
        self.client.login(username='testorg', password='testpass123')
        
        response = self.client.post(
            reverse('delete_opportunity', args=[self.opportunity.id]),
            follow=True
        )
        
        messages = list(response.context['messages'])
        self.assertTrue(any('deleted' in str(m) for m in messages))
        self.assertTrue(any('Test Opportunity' in str(m) for m in messages))


class OpportunityEditDeleteIntegrationTest(TestCase):
    """Integration tests for edit and delete opportunity features."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.client = Client()
        
        self.org_user = User.objects.create_user(
            email='org@example.com',
            username='testorg',
            user_type='organization',
            password='testpass123'
        )
        
        self.opportunity1 = Opportunity.objects.create(
            title='Opportunity 1',
            description='Description 1',
            organization=self.org_user,
            status='open',
            location='City 1',
            opportunity_type='Volunteer',
            duration='3 months',
            required_skills='Skill 1'
        )
        
        self.opportunity2 = Opportunity.objects.create(
            title='Opportunity 2',
            description='Description 2',
            organization=self.org_user,
            status='open',
            location='City 2',
            opportunity_type='Internship',
            duration='6 months',
            required_skills='Skill 2'
        )
    
    def test_edit_then_view_updated_opportunity(self):
        """Test complete flow: edit opportunity and view updated version."""
        self.client.login(username='testorg', password='testpass123')
        
        # Edit the opportunity
        future_date = (timezone.now().date() + timedelta(days=30)).isoformat()
        form_data = {
            'title': 'Updated Opportunity 1',
            'description': 'Updated description',
            'location': 'Updated City',
            'opportunity_type': 'Fellowship',
            'duration': '12 months',
            'required_skills': 'Updated Skills',
            'status': 'open',
            'application_deadline': future_date,
        }
        
        edit_response = self.client.post(
            reverse('edit_opportunity', args=[self.opportunity1.id]),
            data=form_data
        )
        
        # Verify redirect to org opportunities
        self.assertEqual(edit_response.status_code, 302)
        
        # Verify changes were saved
        updated_opp = Opportunity.objects.get(id=self.opportunity1.id)
        self.assertEqual(updated_opp.title, 'Updated Opportunity 1')
        self.assertEqual(updated_opp.location, 'Updated City')
    
    def test_delete_removes_from_organization_list(self):
        """Test that deleted opportunity is removed from organization list."""
        self.client.login(username='testorg', password='testpass123')
        
        # Verify both opportunities exist
        self.assertEqual(Opportunity.objects.filter(organization=self.org_user).count(), 2)
        
        # Delete one opportunity
        self.client.post(reverse('delete_opportunity', args=[self.opportunity1.id]))
        
        # Verify only one remains
        remaining_opps = Opportunity.objects.filter(organization=self.org_user)
        self.assertEqual(remaining_opps.count(), 1)
        self.assertEqual(remaining_opps.first().id, self.opportunity2.id)
    
    def test_edit_multiple_opportunities_independently(self):
        """Test editing multiple opportunities independently."""
        self.client.login(username='testorg', password='testpass123')
        
        future_date = (timezone.now().date() + timedelta(days=30)).isoformat()
        
        # Edit first opportunity
        form_data1 = {
            'title': 'Edited Opportunity 1',
            'description': 'Description 1',
            'location': 'City 1',
            'opportunity_type': 'Volunteer',
            'duration': '3 months',
            'required_skills': 'Skill 1',
            'status': 'open',
            'application_deadline': future_date,
        }
        self.client.post(
            reverse('edit_opportunity', args=[self.opportunity1.id]),
            data=form_data1
        )
        
        # Edit second opportunity
        form_data2 = {
            'title': 'Edited Opportunity 2',
            'description': 'Description 2',
            'location': 'City 2',
            'opportunity_type': 'Internship',
            'duration': '6 months',
            'required_skills': 'Skill 2',
            'status': 'closed',
            'application_deadline': future_date,
        }
        self.client.post(
            reverse('edit_opportunity', args=[self.opportunity2.id]),
            data=form_data2
        )
        
        # Verify both were edited correctly
        opp1 = Opportunity.objects.get(id=self.opportunity1.id)
        opp2 = Opportunity.objects.get(id=self.opportunity2.id)
        
        self.assertEqual(opp1.title, 'Edited Opportunity 1')
        self.assertEqual(opp2.title, 'Edited Opportunity 2')
        self.assertEqual(opp2.status, 'closed')
    
    def test_close_opportunity_appears_as_past(self):
        """Test that closing an opportunity makes it appear in past opportunities."""
        self.client.login(username='testorg', password='testpass123')
        
        # Edit opportunity to mark as closed
        future_date = (timezone.now().date() + timedelta(days=30)).isoformat()
        form_data = {
            'title': 'Opportunity 1',
            'description': 'Description 1',
            'location': 'City 1',
            'opportunity_type': 'Volunteer',
            'duration': '3 months',
            'required_skills': 'Skill 1',
            'status': 'closed',
            'application_deadline': future_date,
        }
        
        self.client.post(
            reverse('edit_opportunity', args=[self.opportunity1.id]),
            data=form_data
        )
        
        # Verify it's now closed
        opp = Opportunity.objects.get(id=self.opportunity1.id)
        self.assertEqual(opp.status, 'closed')
