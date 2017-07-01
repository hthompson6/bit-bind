# MIT License
# 
# Copyright (c) 2017 Hunter Thompson
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
# 
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
# 
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
#SOFTWARE.

import hashlib
import hmac
import requests
import time
import urllib

BASE_URL = 'https://bittrex.com/api/v1.1/{}/{}'


class BittrexAPIBind(object):

    def __init__(self, api_key, api_secret, lower_bound=None, upper_bound=None):
        self.api_key = api_key
        self.api_secret = api_secret
        self.lower_bound = lower_bound
        self.upper_bound = upper_bound

    def _api_query(self, scope, req, **kwargs):

        tokens = ('{}?').format(req)
        request_header = None

        if scope == 'account':
            nonce = str(int(time.time()/100))
            tokens += ('apikey={}&nonce={}').format(self.api_key, nonce)

        if kwargs:
            tokens += ('&{}').format(urllib.urlencode(kwargs))

        request_url = (BASE_URL).format(scope, tokens)

        if scope == 'account':
            api_sign = hmac.new(self.api_secret.encode(),
                                request_url.encode(),
                                hashlib.sha512).hexdigest()
            request_header = dict(apisign=api_sign)

        return requests.get(request_url, headers=request_header).json()


    def get_market_summary(self, currency_base, currency_market):
        market = ('{}-{}').format(currency_base, currency_market)
        resp = self._api_query('public', 'getmarketsummary', market=market)
        market = resp['result'][0]
        return market['PrevDay'], market['Last']

    def get_balances(self):
        resp = self._api_query('account', 'getbalances')
        cnt = -1
        wallet = resp['result']
        while cnt < len(wallet)-1:
            cnt += 1
            if not wallet[cnt].get('Balance') or wallet[cnt].get('Currency') in ["BTC", "ETH"]:
                del wallet[cnt]
                cnt -= 1

        return resp['result']
