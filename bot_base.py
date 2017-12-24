from datetime import time, datetime

from apscheduler.schedulers.background import BackgroundScheduler
from sqlalchemy import Column, Integer, String
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

from chatter import ChatterBase

engine = create_engine('sqlite:///user_data.db', echo=False)

Base = declarative_base()
Session = sessionmaker(bind=engine)


# logging.basicConfig()
# logging.getLogger('sqlalchemy').setLevel(logging.ERROR)


class Subscriber(Base):
    __tablename__ = 'subscribers'

    user_id = Column(String(50), primary_key=True)
    repeat = Column(Integer)
    sleep_from = Column(Integer)
    sleep_to = Column(Integer)

    def __repr__(self):
        return "<Subscriber(id='%s', repeat='%s', sleep_from='%s', sleep_to='%s')>" % (
            self.id, self.repeat, self.sleep_from, self.sleep_to)


Base.metadata.create_all(engine)


class BotBase:
    def __init__(self, chatter: ChatterBase):
        self.session = Session()
        self.subscribers = {}

        # I never expect to have any significant amount of users, so I'll just load all in memory on start
        self.load_subscribers()

        self.chatter = chatter
        self.chatter.set_new_message_event(self.new_message_event)

        self.scheduler = BackgroundScheduler()
        self.schedule_jobs()

    def load_subscribers(self):
        for row in self.session.query(Subscriber):
            s: Subscriber = row
            self.subscribers[s.user_id] = {'repeat': s.repeat, 'sleep_from': s.sleep_from, 'sleep_to': s.sleep_to}

    # bot_base has essential commands: subscribe/unsubscribe/sleep
    def user_subscribe(self, user_id, period):
        session = self.session
        subscriber = session.query(Subscriber).filter_by(user_id=user_id).first()

        if subscriber:
            subscriber.repeat = period
            self.scheduler.remove_job(user_id)
        else:
            subscriber = Subscriber(user_id=user_id, repeat=period)

        session.add(subscriber)
        session.commit()

        self.scheduler.add_job(self.send_to_periodic_subscribers, 'interval', seconds=period, args=[user_id],
                               id=user_id)
        self.subscribers[user_id] = {'repeat': period, 'sleep_from': 0, 'sleep_to': 0}

    def user_unsubscribe(self, user_id):
        session = self.session
        subscriber = session.query(Subscriber).filter(Subscriber.user_id == user_id).first()

        if subscriber:
            self.scheduler.remove_job(user_id)

        session.query(Subscriber).filter(Subscriber.user_id == user_id).delete()
        session.commit()

        if user_id in self.subscribers.keys():
            del self.subscribers[user_id]

    def user_sleep(self, user_id, sleep_from, sleep_to):
        session = self.session
        subscriber = session.query(Subscriber).filter(Subscriber.user_id == user_id).first()
        subscriber.sleep_from = sleep_from
        subscriber.sleep_to = sleep_to

        session.add(subscriber)
        session.commit()

        self.subscribers[user_id]['sleep_from'] = sleep_from
        self.subscribers[user_id]['sleep_to'] = sleep_to

        print('sleep configured for {}'.format(user_id))

    def user_get_subscription(self, user_id):
        session = self.session
        subscriber = session.query(Subscriber).filter_by(user_id=user_id).first()

        return subscriber.repeat if subscriber else 0

    def schedule_jobs(self):
        print('scheduling jobs...')
        for key, value in self.subscribers.items():
            self.scheduler.add_job(self.send_to_periodic_subscribers, 'interval', seconds=value['repeat'], args=[key],
                                   id=key)
            print('scheduling {} every {}'.format(key, value['repeat']))

        self.scheduler.start()

    def is_sleep_time(self, user_id):
        subscriber_settings: dict = self.subscribers.get(user_id)
        sleep_from = subscriber_settings.get('sleep_from', 0)
        sleep_to = subscriber_settings.get('sleep_to', 0)

        if not sleep_from and not sleep_to:
            return False

        sleep_from = time(sleep_from, 0, 0)
        sleep_to = time(sleep_to, 0, 0)

        cur_time = datetime.now().time()

        def time_in_range(start, end, x):
            if start <= end:
                return start <= x <= end
            else:
                return start <= x or x <= end

        if time_in_range(sleep_from, sleep_to, cur_time):
            return True
        else:
            return False

    # respond or distribute message to all subscribers
    def say(self, message, chat_id, bold=False, mono=False, colour=''):
        self.chatter.send_message(message, chat_id, bold, colour, mono)

    # classes can implement it
    def new_message_event(self, message_text, message_source, chat_id):
        pass

    def start_listening(self):  # start bot's event loop
        self.chatter.start_listening()

    def send_to_periodic_subscribers(self, chat_id):
        if self.is_sleep_time(chat_id):
            raise SleepTimeException


class ProcessCommandException(Exception):
    pass


class SleepTimeException(Exception):
    pass
