import hashlib
import hmac
import requests
import time
import urllib

BASE_URL = 'https://bittrex.com/api/v1.1/{}/{}'


class BittrexAPIBinder(object):

    def __init__(self, api_key, api_secret, lower_bound=None, upper_bound=None):
        self.api_key = api_key
        self.api_secret = api_secret
        self.lower_bound = lower_bound
        self.upper_bound = upper_bound

    def _api_query(self, scope, req, **kwargs):
        nonce = str(int(time.time()/100))
        tokens = ('{}?apikey={}&nonce={}').format(req, self.api_key, nonce)

        if kwargs:
            tokens += ('&{}').format(urllib.urlencode(kwargs))

        request_url = (BASE_URL).format(scope, tokens)

        api_sign = hmac.new(self.api_secret.encode(), request_url.encode(), hashlib.sha512).hexdigest()
        request_header = dict(apisign=api_sign)

        return requests.get(request_url, headers=request_header).json()


    def get_current_value(self, currency_base, currency_market):
        market = ('{}-{}').format(currency_base, currency_market)
        resp = self._api_query('public', 'getticker', market=market)

        return resp['result']['Last']

    def get_balances(self):
        resp = self._api_query('account', 'getbalances')

        for currency in resp['result']:
            if not currency['Balance']:
                del resp['result'][currency]

        return resp


bit = BittrexAPIBind('xxxxxxxxxxxxxxxxx', 'zzzzzzzzzzzzzzz')
print(('{:.8f}').format(bit.get_current_value('BTC', 'VOX')))
