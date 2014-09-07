import config
import logging
from django.core.management.base import BaseCommand
from web.models import ShippingMethod, TindieProduct
from web import admin, shipwire


sample_addresses = [
    ("US", shipwire.ShipwireAddress(
        address1="45 Park Avenue",
        city="New York",
        state="NY",
        country="US",
        zip="10016")),
    ("GB", shipwire.ShipwireAddress(
        address1="14 Tottenham Court Road",
        city="London",
        state="London",
        country="UK",
        zip="W1T 1JY")),
    ("EU", shipwire.ShipwireAddress(
        address1="Schulstrasse 4",
        city="Bad Oyenhausen",
        country="DE",
        zip="32547")),
    ("CA", shipwire.ShipwireAddress(
        address1="1010 Easy St",
        city="Ottawa",
        state="Ontario",
        country="CA",
        zip="K1A 0B1")),
    ("Everywhere Else", shipwire.ShipwireAddress(
        address1="173 Park Road",
        address2="Johnsonville",
        city="Wellington",
        country="NZ",
        zip="6004")),
]


shipwire_carrier_id = 48


shipwire_service_names = {
    '1D': 'Premium',
    '2D': 'Priority',
    'GD': 'Ground',
    'FT': 'Freight',
    'E-INTL': 'Economy International',
    'INTL': 'International',
    'PL-INTL': 'Priority International',
    'PM-INTL': 'Premium International',
}


first_pick_cost = float(config.shipwireconfig.get('shipwire', 'firstpick'))
extra_pick_cost = float(config.shipwireconfig.get('shipwire', 'extrapick'))


class Command(BaseCommand):
    help = "Generate Tindie shipping rates from Shipwire quotes"

    def get_rates(self, product_id, pick_list, region, address):
        rates = []

        pick_list_1 = [shipwire.ShipwireItem(sku, qty) for sku, qty in pick_list]
        min_rates = self.shipwire.get_quotes(address, pick_list_1)
        pick_list_5 = [shipwire.ShipwireItem(sku, qty * 5) for sku, qty in pick_list]
        max_rates = self.shipwire.get_quotes(address, pick_list_5)

        methods = set(min_rates.keys()) & set(max_rates.keys())
        for method in methods:
            min_rate = min_rates[method]
            max_rate = max_rates[method]

            if min_rate['mindays'] != min_rate['maxdays']:
                name = "%s (%s - %s days)" % (shipwire_service_names[method], min_rate['mindays'], min_rate['maxdays'])
            else:
                name = "%s (%s days)" % (shipwire_service_names[method], min_rate['mindays'])
            method, created = ShippingMethod.objects.get_or_create(
                region=region,
                service_level=method,
                defaults={
                    'name': "Shipwire " + name,
                })

            base_cost = round((min_rate['cost'] + first_pick_cost) * 1.1, 2)
            incremental_cost = round(((max_rate['cost'] - min_rate['cost']) / 4 + extra_pick_cost) * 1.1, 2)
            print "    %s: $%.2f + $%.2f" % (method.name, base_cost, incremental_cost)
            rates.append((region, shipwire_carrier_id, method.name, base_cost, incremental_cost, [product_id]))

        return rates

    def handle(self, *args, **kwargs):
        self.tindie = admin.get_tindie_api()
        self.shipwire = admin.get_shipwire_api()
        
        q = TindieProduct.objects.filter(shipwire_rates=True)
        if args:
            q = q.filter(model_number__in=args)

        for product in q:
            print "Processing product %s (%s)" % (product.name, product.model_number)
            pick_list = [(mapping.product.sku, mapping.quantity) for mapping in product.skus.all()]
            print "  Pick list: " + ', '.join("%s x %s" % pick for pick in pick_list)
            for region, address in sample_addresses:
                print "  Processing region %s" % (region,)
                for rate in self.get_rates(product.tindie_id, pick_list, region, address):
                    try:
                        self.tindie.add_shipping_rate(*rate)
                    except Exception, e:
                        logging.exception("Problem uploading rate %r", rate)
                        continue
        print "Done."
