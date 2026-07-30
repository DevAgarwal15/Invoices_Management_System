from django.contrib.auth import get_user_model
from django.test import TestCase

from .models import Invoice


class InvoiceAutoNumberTests(TestCase):
    def test_invoice_number_is_generated_on_save(self):
        user = get_user_model().objects.create_user(username='tester', password='testpass123')

        invoice = Invoice.objects.create(owner=user, cust_name='Test Customer', amount='100.00')

        self.assertTrue(invoice.invoice_number)
        self.assertRegex(invoice.invoice_number, r'^INV-\d{6}$')
