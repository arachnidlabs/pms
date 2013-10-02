import shlex
import subprocess
from decimal import Decimal
from django.contrib import admin
from django.shortcuts import redirect
from web.models import ShippingMethod, Order, Product, LineItem, Package, Posting
from web import labelgen

import config
import tindie
import royalmail


def get_tindie_api():
    username = config.tindieconfig.get('auth', 'username')
    password = config.tindieconfig.get('auth', 'password')
    auth_token = config.tindieconfig.get('auth', 'auth_token')
    return tindie.TindieAPI(username, password=password, auth_token=auth_token)


def get_rm_api():
    return royalmail.RoyalMailAPI(
        account_number=config.rmconfig.get('account', 'number'),
        service_register=config.rmconfig.get('account', 'service_register'),
        posting_location=config.rmconfig.get('account', 'posting_location'),
        email=config.rmconfig.get('account', 'email'),
        auto_confirm='Y' if config.rmconfig.get('settings', 'auto_confirm').lower() in ('y', 'yes', 'true') else 'N',
        password=config.rmconfig.get('account', 'password'))


admin.site.register(ShippingMethod)
admin.site.register(Product)
admin.site.register(Posting)


class LineItemInline(admin.TabularInline):
    model = LineItem
    extra = 1


class OrderAdmin(admin.ModelAdmin):
    inlines = (LineItemInline,)
    list_display = ('remote_order_id', 'shipping_name', 'summary', 'total_seller', 'packed', 'shipped')
    list_filter = ('shipped',)
    actions = ('create_packages', 'mark_shipped')
    search_fields = ('remote_order_id',)

    def create_packages(self, request, queryset):
        for order in queryset:
            self.create_order_packages(order)
        return redirect('admin:web_package_changelist')
    create_packages.short_description = "Create packages"

    def create_order_packages(self, order):
        package = Package(order=order, shipping_method=order.shipping_method, shipping_weight=0, customs_value=Decimal(0))
        package.save()
        for lineitem in order.lineitem_set.all():
            if not lineitem.package:
                package.shipping_weight += lineitem.total_weight
                package.customs_value += lineitem.total_value
                lineitem.package = package
                lineitem.save()
        package.save()

    def mark_shipped(self, request, queryset):
        tapi = get_tindie_api()
        for order in queryset:
            tapi.mark_shipped(order.remote_order_id)
            order.shipped = True
            order.save()
    mark_shipped.short_description = "Mark shipped on Tindie"
admin.site.register(Order, OrderAdmin)


class PackageAdmin(admin.ModelAdmin):
    inlines = (LineItemInline,)
    list_display = ('id', 'order', 'shipping_method', 'contents', 'shipping_weight', 'customs_value', 'packed', 'sent')
    list_filter = ('packed', 'sent')
    actions = ('mark_packed', 'print_labels', 'generate_posting')

    def mark_packed(self, request, queryset):
        queryset.update(packed=True)
    mark_packed.short_description = "Mark as packed"

    def print_labels(self, request, queryset):
        fromaddr = config.config.get('labels', 'return_address')
        ppi_path = config.config.get('labels', 'image')
        ppi_size = (int(config.config.get('labels', 'image_width')),
                    int(config.config.get('labels', 'image_height')))
        addr_print_cmd = config.config.get('labels', 'print_command')
        customs_path = config.config.get('customs', 'image')
        customs_print_cmd = config.config.get('customs', 'print_command')

        for package in queryset:
            address_label = labelgen.generate_label(
                fromaddr,
                ppi_path,
                ppi_size,
                package.sender_info,
                package.postal_address)
            self.run_command(addr_print_cmd, address_label)

            if package.zone not in ('GB', 'EUP'):
                customs_label = labelgen.generate_customs(
                    customs_path,
                    "%.1f KG" % (package.shipping_weight / 1000,),
                    "$%.2f" % (package.customs_value,))
                self.run_command(customs_print_cmd, customs_label)
    print_labels.short_description = "Print labels"

    def run_command(self, command, data):
        process = subprocess.Popen(shlex.split(command), stdin=subprocess.PIPE)
        process.stdin.write(data)
        process.stdin.close()
        process.wait()

    def generate_posting(self, request, queryset):
        rm = get_rm_api()
        rm.upload_posting(queryset)

        posting = Posting()
    generate_posting.short_description = "Upload posting to Royal Mail"


admin.site.register(Package, PackageAdmin)
