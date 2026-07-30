from django.contrib import admin
from .models import Invoice


class InvoiceAdmin(admin.ModelAdmin):
    exclude = ["invoice_number"]

    list_display = [
        "owner",
        "cust_name",
        "invoice_number",
        "amount",
        "date_created",
        "is_paid",
    ]

    search_fields = [
        "cust_name",
        "invoice_number",
    ]

    list_filter = [
        "is_paid",
        "date_created",
    ]

    ordering = [
        "-date_created",
    ]


admin.site.register(Invoice, InvoiceAdmin)