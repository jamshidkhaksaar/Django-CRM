from django.test import TestCase, Client
from django.urls import reverse
from django.core.cache import cache
from website.models import Record, CustomUser

class DashboardTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = CustomUser.objects.create_user(
            username='testuser',
            password='testpass123',
            user_type='cashier'
        )
        self.client.login(username='testuser', password='testpass123')
        
    def test_dashboard_view(self):
        response = self.client.get(reverse('dashboard'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'dashboard.html')
        
    def test_dashboard_cache(self):
        # Create some records
        Record.objects.create(
            requester=self.user,
            transaction_type='income',
            total_value='1000.00'
        )
        
        response = self.client.get(reverse('dashboard'))
        self.assertEqual(response.status_code, 200)
        
        # Check if cache is working
        cache_key = f'dashboard_stats_{self.user.id}'
        self.assertIsNotNone(cache.get(cache_key)) 