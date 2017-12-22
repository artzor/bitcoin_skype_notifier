from datetime import datetime

import requests

from bot_base import BotBase
from chatter import ChatterSkype


class BotBtcSender(BotBase):
    @staticmethod
    def get_coinmarketcap_prices():
        btc_price = requests.get('https://api.coinmarketcap.com/v1/ticker/bitcoin/').json()[0]['price_usd']
        bch_price = requests.get('https://api.coinmarketcap.com/v1/ticker/bitcoin-cash/').json()[0]['price_usd']
        eth_price = requests.get('https://api.coinmarketcap.com/v1/ticker/ethereum/').json()[0]['price_usd']
        iota_price = requests.get('https://api.coinmarketcap.com/v1/ticker/iota/').json()[0]['price_usd']

        return '''BTC:  {}\nBCH:  {}\nETH:  {}\nIOTA: {}'''.format(btc_price, bch_price, eth_price, iota_price)

    def get_crypto_prices(self):
        price = BotBtcSender.get_coinmarketcap_prices()
        return price


chatter = ChatterSkype()
btc_sender = BotBtcSender(chatter)

dt = '[Crypto rates : {} ]'.format(datetime.now().strftime('%Y-%m-%d %H:%M')) + '\n'
prices = btc_sender.get_crypto_prices()
btc_sender.say(dt + prices, mono=True)

'''
    def get_btc(self):
        url = 'https://api.coindesk.com/v1/bpi/currentprice/USD.json'
        resp = requests.get(url).json()
        price = float(resp['bpi']['USD']['rate'].replace(',', ''))
        price = int(round(price))

        return price
'''
