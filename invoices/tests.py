from decimal import Decimal

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from .models import Invoice


class InvoiceAutoNumberTests(TestCase):
    def test_invoice_number_is_generated_on_save(self):
        user = get_user_model().objects.create_user(username='tester', password='testpass123')

        invoice = Invoice.objects.create(owner=user, cust_name='Test Customer', amount='100.00')

        self.assertTrue(invoice.invoice_number)
        self.assertRegex(invoice.invoice_number, r'^INV-\d{6}$')


class InvoiceWorkflowTests(TestCase):
    def setUp(self):
        user_model = get_user_model()
        self.user = user_model.objects.create_user(
            username="owner", password="test-password"
        )
        self.other_user = user_model.objects.create_user(
            username="other", password="test-password"
        )
        self.invoice = Invoice.objects.create(
            owner=self.user,
            cust_name="Acme Customer",
            amount=Decimal("1250.00"),
            is_paid=True,
        )
        Invoice.objects.create(
            owner=self.user,
            cust_name="Pending Customer",
            amount=Decimal("400.00"),
            is_paid=False,
        )

    def test_invoice_detail_is_owner_scoped(self):
        self.client.login(username="owner", password="test-password")
        response = self.client.get(reverse("show_invoice", args=[self.invoice.id]))
        self.assertContains(response, self.invoice.invoice_number)

        self.client.login(username="other", password="test-password")
        self.assertEqual(
            self.client.get(reverse("show_invoice", args=[self.invoice.id])).status_code,
            404,
        )

    def test_invoice_list_combines_search_and_status(self):
        self.client.login(username="owner", password="test-password")
        response = self.client.get(
            reverse("invoice"), {"q": "Acme", "status": "paid"}
        )
        self.assertContains(response, self.invoice.invoice_number)
        self.assertEqual(list(response.context["page_obj"].object_list), [self.invoice])

    def test_invoice_list_paginates_real_records(self):
        for index in range(11):
            Invoice.objects.create(
                owner=self.user,
                cust_name=f"Customer {index}",
                amount=Decimal("10.00"),
            )
        self.client.login(username="owner", password="test-password")
        response = self.client.get(reverse("invoice"), {"q": "Customer", "status": "all"})
        self.assertContains(response, "Next")
        self.assertContains(response, "page=2")

    def test_authenticated_workspace_pages_render(self):
        self.client.login(username="owner", password="test-password")
        for route_name in (
            "invoice",
            "paid_invoices",
            "unpaid_invoices",
            "add_invoice",
            "profile",
            "settings",
            "help",
        ):
            with self.subTest(route_name=route_name):
                self.assertEqual(self.client.get(reverse(route_name)).status_code, 200)

    def test_delete_invoice_is_post_and_owner_scoped(self):
        other_invoice = Invoice.objects.create(
            owner=self.other_user,
            cust_name="Other Customer",
            amount=Decimal("25.00"),
        )
        self.client.login(username="owner", password="test-password")
        response = self.client.post(
            reverse("delete_invoice"), {"invoice_id": self.invoice.id}
        )
        self.assertRedirects(response, reverse("invoice"))
        self.assertFalse(Invoice.objects.filter(id=self.invoice.id).exists())

        self.client.post(reverse("delete_invoice"), {"invoice_id": other_invoice.id})
        self.assertTrue(Invoice.objects.filter(id=other_invoice.id).exists())
