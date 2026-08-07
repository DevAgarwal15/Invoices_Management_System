from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Q, Sum
from django.core.paginator import Paginator
from django.shortcuts import get_object_or_404, redirect, render

from .models import Invoice
from .forms import InvoiceForm


def _invoice_page(request, queryset, template_name, page_title, status_filter):
    query = request.GET.get("q", "").strip()
    if query:
        queryset = queryset.filter(
            Q(invoice_number__icontains=query) | Q(cust_name__icontains=query)
        )

    selected_status = status_filter
    if status_filter == "all":
        selected_status = request.GET.get("status", "all")
    if selected_status == "paid":
        queryset = queryset.filter(is_paid=True)
    elif selected_status == "pending":
        queryset = queryset.filter(is_paid=False)

    paginator = Paginator(queryset.order_by("-date_created", "-id"), 10)
    page_obj = paginator.get_page(request.GET.get("page"))
    return render(
        request,
        template_name,
        {
            "all_invoices": page_obj,
            "page_obj": page_obj,
            "query": query,
            "status_filter": selected_status,
            "page_title": page_title,
        },
    )


@login_required
def dashboard(request):
    invoices = Invoice.objects.filter(owner=request.user)
    recent_invoices = invoices.order_by("-date_created")[:5]

    context = {
        "total_invoices": invoices.count(),
        "paid_invoices": invoices.filter(is_paid=True).count(),
        "pending_invoices": invoices.filter(is_paid=False).count(),
        "total_revenue": invoices.aggregate(total=Sum("amount"))["total"] or 0,
        "recent_invoices": recent_invoices,
    }

    return render(request, "dashboard.html", context)

def home(request):
    return render(request, 'home.html')


@login_required
def show_invoices(request):
    invoices = Invoice.objects.filter(owner=request.user)
    return _invoice_page(request, invoices, "invoice_list.html", "Invoices", "all")


@login_required
def create_invoice(request):
    return redirect("add_invoice")


@login_required
def show_one_invoice(request, invoice_id):
    invoice = get_object_or_404(Invoice, id=invoice_id, owner=request.user)
    return render(request, "invoice_detail.html", {"invoice": invoice})


@login_required
def show_unpaid_invoices(request):
    invoices = Invoice.objects.filter(owner=request.user, is_paid=False)
    return _invoice_page(
        request, invoices, "unpaid_invoices.html", "Pending invoices", "pending"
    )


@login_required
def show_paid_invoices(request):
    invoices = Invoice.objects.filter(owner=request.user, is_paid=True)
    return _invoice_page(
        request, invoices, "paid_invoices.html", "Paid invoices", "paid"
    )


@login_required
def delete_invoices(request):
    if request.method == "POST":
        invoice = get_object_or_404(
            Invoice, id=request.POST.get("invoice_id"), owner=request.user
        )
        invoice.delete()
        messages.success(request, "Invoice deleted.")
    return redirect('invoice')


@login_required
def add_invoice(request):
    if request.method == 'POST':
        form = InvoiceForm(request.POST)
        if form.is_valid():
            invoice = form.save(commit=False)
            invoice.owner = request.user
            invoice.save()
            messages.success(request, f"{invoice.invoice_number} was created.")
            return redirect('invoice')
    else:
        form = InvoiceForm()
    data = {
        'form': form
    }
    return render(request, 'add_invoice.html', data)


@login_required
def profile(request):
    return render(request, "profile.html")


@login_required
def settings_page(request):
    return render(request, "settings.html")


@login_required
def help_page(request):
    return render(request, "help.html")