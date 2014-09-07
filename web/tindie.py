from bs4 import BeautifulSoup
import cStringIO
import csv
import json
import logging
import requests
import time
import urllib


def cached(fun):
    fun.cache = None
    def decorate(*args, **kwargs):
        if not fun.cache:
            fun.cache = fun(*args, **kwargs)
        return fun.cache
    return decorate


class TindieAPI(object):
    base_url = "https://www.tindie.com/"

    def __init__(self, username, auth_token=None, password=None):
        self.username = username
        self.auth_token = auth_token
        self.password = password
        self.logged_in = False
        self.session = requests.Session()

    def get_csrf_token(self, url):
        response = self.session.get(url)
        response.raise_for_status()
        soup = BeautifulSoup(response.content)
        token = soup.find('input', {"name": "csrfmiddlewaretoken"})['value']
        return token

    def form_request(self, path, data):
        for i in range(3):
            url = "%s/%s" % (self.base_url, path)
            data['csrfmiddlewaretoken'] = self.get_csrf_token(url)
            response = self.session.post(url, data=data, headers={
                'Referer': url,
            })
            if i < 2 and int(response.status_code) == 503:
                logging.warn("Delaying 5 seconds due to 503 response.")
                time.sleep(5.0)
                continue
            response.raise_for_status()
            return BeautifulSoup(response.content)

    def get_url(self, path):
        url = "%s/%s" % (self.base_url, path)
        response = self.session.get(url, headers={
            'Referer': url
        })
        response.raise_for_status()
        return BeautifulSoup(response.content)

    def login(self):
        if self.logged_in:
            return

        self.form_request('accounts/login/', data={
            'auth-username': self.username,
            'auth-password': self.password,
            'login': 'Login',
        })
        self.logged_in = True

    def get_csv_orders(self):
        self.login()
        return csv.DictReader(cStringIO.StringIO(
            self.session.get("https://www.tindie.com/orders/csv/?").content.decode(
                'utf_8_sig', errors='ignore').encode('utf8')))

    def api_request(self, path):
        response = self.session.get(
            "https://www.tindie.com/%s" % (path),
            headers={
                "Authorization": "ApiKey %s:%s" % (self.username, self.auth_token),
            })
        response.raise_for_status()
        return json.loads(response.content)

    def iter_api_request(self, method, key, delay=None, **kwargs):
        path = "api/v1/%s/?%s" % (method, urllib.urlencode(kwargs),)
        while path:
            response = self.api_request(path)
            path = response['meta'].get('next')
            for item in response[key]:
                yield item
            if delay:
                time.sleep(delay)

    def get_orders(self, **kwargs):
        return self.iter_api_request('order', 'orders', **kwargs)

    @cached
    def get_products(self):
        return list(self.iter_api_request('product', 'objects', store_username=self.username))

    def mark_shipped(self, order_id, tracking_code='', message=''):
        self.login()

        self.form_request('orders/%s/' % (order_id,), data={
            'tracking_code': tracking_code,
            'message': message,
            'save': 'Shipped',
        })

    @cached
    def get_shipping_providers(self):
        self.login()
        response = self.get_url('shipping/create/')
        select = response.find(id="id_shipping_company")
        return {x.text: int(x['value']) for x in select("option") if x['value']}

    def get_shipping_rate_ids(self):
        self.login()
        response = self.get_url('shipping/')

        rates = []
        table = response.select("table.table")[-1]
        links = [x['href'] for x in table.select("tbody a.btn-primary")]
        return [int(x.split('/')[-2]) for x in links]

    def add_shipping_rate(self, country, shipping_company_id, description, base_rate, addon_rate, product_ids):
        """Adds a shipping rate to Tindie.

        Arguments:
          country: Two letter ISO country code, or special values for regions
          shipping_company_id: Numeric ID of shipping company
          description: Name of shipping method
          base_rate: Decimal rate for first unit
          addon_rate: Decimal rate for subsequent units
          product_ids: A list of product IDs for products included in this rate.
        """
        self.login()
        self.form_request('shipping/create/', data={
            'country': country,
            'shipping_company': shipping_company_id,
            'description': description,
            'base_rate': "%.2f" % base_rate,
            'addon_rate': "%.2f" % addon_rate,
            'products': product_ids,
        })

    def delete_shipping_rate(self, rate_id):
        """Deletes a shipping rate from Tindie.

        Arguments:
          rate_id: The shipping rate ID.
        """
        self.login()
        self.form_request('shipping/rates/delete/%d/' % (rate_id,), data={
            'submit': 'Delete',
        })
