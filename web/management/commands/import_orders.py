import logging
from django.core.management.base import BaseCommand

from web.models import Order, ShippingMethod, LineItem, Product
from web import admin


def import_orders():
    api = admin.get_tindie_api()
    orders = api.get_orders()

    num_orders = 0
    num_new = 0
    for item in orders:
        num_orders += 1
        defaults = dict((k, item[k]) for k in (
            'date', 'email', 'message', 'phone', 'shipping_city', 'shipping_country',
            'shipping_instructions', 'shipping_name', 'shipping_postcode', 'shipping_state',
            'shipping_street', 'total', 'total_discount', 'total_kickback', 'total_seller',
            'total_shipping', 'total_subtotal', 'total_tindiefee', 'payment', 'refunded',
            'tracking_code', 'tracking_url'))
        defaults['shipping_method'] = ShippingMethod.objects.get_or_create(name=item['shipping_service'])[0]
        defaults['shipped'] = item['shipped'] or item['refunded']
        order, created = Order.objects.get_or_create(remote_order_id=item['number'], defaults=defaults)
        if not created:
            for k, v in defaults.iteritems():
                setattr(order, k, v)
            order.save()
        else:
            num_new += 1
            for li in item['items']:
                product, created = Product.objects.get_or_create(name=li['product'])
                defaults = dict((k, li[k]) for k in (
                    'options', 'pre_order', 'price_total', 'price_unit', 'quantity', 'status'))
                lineitem = LineItem(order=order, product=product, **defaults)
                lineitem.save()
    logging.info("Imported %d orders (%d new)", num_orders, num_new)


class Command(BaseCommand):
    help = "Import order data from Tindie"

    def handle(self, *args, **options):
        import_orders()
