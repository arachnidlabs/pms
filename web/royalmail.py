from bs4 import BeautifulSoup
import cStringIO
import collections
import csv
import math
import requests


POSTING_FIELDS = [
    'Customer Account Number',
    'Product Code',
    'Service Register',
    'Weight(g)',
    'Number Of Items / Directs',
    'Bag Count',
    'Class',
    'Format',
    'Sortation',
    'Submission',
    'OCR Indicator',
    'Franking Indicator',
    'Franking Surcharge',
    'Zone Identifier',
    'Country Identifier',
    'Residues',
    'Region',
    'Container Type',
    'Consignment Reference Number',
    'Department',
    'Your Reference',
    'Fees',
    'Magazine Code Issue ID',
    'Magazine Code',
    'Mailmedia Booking Reference Number',
    'MAP Reference Number',
    'Posting Location Number',
    'Customer Email Address',
    'Your Description',
    'Customer Reference',
    'Your Notes',
    'Auto Confirm Order'
]


PostingKey = collections.namedtuple('PostingKey', [
    'product_code',
    'klass',
    'format',
    'country_identifier',
    'weight'])


def roundup(x, accuracy):
    return int(math.ceil(float(x) / accuracy)) * accuracy


def get_posting_key(package):
    if package.zone == 'GB':
        return PostingKey('STL', 'F', 'P', '', roundup(package.shipping_weight, 1000))
    else:
        if package.shipping_weight < 100:
            weight = 100
        else:
            weight = roundup(package.shipping_weight, 250)
        return PostingKey('OLA', '', '', package.zone, weight)


class RoyalMailAPI(object):
    def __init__(self, account_number, service_register, posting_location, email, auto_confirm, password):
        # TODO: Refactor out dependency on config parser
        self.account_number = account_number
        self.service_register = service_register
        self.posting_location = posting_location
        self.email = email
        self.auto_confirm = auto_confirm
        self.password = password
        self.logged_in = False
        self.session = requests.Session()

    def generate_posting(self, packages, posting_id, outfile):
        packages = list(packages)

        postings = collections.defaultdict(list)
        for package in packages:
            postings[get_posting_key(package)].append(package)

        w = csv.DictWriter(outfile, POSTING_FIELDS)
        w.writerow(dict((k, k) for k in POSTING_FIELDS))
        for posting, packages in postings.iteritems():
            w.writerow({
                'Customer Account Number': self.account_number,
                'Product Code': posting.product_code,
                'Service Register': self.service_register,
                'Weight(g)': posting.weight,
                'Number Of Items / Directs': len(packages),
                'Class': posting.klass,
                'Format': posting.format,
                'Container Type': 'Bags',
                'Country Identifier': posting.country_identifier,
                'Your Reference': '%s' % (posting_id,),
                'Your Notes': '; '.join(package.order.remote_order_id for package in packages),
                'Posting Location Number': self.posting_location,
                'Customer Email Address': self.email,
                'Auto Confirm Order': self.auto_confirm,
            })

    def login(self):
        if self.logged_in:
            return

        url = 'https://www.royalmail.com/discounts-payment/credit-account/online-business-account'
        response = self.session.get(url)
        soup = BeautifulSoup(response.content)
        form_build = soup.find("input", {"name": "form_build_id"})['value']

        response = self.session.post(url, data={
            'name': self.email,
            'pass': self.password,
            'op': 'Login',
            'form_id': 'user_login',
            'form_build_id': form_build,
        }, headers={'Referer': url})
        response.raise_for_status()
        self.logged_in = True

    def upload_posting(self, packages, posting_id):
        out = cStringIO.StringIO()
        self.generate_posting(packages, posting_id, out)

        self.login()

        response = self.session.post(
            'https://www.oba.royalmail.com/DirectUpload/servlet/UploadFileServlet',
            data={
                'selPostingLoc': self.posting_location,
                'postingLocCP': self.posting_location,
            },
            verify=False)
        response.raise_for_status()

        response = self.session.post(
            'https://www.oba.royalmail.com/DirectUpload/servlet/ProcessFileServlet',
            files={'dateFile': ('posting.csv', out.getvalue())},
            verify=False)
        response.raise_for_status()
