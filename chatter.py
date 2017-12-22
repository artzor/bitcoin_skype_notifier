import json
from io import BytesIO

import requests
from skpy import Skype
from skpy import SkypeGroupChat, SkypeSingleChat, SkypeMsg


class ChatterBase:
    def send_message(self, receiver, message, bold=False, colour='', mono=False):
        pass


class ChatterSkype(ChatterBase):

    def __init__(self):
        token_filename = 'bot_settings/skype_token.txt'

        with open("bot_settings/skype_cred.json") as skype_cred:
            cred = json.load(skype_cred)
            login = cred['login']
            pwd = cred['pwd']

        self.sk = Skype(login, pwd, token_filename)
        self.chats_dict = self.sk.chats.recent()

        print(self.chats_dict)

    def find_chat(self, chat_topic):
        for key in self.chats_dict:
            val = self.chats_dict[key]

            if type(val) is SkypeGroupChat and val.topic == chat_topic:
                chat_value: SkypeGroupChat = self.chats_dict[key]
                return chat_value

            if (type(val) is SkypeSingleChat) and chat_topic in key:
                chat_value: SkypeSingleChat = self.chats_dict[key]
                return chat_value

        return self.sk.contacts.user(chat_topic).chat

    def send_message(self, receiver, message, bold=False, colour='', mono=False):
        recipient = self.find_chat(receiver)

        if recipient:
            if bold:
                message = SkypeMsg.bold(message)

            if colour:
                message = SkypeMsg.colour(message, colour)

            if mono:
                message = SkypeMsg.mono(message)

            recipient.sendMsg(message, rich=True)
        else:
            raise NoRecipientException('recipient {} not found'.format(receiver))

    def send_image(self, receiver, image_url, send_url_only=False):
        recipient = self.find_chat(receiver)

        if send_url_only:
            recipient.sendMsg(image_url, rich=True)
        else:
            f = BytesIO(requests.get(image_url).content)
            recipient.sendFile(f, 'file', True)


class NoRecipientException(Exception):
    pass
