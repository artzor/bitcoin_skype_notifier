import json
from io import BytesIO

import requests
from skpy import SkypeEventLoop
from skpy import SkypeGroupChat, SkypeSingleChat, SkypeMsg
from skpy.core import SkypeApiException
from skpy.event import SkypeNewMessageEvent


class ChatterBase:
    def send_message(self, message, chat_id, bold=False, colour='', mono=False):
        pass

    def respond_message(self, chat_id, message, bold=False, colour='', mono=False):
        pass

    def set_new_message_event(self, event_method):
        pass

    def start_listening(self):
        pass

    def cycle(self):
        pass


class MySkype(SkypeEventLoop):

    def __init__(self, user=None, pwd=None, tokenFile=None, autoAck=True, status=None):
        self.new_message = ''
        super(MySkype, self).__init__(user, pwd, tokenFile, autoAck, status)

    def onEvent(self, event):
        if type(event) == SkypeNewMessageEvent:
            cht = self.chats[event.msg.chatId]

            message_source = ''
            if type(cht) is SkypeSingleChat:
                message_source = cht.userId
            elif type(cht) is SkypeGroupChat:
                message_source = cht.topic

            self.new_message_event(event.msg.content, message_source, event.msg.chatId)

    def new_message_event(self, message_text, message_source, chat_id):
        pass


class ChatterSkype(ChatterBase):
    def __init__(self):
        token_filename = 'bot_settings/skype_token.txt'

        with open("bot_settings/skype_cred.json") as skype_cred:
            cred = json.load(skype_cred)
            login = cred['login']
            pwd = cred['pwd']

        self.sk = MySkype(login, pwd, token_filename, True)
        self.chats_dict = self.sk.chats.recent()

    def start_listening(self):
        self.sk.loop()

    def cycle(self):
        self.sk.cycle()

    def set_new_message_event(self, event_method):
        self.sk.new_message_event = event_method

    def find_chat(self, chat_topic_or_id):
        for key in self.chats_dict:
            val = self.chats_dict[key]

            if type(val) is SkypeGroupChat and val.topic == chat_topic_or_id:
                chat_value: SkypeGroupChat = self.chats_dict[key]
                return chat_value

            if (type(val) is SkypeSingleChat) and chat_topic_or_id in key:
                chat_value: SkypeSingleChat = self.chats_dict[key]
                return chat_value

        # if group chat or existing single chat not found: create new single chat with the user
        try:
            return self.sk.contacts.user(chat_topic_or_id).chat
        except (KeyError, SkypeApiException):
            return None

    @staticmethod
    def format_message(message, bold=False, colour='', mono=False):
        if bold:
            message = SkypeMsg.bold(message)

        if colour:
            message = SkypeMsg.colour(message, colour)

        if mono:
            message = SkypeMsg.mono(message)

        return message

    def send_message(self, message, chat_id, bold=False, colour='', mono=False):

        try:
            recipient = self.find_chat(chat_id)

            if not recipient:
                recipient = self.sk.chats[chat_id]

            if recipient:
                message = ChatterSkype.format_message(message, bold=bold, colour=colour, mono=mono)
                recipient.sendMsg(message, rich=True)
            else:
                raise NoRecipientException('chat {} not found'.format(chat_id))
        except NoRecipientException:
            pass

    def send_image(self, receiver, image_url, send_url_only=False):
        recipient = self.find_chat(receiver)

        if send_url_only:
            recipient.sendMsg(image_url, rich=True)
        else:
            f = BytesIO(requests.get(image_url).content)
            recipient.sendFile(f, 'file', True)


class NoRecipientException(Exception):
    pass
