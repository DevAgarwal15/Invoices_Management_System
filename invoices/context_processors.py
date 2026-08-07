from .models import Invoice


def billing_notifications(request):
    if not request.user.is_authenticated:
        return {}

    pending_invoices = Invoice.objects.filter(
        owner=request.user,
        is_paid=False,
    ).order_by("-date_created", "-id")

    return {
        "pending_notification_count": pending_invoices.count(),
        "pending_notifications": pending_invoices[:5],
    }
