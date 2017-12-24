import threading
import time
from datetime import datetime

import requests

from bot_base import BotBase, ProcessCommandException, SleepTimeException
from bot_commands import BotCommandSub, BotCommandUnsub, BotCommandSleep, BotCommandHelp
from chatter import ChatterSkype

cache_age = 180
bot_call_name = 'botinok'


class BotBtcSender(BotBase):
    cache_dt = 0
    prices_formatted = ''

    def get_coinmarketcap_prices(self):
        cache_time_dif = int(time.time()) - self.cache_dt

        if self.prices_formatted and cache_time_dif <= cache_age:
            return self.prices_formatted

        btc_price = requests.get('https://api.coinmarketcap.com/v1/ticker/bitcoin/').json()[0]['price_usd']
        bch_price = requests.get('https://api.coinmarketcap.com/v1/ticker/bitcoin-cash/').json()[0]['price_usd']
        eth_price = requests.get('https://api.coinmarketcap.com/v1/ticker/ethereum/').json()[0]['price_usd']
        iota_price = requests.get('https://api.coinmarketcap.com/v1/ticker/iota/').json()[0]['price_usd']
        monero_price = requests.get('https://api.coinmarketcap.com/v1/ticker/monero/').json()[0]['price_usd']

        self.cache_dt = int(time.time())
        self.prices_formatted = '''BTC:  {}\nBCH:  {}\nETH:  {}\nIOTA: {}\nXMR:  {}'''.format(
            btc_price, bch_price, eth_price, iota_price, monero_price)

        return self.prices_formatted

    def tell_prices(self, respond_to=''):
        dt = '[Cryptocurrency rates : {} ]'.format(datetime.now().strftime('%Y-%m-%d %H:%M')) + '\n'

        prices = self.get_crypto_prices()
        self.say(dt + prices, chat_id=respond_to, mono=True)


    def get_crypto_prices(self):
        price = self.get_coinmarketcap_prices()
        return price

    def new_message_event(self, message_text, message_source, chat_id):
        msg_text: str = message_text
        msg_text = msg_text.lower()

        words = msg_text.split(' ')

        if ('почем' in msg_text or 'почём' in msg_text) and 'крипта' in msg_text:
            self.tell_prices(respond_to=chat_id)

        elif len(words) > 1 and words[0] == bot_call_name:
            self.process_command(words[1], words[2:], message_source, chat_id)

    def process_command(self, command, args, message_source, chat_id):
        try:
            if command == 'sub':
                resp = BotCommandSub(args, message_source, chat_id, self).run_command()
                self.say(resp, chat_id)

            elif command == 'unsub':
                resp = BotCommandUnsub(args, message_source, chat_id, self).run_command()
                self.say(resp, chat_id)

            elif command == 'sleep':
                resp = BotCommandSleep(args, message_source, chat_id, self).run_command()
                self.say(resp, chat_id)

            elif command == 'help':
                resp = BotCommandHelp(args, message_source, chat_id, self).run_command()
                self.say(resp, chat_id)

            else:
                raise ProcessCommandException
        except ProcessCommandException:
            self.say("Sorry, can't process this command.", chat_id=chat_id)

    def process_command_sleep(self, args, message_source, chat_id):
        resp = BotCommandSleep(args, message_source, chat_id, self).run_command()
        self.say(resp, chat_id=chat_id)

    def send_to_periodic_subscribers(self, chat_id):
        try:
            super(BotBtcSender, self).send_to_periodic_subscribers(chat_id)
            print('sending periodic message to {}'.format(chat_id))
            self.tell_prices(chat_id)
        except SleepTimeException:
            print('message to {} not sent, it is sleep time'.format(chat_id))


def listen():
    btc_sender = BotBtcSender(ChatterSkype())
    btc_sender.start_listening()


listen_thread = threading.Thread(target=listen)
listen_thread.start()

print('started listening for messages...')
