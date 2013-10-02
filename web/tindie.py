from bs4 import BeautifulSoup
import cStringIO
import csv
import json
import requests
import urllib


class TindieAPI(object):
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
        print (response.url, token)
        return token

    def form_request(self, path, data):
        url = "https://www.tindie.com/%s" % (path,)
        data['csrfmiddlewaretoken'] = self.get_csrf_token(url)
        response = self.session.post(url, data=data, headers={
            'Referer': url,
        })
        response.raise_for_status()
        return response

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

    def iter_api_request(self, method, key, **kwargs):
        path = "api/v1/%s/?%s" % (method, urllib.urlencode(kwargs),)
        while path:
            response = self.api_request(path)
            path = response['meta'].get('next')
            for item in response[key]:
                yield item

    def get_orders(self, **kwargs):
        return self.iter_api_request('order', 'orders', **kwargs)

    def mark_shipped(self, order_id, tracking_code='', message=''):
        self.login()

        self.form_request('orders/%s/' % (order_id,), data={
            'tracking_code': tracking_code,
            'message': message,
            'save': 'Shipped',
        })
