from bot_base import ProcessCommandException, BotBase


class BotCommandBase:
    def __init__(self, args, message_source, chat_id, bot: BotBase):
        self.args = args
        self.message_source = message_source
        self.chat_id = chat_id
        self.bot = bot

    def run_command(self):
        raise Exception('This method should be overridden.')


class BotCommandSub(BotCommandBase):
    def run_command(self):
        try:
            if len(self.args) == 0:
                period = self.bot.user_get_subscription(self.message_source)

                if period:
                    return "'{}' is subscribed to receive updates every {} minutes. Next run: {}".format \
                        (self.message_source, period, self.bot.get_next_run_time(self.message_source))
                else:
                    return "'{}' is not subscribed.".format(self.message_source)

            else:
                period = int(self.args[0])

                if period <= 0 or not period:
                    raise ProcessCommandException

                self.bot.user_subscribe(self.message_source, period)

                return "'{}' is subscribed to receive updates every {} minutes".format(self.message_source, period)

        except (TypeError, ValueError, IndexError, ProcessCommandException):
            raise ProcessCommandException


class BotCommandUnsub(BotCommandBase):
    def run_command(self):
        self.bot.user_unsubscribe(self.message_source)
        return "'{}' is unsubscribed from receiving periodic updates.".format(self.message_source)


class BotCommandSleep(BotCommandBase):
    def run_command(self):

        try:
            if not self.bot.subscribers.get(self.message_source):
                return 'User {} is not subscribed. Use sub command to subscribe first.'.format(self.message_source)

            if len(self.args) == 0:
                sleep_from, sleep_to = self.bot.get_sleep_hours(self.message_source)
                return 'Sleeping from {} to {}'.format(sleep_from, sleep_to)

            sleep_times = self.args[0].split('..')

            sleep_from = int(sleep_times[0])
            sleep_to = int(sleep_times[1])

            if sleep_from >= 24 or sleep_to >= 24 or sleep_from < 0 or sleep_to < 0:
                raise ProcessCommandException

            self.bot.user_sleep(self.message_source, sleep_from, sleep_to)
            return "OK, I won't send updates from {}:00 till {}:00".format(sleep_from, sleep_to)

        except (IndexError, ValueError):
            raise ProcessCommandException


class BotCommandHelp(BotCommandBase):
    def run_command(self):
        return 'comman list:\nbotinok sub N - subscribe to receive updates every N minutes (N should be integer value > 0)\n' + \
               'botinok unsub - unsubscribe from updates\n' + \
               'botinok sleep FR..TO - bot will not send updates from FR to TO time'
