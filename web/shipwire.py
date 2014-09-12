from bs4 import BeautifulSoup
import logging
from lxml import etree
from lxml.builder import E
import requests


class DictObject(object):
    fields = ()

    def __init__(self, *args, **kwargs):
        fields = list(self.fields)
        if len(args) > len(self.fields):
            raise ValueError("More arguments (%d) than fields (%d)"
                % (len(args), len(self.fields)))
        for field, value in zip(fields, args):
            setattr(self, field, value)
            fields.remove(field)

        for field, value in kwargs.iteritems():
            if field not in fields:
                raise ValueError("Unexpected keyword argument %s" % (field,))
            setattr(self, field, value)
            fields.remove(field)

        for field in fields:
            setattr(self, field, None)


class ShipwireAddress(DictObject):
    fields = ("name", "company", "address1", "address2", "address3", "city",
              "state", "country", "zip", "phone", "email")

    def to_elements(self):
        nodes = []
        if self.name:
            nodes.append(E.Name(E.Full(self.name)))
        if self.company:
            nodes.append(E.Company(self.company))
        nodes.append(E.Address1(self.address1))
        if self.address2:
            nodes.append(E.Address2(self.address2))
        if self.address3:
            nodes.append(E.Address2(self.address3))
        nodes.append(E.City(self.city))
        if self.state:
            nodes.append(E.State(self.state))
        nodes.append(E.Country(self.country))
        if self.zip:
            nodes.append(E.Zip(self.zip))
        if self.phone:
            nodes.append(E.Phone(self.phone))
        if self.email:
            nodes.append(E.Email(self.email))

        return E.AddressInfo(type="ship", *nodes)


class ShipwireOrder(DictObject):
    fields = ("id", "hold", "can_split", "do_not_ship_before", "warehouse",
              "address", "shipping", "items")

    def to_elements(self):
        nodes = []
        if self.hold:
            nodes.append(E.Hold())
        if self.can_split:
            nodes.append(E.CanSplit())
        if self.do_not_ship_before:
            nodes.append(E.DoNotShipBefore(self.do_not_ship_before))
        if self.warehouse:
            nodes.append(E.Warehouse(self.warehouse))
        nodes.append(self.address.to_elements())
        if self.shipping:
            nodes.append(E.Shipping(self.shipping))
        nodes.extend(item.to_elements(i) for i, item in enumerate(self.items))

        return E.Order(id=self.id, *nodes)


class ShipwireItem(object):
    def __init__(self, sku, quantity):
        self.sku = sku
        self.quantity = quantity

    def to_elements(self, idx):
        return E.Item(
            E.Code(self.sku),
            E.Quantity(str(self.quantity)),
            num=str(idx)
        )


class ShipwireAPI(object):
    def __init__(self, host, username, password):
        self.host = host
        self.username = username
        self.password = password

    def make_request(self, path, request, response_element):
        url = "https://%s/exec%s" % (self.host, path)
        response = requests.post(url, data=etree.tostring(request))
        response.raise_for_status()
        soup = BeautifulSoup(response.content, "xml")
        responsedata = getattr(soup, response_element)
        if responsedata.Status.text not in ("OK", "0"):
            raise ValueError("Got unexpected status back: %s (%s)"
                % (responsedata.ErrorMessage.text, responsedata.Status.text))
        return soup

    def get_quotes(self, address, items, warehouse=None):
        orderitems = [address.to_elements()]
        if warehouse:
            orderitems.append(E.Warehouse(warehouse))
        orderitems.extend(item.to_elements(i) for i, item in enumerate(items))

        request = E.RateRequest(
            E.Username(self.username),
            E.Password(self.password),
            E.Order(*orderitems),
        )
        response = self.make_request("/RateServices.php", request,
                                     "RateResponse")
        quotes = {}
        for quote in response("Quote"):
            quotes[quote['method']] = {
                "service": quote.Service.text,
                "carriercode": quote.CarrierCode.text,
                "cost": float(quote.Cost.text),
                "warehouse": quote.Warehouse.text,
                "mindays": quote.DeliveryEstimate.Minimum.text,
                "maxdays": quote.DeliveryEstimate.Maximum.text,
            }

        return quotes

    def submit_orders(self, orders, test=False):
        request = E.OrderList(
            E.Username(self.username),
            E.Password(self.password),
            E.Server("Test" if test else "Production"),
            *[x.to_elements() for x in orders]
        )
        response = self.make_request("/FulfillmentServices.php", request,
                                     "SubmitOrderResponse")
        total_orders = int(response.SubmitOrderResponse.TotalOrders.text)
        total_items = int(response.SubmitOrderResponse.TotalItems.text)
        orders = [(order['number'], order['id']) for order in response("Order")]
        holds = len(response("Order", status="held"))
        if holds:
            logging.warn("Submitted %d orders with holds", holds)
        return total_orders, total_items, orders

    def get_tracking(self, sw_ids):
        request = E.TrackingUpdate(
            E.Username(self.username),
            E.Password(self.password),
            E.Server("Production"),
            *[E.ShipwireId(sw_id) for sw_id in sw_ids])
        response = self.make_request("/TrackingServices.php", request,
                                     "TrackingUpdateResponse")
        tracking = [response.find("Order", shipwireId=sw_id) for sw_id in sw_ids]
        return [(track['shipped'] == 'YES', track.TrackingNumber.text if track.TrackingNumber else None)
                for track in tracking]
