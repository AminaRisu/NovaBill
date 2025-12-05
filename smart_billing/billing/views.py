import json
from io import BytesIO
from datetime import timedelta
from django.urls import reverse

import qrcode
from xhtml2pdf import pisa

import random
import string

def generate_invoice_number(length=6):
    random_str = ''.join(random.choices(string.digits, k=length))
    return f"INV-{random_str}"

from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse, HttpResponse
from django.template.loader import render_to_string
from django.core.files.base import ContentFile
from django.utils import timezone
from django.urls import reverse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from django.db.models import Sum, F

from .models import Product, Invoice, InvoiceItem
from .ml_model import predict_item
from .utils import calculate_line_item
from .decorators import group_required


def login_view(request):
    return render(request, 'login.html')

# ---------------------------------------------------------
# Homepage (Public)
# ---------------------------------------------------------
def index(request):
    return render(request, 'billing/index.html')


# ---------------------------------------------------------
# Staff-only Billing View
# ---------------------------------------------------------
@login_required
@group_required(['Staff'])
def billing_view(request):
    """Main billing page UI (Staff-only)"""
    return render(request, "billing/billing.html")


# ---------------------------------------------------------
# Dashboard (Manager + Admin only)
# ---------------------------------------------------------
@login_required
@group_required(['Manager', 'Admin'])
def dashboard_view(request):
    """Dashboard UI"""
    return render(request, 'billing/dashboard.html')


# ---------------------------------------------------------
# API: Dashboard Data (Charts)
# ---------------------------------------------------------
@login_required
@group_required(['Manager', 'Admin'])
def api_dashboard_data(request):
    today = timezone.now().date()
    start_14 = today - timedelta(days=13)  # last 14 days

    invoices = Invoice.objects.filter(created_at__date__gte=start_14)

    # Prepare day buckets
    labels = []
    day_counts = []

    for i in range(14):
        day = start_14 + timedelta(days=i)
        day_total_qs = invoices.filter(created_at__date=day).aggregate(total=Sum('total'))
        total = day_total_qs['total'] or 0

        labels.append(day.strftime('%b %d'))
        day_counts.append(round(total, 2))

    # Top 5 products by quantity
    top_products = (
        InvoiceItem.objects
        .values(name=F('product__name'))
        .annotate(qty_sum=Sum('qty'))
        .order_by('-qty_sum')[:5]
    )

    top_labels = [x['name'] for x in top_products]
    top_values = [x['qty_sum'] for x in top_products]

    # GST (last 30 days)
    start_30 = today - timedelta(days=29)
    gst_total = Invoice.objects.filter(created_at__date__gte=start_30).aggregate(
        sum=Sum('total_tax')
    )['sum'] or 0

    return JsonResponse({
        'labels': labels,
        'sales': day_counts,
        'top_labels': top_labels,
        'top_values': top_values,
        'gst_total': round(gst_total, 2)
    })


# ---------------------------------------------------------
# API: Smart Search Item via ML (Autocomplete)
# ---------------------------------------------------------
def api_search(request):
    q = request.GET.get('q', '')
    results = []

    if q:
        results = predict_item(q, topk=8)

    return JsonResponse({'results': results})


# ---------------------------------------------------------
# API: Fetch Product
# ---------------------------------------------------------
@csrf_exempt
def api_get_product(request, pid):
    p = get_object_or_404(Product, id=pid)

    data = {
        'id': p.id,
        'name': p.name,
        'price': p.price,
        'gst': p.gst,
        'discount': p.discount,
        'stock': p.stock,
    }
    return JsonResponse(data)


# ---------------------------------------------------------
# API: Generate Invoice + PDF + QR
# ---------------------------------------------------------
@csrf_exempt
def api_generate_invoice(request):
    import base64
    import qrcode
    from io import BytesIO
    from django.urls import reverse

    payload = json.loads(request.body)
    items = payload.get('items', [])
    customer_name = payload.get('customer_name', "Guest")

    subtotal = 0
    total_tax = 0
    total_discount = 0

    # Create invoice
    invoice = Invoice(customer_name=customer_name)
    invoice.invoice_number = generate_invoice_number()
    invoice.save()

    # Create invoice items
    for it in items:
        prod = Product.objects.get(id=it['product_id'])
        qty = int(it.get('qty', 1))

        li = calculate_line_item(prod, qty)

        subtotal += li['after_discount']
        total_tax += li['tax_amt']
        total_discount += li['discount_amt']

        InvoiceItem.objects.create(
            invoice=invoice,
            product=prod,
            qty=qty,
            price=prod.price,
            gst_amt=li['tax_amt'],
            discount_amt=li['discount_amt']
        )

    # Update invoice totals
    invoice.subtotal = round(subtotal, 2)
    invoice.total_tax = round(total_tax, 2)
    invoice.total_discount = round(total_discount, 2)
    invoice.total = round(subtotal + total_tax, 2)
    invoice.save()

    # ---------------------------------------------------
    #       QR CODE GENERATION + BASE64 ENCODING
    # ---------------------------------------------------
    invoice_url = request.build_absolute_uri(
        reverse('billing:invoice_detail', args=[invoice.id])
    )

    qr = qrcode.make(invoice_url)
    qr_io = BytesIO()
    qr.save(qr_io, format='PNG')

    # convert QR PNG → base64 string
    qr_io.seek(0)
    qr_base64 = base64.b64encode(qr_io.getvalue()).decode('utf-8')

    # ---------------------------------------------------
    #       RENDER HTML WITH EMBEDDED BASE64 QR
    # ---------------------------------------------------
    html = render_to_string('billing/invoice.html', {
        'invoice': invoice,
        'items': InvoiceItem.objects.filter(invoice=invoice),
        'qr_base64': qr_base64
    })

    # ---------------------------------------------------
    #       GENERATE PDF & SAVE IT TO invoice.pdf_file
    # ---------------------------------------------------
    pdf_buffer = BytesIO()
    pisa_status = pisa.CreatePDF(html, dest=pdf_buffer)

    if pisa_status.err:
        return HttpResponse("Error creating PDF", status=500)

    pdf_buffer.seek(0)
    invoice.pdf_file.save(
        f"{invoice.invoice_number}.pdf",
        ContentFile(pdf_buffer.read())
    )
    invoice.save()

    # Return JSON for frontend
    return JsonResponse({
        'invoice_id': invoice.id,
        'invoice_number': invoice.invoice_number,
        'pdf_url': invoice.pdf_file.url,
        'qr_base64': qr_base64
    })


def invoice_detail(request, invoice_id):
    invoice = get_object_or_404(Invoice, id=invoice_id)
    return render(request, 'billing/invoice_detail.html', {'invoice': invoice})


def dashboard(request):
    return render(request, 'dashboard.html')
