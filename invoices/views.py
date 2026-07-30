from django.shortcuts import render,redirect
from .models import Invoice
from .forms import InvoiceForm
from django.shortcuts import get_object_or_404
from django.contrib.auth.decorators import login_required

# Create your views here.

@login_required
def dashboard(request):
    return render(request, "dashboard.html")

def home(request):
    return render(request, 'home.html')

def show_invoices(request):
    # data = {
    #     'all_invoices': [
    #         {"Invoice_Number": 1, "Customer_Name": "Rahul", "Total_Amount": 1100},
    #         {"Invoice_Number": 2, "Customer_Name": "Yash", "Total_Amount": 22000},
    #         {"Invoice_Number": 3, "Customer_Name": "Dev", "Total_Amount": 1234},
    #     ]
    # }
    # return render(request, "invoice_list.html", data)
    if request.user.is_superuser:
        all_invoices = Invoice.objects.all()
    else:
        all_invoices = Invoice.objects.filter(owner=request.user)
    return render(request, "invoice_list.html", {"all_invoices": all_invoices})
# ORM
# to create invoice
def create_invoice(request):
    Invoice.objects.create(
        cust_name='Dev-Agarwal',
        invoice_number='INV-001',
        amount=15000,
        is_paid=False
    ) 
    return redirect('invoice')

# to display invoice
def show_one_invoice(request):
    if request.user.is_superuser:
        invoice = Invoice.objects.get(invoice_number='INV-010')
    else:
        invoice = get_object_or_404(
            Invoice,
            invoice_number='INV-010',
            owner=request.user
        )
    data={
        'invoice':invoice
    }
    return render(request,'invoice_detail.html',data)

# to display unpaid invoices
def show_unpaid_invoices(request):
    unpaid_invoices = Invoice.objects.filter(is_paid=False)
    data={
        'unpaid_invoices':unpaid_invoices
    }
    return render(request,'unpaid_invoices.html',data)

# to display paid invoices
def mark_as_paid(request):
    Invoice.objects.filter(invoice_number='INV-001').update(is_paid=False)
    paid_invoices=Invoice.objects.filter(is_paid=True)
    data={
        'paid_invoices':paid_invoices
    }
    return render(request,'paid_invoices.html',data)

# to delete invoices
def delete_invoices(request):
    Invoice.objects.filter(invoice_number='INV-001').delete()
    return redirect('invoice')

# forms and validation

def add_invoice(request):
    if request.method == 'POST':
        form = InvoiceForm(request.POST)
        if form.is_valid():
            invoice = form.save(commit=False)
            invoice.owner = request.user
            invoice.save()
            return redirect('invoice')
    else:
        form = InvoiceForm()
    data = {
        'form': form
    }
    return render(request, 'add_invoice.html', data)