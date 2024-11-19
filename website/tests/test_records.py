from django.test import TestCase, Client
from django.urls import reverse
from website.models import Record, CustomUser
from decimal import Decimal

class RecordTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = CustomUser.objects.create_user(
            username='testuser',
            password='testpass123',
            user_type='cashier'
        )
        self.client.login(username='testuser', password='testpass123')
        
    def test_add_record(self):
        response = self.client.post(reverse('add_record'), {
            'transaction_type': 'income',
            'item_name': 'Test Item',
            'quantity': '10',
            'unit_price': '100.00',
            'total_value': '1000.00',
            'cashier_status': 'Pending'
        })
        self.assertEqual(response.status_code, 302)
        self.assertEqual(Record.objects.count(), 1)
        
    def test_edit_record(self):
        record = Record.objects.create(
            requester=self.user,
            transaction_type='income',
            item_name='Test Item',
            quantity=Decimal('10.00'),
            unit_price=Decimal('100.00'),
            total_value=Decimal('1000.00')
        )
        response = self.client.post(
            reverse('edit_record', kwargs={'pk': record.pk}),
            {'item_name': 'Updated Item'}
        )
        self.assertEqual(response.status_code, 302)
        record.refresh_from_db()
        self.assertEqual(record.item_name, 'Updated Item') 