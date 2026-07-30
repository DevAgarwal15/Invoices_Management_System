from django.db import models
from django.conf import settings


class Invoice(models.Model):
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="invoices"
    )

    cust_name = models.CharField(max_length=200)
    invoice_number = models.CharField(
        max_length=50,
        unique=True,
        blank=True,
        null=True,
    )
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    date_created = models.DateField(auto_now_add=True)
    is_paid = models.BooleanField(default=False)

    def __str__(self):
        return self.invoice_number or "New Invoice"

    def save(self, *args, **kwargs):
        if not self.invoice_number:
            last_invoice = (
                Invoice.objects.exclude(invoice_number__isnull=True)
                .exclude(invoice_number="")
                .filter(invoice_number__startswith="INV-")
                .order_by("-id")
                .first()
            )

            if last_invoice and last_invoice.invoice_number:
                try:
                    last_number = int(last_invoice.invoice_number.split("-")[1])
                except (IndexError, ValueError):
                    last_number = 0
            else:
                last_number = 0

            self.invoice_number = f"INV-{last_number + 1:06d}"

        super().save(*args, **kwargs)