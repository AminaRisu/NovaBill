from .models import Product, Invoice
import uuid
from django.utils import timezone


# ---------------------------------------------------------
# Calculate Line Item (Price + Discount + GST)
# ---------------------------------------------------------
def calculate_line_item(product: Product, qty=1):
    base = product.price * qty
    discount_amt = base * (product.discount / 100.0)
    after_discount = base - discount_amt
    tax_amt = after_discount * (product.gst / 100.0)
    total = after_discount + tax_amt

    return {
        'base': round(base, 2),
        'discount_amt': round(discount_amt, 2),
        'after_discount': round(after_discount, 2),
        'tax_amt': round(tax_amt, 2),
        'total': round(total, 2)
    }


# ---------------------------------------------------------
# Generate Invoice Number
# Format: INVYYYYMMDDXXXX (example: INV202502010001)
# ---------------------------------------------------------
def generate_invoice_number():
    today = timezone.now().date()
    prefix = 'INV' + today.strftime('%Y%m%d')

    # Find the last invoice created today
    last = Invoice.objects.filter(invoice_number__startswith=prefix).order_by('-id').first()

    if not last:
        seq = 1
    else:
        # Get last 4 digits safely
        try:
            seq = int(last.invoice_number[-4:]) + 1
        except:
            seq = last.id + 1

    return f"{prefix}{seq:04d}"
