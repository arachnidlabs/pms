from decimal import Decimal
from django.db import models
from web.countries import countries, europe_country_codes, world_zone_2_country_codes


def country_to_region(country_code):
    if country_code in europe_country_codes:
        return 'EU'
    else:
        return 'Everywhere Else'


class ShippingMethod(models.Model):
    name = models.CharField(max_length=255)
    region = models.CharField(max_length=255, null=True, blank=True)
    service_level = models.CharField(max_length=8, null=True, blank=True)

    @classmethod
    def find(cls, name, region):
        try:
            return cls.objects.get(name=name, region=region)
        except cls.DoesNotExist:
            return cls.objects.get(name=name, region=country_to_region(region))

    def __unicode__(self):
        return self.name


class Order(models.Model):
    remote_order_id = models.CharField(max_length=255, null=True, blank=True)
    date = models.DateTimeField()
    email = models.CharField(max_length=255)
    message = models.TextField(null=True, blank=True)
    payment = models.CharField(max_length=255, blank=True, null=True)
    phone = models.CharField(max_length=255, blank=True, null=True)
    refunded = models.BooleanField(default=False)
    shipped = models.BooleanField(default=False)
    shipping_city = models.CharField(max_length=255)
    shipping_country = models.CharField(max_length=255)
    shipping_instructions = models.TextField(blank=True, null=True)
    shipping_name = models.CharField(max_length=255)
    shipping_postcode = models.CharField(max_length=255)
    shipping_method = models.ForeignKey('ShippingMethod')
    shipping_state = models.CharField(max_length=255, blank=True)
    shipping_street = models.TextField()
    total = models.DecimalField(max_digits=8, decimal_places=2)
    total_discount = models.DecimalField(max_digits=8, decimal_places=2)
    total_kickback = models.DecimalField(max_digits=8, decimal_places=2)
    total_seller = models.DecimalField(max_digits=8, decimal_places=2)
    total_shipping = models.DecimalField(max_digits=8, decimal_places=2)
    total_subtotal = models.DecimalField(max_digits=8, decimal_places=2)
    total_tindiefee = models.DecimalField(max_digits=8, decimal_places=2)
    tracking_code = models.CharField(max_length=255, null=True, blank=True)
    tracking_url = models.CharField(max_length=255, null=True, blank=True)
    shipwire_id = models.CharField(max_length=255, null=True, blank=True)
    submitted = models.BooleanField(default=False)
    backorder = models.BooleanField(default=False)

    def __unicode__(self):
        return "Order #%s" % (self.remote_order_id,)

    @property
    def summary(self):
        return ", ".join(lineitem.summary for lineitem in self.lineitems.all())

    @property
    def packed(self):
        total = 0
        total_packed = 0
        for lineitem in self.lineitems.all():
            total += 1
            if lineitem.package and lineitem.package.packed:
                total_packed += 1
        return "%d/%d" % (total_packed, total)

    @property
    def country_code(self):
        return countries.get(self.shipping_country.upper(), None)

    @property
    def zone(self):
        if self.country_code == 'GB':
            return 'GB'
        elif self.country_code in europe_country_codes:
            return 'EUF'
        elif self.country_code in world_zone_2_country_codes:
            return 'RWE'
        else:
            return 'RWJ'

    @property
    def sender_info(self):
        return "%s %s" % (self.remote_order_id, self.zone)

    @property
    def postal_address(self):
        lines = []
        for line in [
            self.shipping_name,
            self.shipping_street,
            self.shipping_city,
            "%s %s" % (self.shipping_state, self.shipping_postcode),
            self.shipping_country if not self.zone == "GB" else ""]:
            lines.extend(x.strip() for x in line.split('\n') if x.strip())
        return lines


class Product(models.Model):
    sku = models.CharField(max_length=255)
    name = models.CharField(max_length=255)
    shipping_weight = models.IntegerField(null=True, blank=True)
    customs_value = models.DecimalField(max_digits=8, decimal_places=2, null=True, blank=True)

    def __unicode__(self):
        return self.sku


class TindieProduct(models.Model):
    """Maps Tindie products to actual SKUs."""
    tindie_id = models.IntegerField()
    model_number = models.CharField(max_length=255)
    name = models.CharField(max_length=255)
    shipwire_rates = models.BooleanField(default=False)
    shipwire_warehouse = models.CharField(max_length=255, null=True, blank=True)


class TindieProductMap(models.Model):
    """Maps Tindie products to SKUs."""
    tindie_product = models.ForeignKey(TindieProduct, related_name='skus')
    product = models.ForeignKey(Product, related_name='tindie_products')
    quantity = models.IntegerField()


class LineItem(models.Model):
    order = models.ForeignKey('Order', related_name='lineitems')
    package = models.ForeignKey('Package', null=True, blank=True, on_delete=models.SET_NULL, related_name='lineitems')
    product = models.ForeignKey('Product')
    options = models.TextField(blank=True, null=True)
    pre_order = models.BooleanField(default=False)
    price_total = models.DecimalField(max_digits=8, decimal_places=2)
    price_unit = models.DecimalField(max_digits=8, decimal_places=2)
    quantity = models.IntegerField()
    status = models.CharField(max_length=255)

    @property
    def summary(self):
        if self.options:
            return "%d x %s %s" % (self.quantity, self.product.name, self.options)
        else:
            return "%d x %s" % (self.quantity, self.product.name)

    @property
    def total_weight(self):
        return (self.product.shipping_weight or 0) * self.quantity

    @property
    def total_value(self):
        return (self.product.customs_value or Decimal(0)) * self.quantity


class Package(models.Model):
    order = models.ForeignKey('Order')
    posting = models.ForeignKey('Posting', null=True, blank=True, on_delete=models.SET_NULL)
    shipping_method = models.ForeignKey('ShippingMethod')
    shipping_weight = models.IntegerField()
    customs_value = models.DecimalField(max_digits=8, decimal_places=2)
    packed = models.BooleanField(default=False)
    sent = models.BooleanField(default=False)

    @property
    def contents(self):
        return ", ".join(lineitem.summary for lineitem in self.lineitems.all())

    @property
    def sender_info(self):
        return self.order.sender_info

    @property
    def postal_address(self):
        return self.order.postal_address

    @property
    def zone(self):
        return self.order.zone

    @property
    def shipping_name(self):
        return self.order.shipping_name


class Posting(models.Model):
    shipping_method = models.ForeignKey('ShippingMethod')
    provider_id = models.CharField(max_length=255, null=True, blank=True)

