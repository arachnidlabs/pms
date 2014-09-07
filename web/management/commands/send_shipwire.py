import config
import logging
from django.core.management.base import BaseCommand

from web import admin, shipwire, models, countries


class Command(BaseCommand):
    help = "Upload orders to Shipwire."

    def handle(self, *args, **kwargs):
    	hold = config.shipwireconfig.get('shipwire', 'hold').lower() == 'true'
    	orders = {order.remote_order_id: order for order in
    	          models.Order.objects.filter(
    	          	backorder=False,
    	          	shipped=False,
    		        submitted=False,
    		        shipping_method__service_level__isnull=False)}
    	if not orders:
    		print "Nothing to send."
    		return
    	orderinfo = [self.make_order(order, hold) for order in orders.values()]
    	print "Sending %d orders" % (len(orderinfo,))
    	api = admin.get_shipwire_api()
    	total_packages, total_items, shipwire_ids = api.submit_orders(orderinfo)
    	print "Uploaded %d packages and %d items" % (total_packages, total_items)
    	for tindie_id, shipwire_id in shipwire_ids:
    		order = orders[tindie_id]
    		order.shipwire_id = shipwire_id
    		order.submitted = True
    		order.save()

    def make_order(self, order, hold):
    	address_parts = order.shipping_street.split('\n', 2)
    	address = shipwire.ShipwireAddress(
    		name=order.shipping_name,
    		address1=address_parts[0],
    		address2=address_parts[1] if len(address_parts) > 1 else None,
    		address3=address_parts[2] if len(address_parts) > 2 else None,
    		city=order.shipping_city,
    		state=order.shipping_state,
    		zip=order.shipping_postcode,
    		country=countries.countries[order.shipping_country.upper()],
    		phone=order.phone,
    		email=order.email)
    	items = [shipwire.ShipwireItem(li.product.sku, li.quantity)
    			 for li in order.lineitems.all()]
    	return shipwire.ShipwireOrder(
    		id=order.remote_order_id,
    		hold=hold,
    		address=address,
    		shipping=order.shipping_method.service_level,
    		items=items)
