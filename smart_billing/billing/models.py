from django.db import models


# ---------------------------------------------------------
# Product Model
# ---------------------------------------------------------
class Product(models.Model):
    name = models.CharField(max_length=255)
    sku = models.CharField(max_length=100, blank=True, null=True)
    price = models.FloatField()
    gst = models.FloatField(default=0)  # percentage e.g. 18%
    discount = models.FloatField(default=0)  # percentage e.g. 5%
    stock = models.IntegerField(default=0)

    def __str__(self):
        return f"{self.name} - {self.price}"


# ---------------------------------------------------------
# Invoice Model (Updated)
# ---------------------------------------------------------
class Invoice(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    subtotal = models.FloatField()
    total_tax = models.FloatField()
    total_discount = models.FloatField()
    total = models.FloatField()

    # New fields added:
    invoice_number = models.CharField(max_length=30, unique=True, null=True, blank=True)
    customer_name = models.CharField(max_length=200, blank=True, null=True)
    pdf_file = models.FileField(upload_to='invoices/', blank=True, null=True)

    def __str__(self):
        return f"Invoice #{self.id} - {self.customer_name}"


# ---------------------------------------------------------
# Invoice Item Model
# ---------------------------------------------------------
class InvoiceItem(models.Model):
    invoice = models.ForeignKey(Invoice, related_name='items', on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.PROTECT)
    qty = models.IntegerField(default=1)
    price = models.FloatField()  # captured at sale time
    gst_amt = models.FloatField()
    discount_amt = models.FloatField()

    def __str__(self):
        return f"{self.product.name} x {self.qty}"
