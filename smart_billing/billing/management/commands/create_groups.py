# billing/management/commands/create_groups.py
from django.core.management.base import BaseCommand
from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType
from billing.models import Invoice, Product, InvoiceItem

class Command(BaseCommand):
    help = 'Create default groups: Admin, Staff, Manager and assign permissions'

    def handle(self, *args, **options):
        # Admin group (mostly managed via superuser)
        admin_group, _ = Group.objects.get_or_create(name='Admin')

        # Staff: can add invoice, view product & invoice
        staff_group, _ = Group.objects.get_or_create(name='Staff')
        manager_group, _ = Group.objects.get_or_create(name='Manager')

        ct_invoice = ContentType.objects.get_for_model(Invoice)
        ct_product = ContentType.objects.get_for_model(Product)
        ct_item = ContentType.objects.get_for_model(InvoiceItem)

        # Staff permissions: add invoice, view invoice, view product
        perms = [
            Permission.objects.get(content_type=ct_invoice, codename='add_invoice'),
            Permission.objects.get(content_type=ct_invoice, codename='view_invoice'),
            Permission.objects.get(content_type=ct_product, codename='view_product'),
        ]
        for p in perms:
            staff_group.permissions.add(p)

        # Manager permissions: view/add/change products & invoices + view invoice items
        mgr_perms = [
            Permission.objects.get(content_type=ct_invoice, codename='view_invoice'),
            Permission.objects.get(content_type=ct_invoice, codename='change_invoice'),
            Permission.objects.get(content_type=ct_product, codename='view_product'),
            Permission.objects.get(content_type=ct_product, codename='change_product'),
            Permission.objects.get(content_type=ct_item, codename='view_invoiceitem'),
        ]
        for p in mgr_perms:
            manager_group.permissions.add(p)

        self.stdout.write(self.style.SUCCESS('Default groups created/updated.'))
