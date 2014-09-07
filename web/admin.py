import shlex
import subprocess
from decimal import Decimal
from django.contrib import admin
from django.shortcuts import redirect
from web.models import ShippingMethod, Order, Product, LineItem, Package, Posting, TindieProduct, TindieProductMap
from web import labelgen

import config
import tindie
import royalmail
import shipwire


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


def get_shipwire_api():
    username = config.shipwireconfig.get('auth', 'username')
    password = config.shipwireconfig.get('auth', 'password')
    host = config.shipwireconfig.get('shipwire', 'host')
    return shipwire.ShipwireAPI(host, username, password)


admin.site.register(Posting)


class ShippingMethodAdmin(admin.ModelAdmin):
    list_display = ('region', 'service_level', 'name')
admin.site.register(ShippingMethod, ShippingMethodAdmin)


class ProductAdmin(admin.ModelAdmin):
    list_display = ('sku', 'name')
admin.site.register(Product, ProductAdmin)


class TindieProductMapInline(admin.TabularInline):
    list_display = ('tindie_product', 'product', 'quantity')
    model = TindieProductMap
    extra = 1


class TindieProductAdmin(admin.ModelAdmin):
    inlines = (TindieProductMapInline,)
    list_display = ('model_number', 'name')
admin.site.register(TindieProduct, TindieProductAdmin)


class LineItemInline(admin.TabularInline):
    model = LineItem
    extra = 1


class OrderAdmin(admin.ModelAdmin):
    inlines = (LineItemInline,)
    list_display = ('remote_order_id', 'shipping_name', 'summary', 
        'total_seller', 'shipped', 'submitted', 'backorder')
    list_filter = ('shipped', 'submitted', 'backorder')
    actions = ('create_packages', 'mark_shipped')
    search_fields = ('remote_order_id',)
    fieldsets = (
        (None, {
            'fields': ('remote_order_id', 'date', 'message', 'payment', 'backorder'),
        }),
        ('Shipping', {
            'fields': ('shipped', 'email', 'phone', 'shipping_name', 
                'shipping_street', 'shipping_city', 'shipping_state', 
                'shipping_postcode', 'shipping_country', 'shipping_method', 
                'shipping_instructions', 'tracking_code', 'tracking_url',
                'submitted', 'shipwire_id'),
        }),
        ('Payment', {
            'fields': ('refunded', 'total', 'total_discount', 'total_kickback', 
                'total_shipping', 'total_tindiefee', 'total_subtotal', 
                'total_seller'),
        })
    )

    def create_packages(self, request, queryset):
        for order in queryset:
            self.create_order_packages(order)
        return redirect('admin:web_package_changelist')
    create_packages.short_description = "Create packages"

    def create_order_packages(self, order):
        package = Package(
            order=order, 
            shipping_method=order.shipping_method, 
            shipping_weight=0, 
            customs_value=Decimal(0))
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
    list_display = ('id', 'order', 'shipping_name', 'shipping_method', 
        'contents', 'shipping_weight', 'customs_value', 'packed', 'sent')
    list_filter = ('packed', 'sent')
    actions = ('mark_packed', 'print_labels', 'print_noppi_labels', 
        'generate_posting')

    def mark_packed(self, request, queryset):
        queryset.update(packed=True)
    mark_packed.short_description = "Mark as packed"

    def print_noppi_labels(self, request, queryset):
        return self.print_labels(request, queryset, ppi=False)

    def print_labels(self, request, queryset, ppi=True):
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
                ppi_path if ppi else None,
                ppi_size if ppi else None,
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
        posting = Posting(shipping_method=queryset[0].shipping_method)
        posting.save()

        queryset.update(posting=posting)

        rm = get_rm_api()
        rm.upload_posting(queryset, posting.id)

    generate_posting.short_description = "Upload posting to Royal Mail"
admin.site.register(Package, PackageAdmin)
