import logging
from datetime import datetime, timedelta
from django.core.management.base import BaseCommand
from django.utils import timezone

from web.models import Order, ShippingMethod, LineItem, Product, TindieProduct, TindieProductMap
from web import admin, countries


def import_orders():
    api = admin.get_tindie_api()
    orders = api.get_orders(delay=1.0)

    num_orders = 0
    num_new = 0
    for item in orders:
        print "Processing order %d" % (item['number'])
        num_orders += 1
        defaults = dict((k, item[k]) for k in (
            'date', 'email', 'message', 'phone', 'shipping_city', 'shipping_country',
            'shipping_instructions', 'shipping_name', 'shipping_postcode', 'shipping_state',
            'shipping_street', 'total', 'total_discount', 'total_kickback', 'total_seller',
            'total_shipping', 'total_subtotal', 'total_tindiefee', 'payment', 'refunded',
            'tracking_code', 'tracking_url'))
        defaults['date'] = datetime.strptime(defaults['date'].split(".")[0], "%Y-%m-%dT%H:%M:%S").replace(tzinfo=timezone.utc)
        country_code = countries.countries[item['shipping_country'].upper()]
        try:
            defaults['shipping_method'] = ShippingMethod.find(item['shipping_service'], country_code)
        except ShippingMethod.DoesNotExist:
            defaults['shipping_method'] = ShippingMethod(name=item['shipping_service'], region=country_code)
            defaults['shipping_method'].save()

        defaults['shipped'] = item['shipped'] or item['refunded']
        defaults['backorder'] = any(li['status'] == 'pending' for li in item['items'])
        order, created = Order.objects.get_or_create(remote_order_id=item['number'], defaults=defaults)
        if not created:
            for k, v in defaults.iteritems():
                setattr(order, k, v)
            order.save()
        else:
            num_new += 1

            # Normalise lineitems for fulfillment
            items = {}
            for li in item['items']:
                try:
                    tindie_product = TindieProduct.objects.get(
                        tindie_id=int(li['sku']),
                        model_number=li['model_number'])
                except TindieProduct.DoesNotExist:
                    print "Creating new product for model number %s" % (li['model_number'],)

                    product = Product(
                        sku=li['model_number'],
                        name=li['product'],
                    )
                    product.save()

                    tindie_product = TindieProduct(
                        tindie_id=int(li['sku']),
                        model_number=li['model_number'],
                        name=li['product'])
                    tindie_product.save()

                    product_map = TindieProductMap(
                        tindie_product=tindie_product,
                        product=product,
                        quantity=1)
                    product_map.save()

                for mapitem in tindie_product.skus.all():
                    product = mapitem.product
                    if product.sku not in items:
                        items[product.sku] = dict(li)
                        items[product.sku]['quantity'] = 0
                        items[product.sku]['product'] = product
                    items[product.sku]['quantity'] += mapitem.quantity * int(li['quantity'])

            for sku, li in items.iteritems():
                defaults = dict((k, li[k]) for k in (
                    'options', 'pre_order', 'price_total', 'price_unit', 'quantity', 'status'))
                lineitem = LineItem(order=order, product=li['product'], **defaults)
                lineitem.save()
        if datetime.utcnow().replace(tzinfo=timezone.utc) - order.date > timedelta(days=90):
            break
    logging.info("Imported %d orders (%d new)", num_orders, num_new)


class Command(BaseCommand):
    help = "Import order data from Tindie"

    def handle(self, *args, **options):
        import_orders()
