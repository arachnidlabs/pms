import config
import logging
from django.core.management.base import BaseCommand

from web import admin, shipwire, models, countries


class Command(BaseCommand):
    help = "Fetch tracking data from Shipwire."

    def handle(self, *args, **kwargs):
        orders = list(models.Order.objects.filter(
                    shipped=False, shipwire_id__isnull=False))
        sw_api = admin.get_shipwire_api()
        tindie_api = admin.get_tindie_api()
        tracking = sw_api.get_tracking([order.shipwire_id for order in orders])
        for order, (shipped, tracking) in zip(orders, tracking):
            if not shipped:
                print "No change for %s" % (order,)
            else:
                print "%s shipped with tracking code %s" % (order, tracking)
                tindie_api.mark_shipped(order.remote_order_id, tracking)
                order.shipped = True
                order.tracking_code = tracking
                order.save()
