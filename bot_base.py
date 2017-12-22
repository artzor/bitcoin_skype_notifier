import json

from chatter import ChatterBase


class BotBase:
    def __init__(self, chatter: ChatterBase, recipient='', name=''):
        if not name:
            self.name = self.__class__.__name__

        with open('bot_settings/{}.json'.format(self.name)) as parm_file:
            self.parameters = json.load(parm_file)
            self.recipient = self.parameters['recipient']

        if recipient:
            self.recipient = recipient

        self.chatter = chatter
        self.name = name

    # TODO:
    def first_run_message(self):
        pass

    def next_message(self):
        pass

    def say(self, message, colour='', bold=False, mono=False):
        self.chatter.send_message(self.recipient, message, bold, colour, mono)
