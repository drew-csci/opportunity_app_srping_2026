import time
from django.test import TestCase, Client
from django.urls import reverse
from accounts.models import User
from pages.models import Opportunity, Application

class PerformanceTests(TestCase):
    """
    Performance and load volume tests using Django's test client.
    Seeds physical data blocks to simulate realistic database pressure
    and measures the benchmarked retrieval rates safely.
    """

    @classmethod
    def setUpTestData(cls):
        # Create heavy base dependencies once for all tests
        cls.student = User.objects.create_user(
            email='perf_student@test.com', username='perf_student', password='testpass', user_type='student'
        )
        cls.org = User.objects.create_user(
            email='perf_org@test.com', username='perf_org', password='testpass', user_type='organization'
        )
        
        # Simulate Database Stress: Bulk create 200 connected properties 
        opportunities = [
            Opportunity(title=f"Volunteering Gig {i}", organization=cls.org, is_active=True)
            for i in range(200)
        ]
        Opportunity.objects.bulk_create(opportunities)
        
        # Save a large volume of applications simulating heavy user history
        saved_opps = Opportunity.objects.all()
        applications = [
            Application(student=cls.student, opportunity=opp, status=Application.Status.PENDING)
            for opp in saved_opps[:150]
        ]
        Application.objects.bulk_create(applications)

    def setUp(self):
        self.client = Client()
        self.client.force_login(self.student)

    def test_opportunity_list_volume_load(self):
        """
        Benchmark measuring the latency to fetch and render 
        a massively bloated opportunity database query.
        """
        durations = []
        # Cycle repeated bulk renders to simulate localized traffic
        for _ in range(15):
            start_time = time.time()
            response = self.client.get(reverse('opportunity_list'))
            end_time = time.time()
            
            self.assertEqual(response.status_code, 200)
            durations.append(end_time - start_time)
            
        avg_duration = sum(durations) / len(durations)
        
        # Local development PCs vary, but rendering 200 entries 
        # sequentially shouldn't average more than 2 full seconds per hit.
        self.assertLess(avg_duration, 2.0)
        print(f"\n[BENCHMARK] Opportunity List (200 records): {avg_duration:.3f} seconds/avg")

    def test_my_applications_join_query_performance(self):
        """
        Tests the expensive Application pull which natively 
        performs an SQL JOIN across User and Opportunity tables.
        """
        start_time = time.time()
        response = self.client.get(reverse('my_applications'))
        duration = time.time() - start_time
        
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context['applications']), 150)
        
        # Even with SQL Joins on 150 instances, it should remain performant
        self.assertLess(duration, 2.0)
        print(f"\n[BENCHMARK] Application Joins (150 bounds): {duration:.3f} seconds")