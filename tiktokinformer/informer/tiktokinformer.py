import logging
import time
from TikTokApi import TikTokApi
from tiktokinformer.informer.user import User
from tiktokinformer.informer.tiktok import Tiktok
from tiktokinformer.database.db import Database
from datetime import datetime, timedelta

logging.basicConfig(format='[%(asctime)s]: %(message)s\n',
                    level=logging.INFO)


class TikTokInformer:
    # Timeout of requests in seconds
    timeout = 300

    def __init__(self, database: Database, bot):
        self.database = database
        self.names = []
        self.bot = bot
        self.api = TikTokApi.get_instance(use_selenium=True)
        self.last_timestamps = {}

    def run(self):
        """
        Runs a loop that creates tasks and waits when they will be finished.
        """
        while True:
            self.names = self.database.get_favourite_users()

            if not self.names:
                time.sleep(self.timeout)
                continue

            self._load_profiles(self.names)

    def _load_profiles(self, names: list):
        """
        Makes a request to TikTok for certain profiles and insert information about it
        and its videos into the database.

        :param names: list of unique names of TikTok profiles
        """
        for name in names:
            user_dict = self.api.getUser(username=name)
            user = User(user_dict)
            self.database.add_user(user)

            # Iterate from the last tiktok to the first
            for item in user_dict['items'][::-1]:
                tiktok = Tiktok(item)

                if tiktok.time > self.last_timestamps.get(name, datetime.now() - timedelta(seconds=self.timeout)):
                    # Check whether it's a new video or not
                    self.database.add_tiktok(tiktok)
                    self.last_timestamps[name] = tiktok.time

                    # Send notifications
                    for chat_id in self.database.get_chats_favourite_users(name):
                        self.send_notification(chat_id, tiktok)

        time.sleep(self.timeout)

    def send_notification(self, chat_id: int, tiktok: Tiktok):
        """
        Method to send notification to a user that a new video was released.

        :param chat_id: the id of a user
        :param tiktok: Tiktok object
        """
        text = f"Тут вышло новое видео у @{tiktok.user_id}, посмотри!\n\n" \
               f"Описание: {tiktok.desc}.\n\n" \
               f"https://www.tiktok.com/@{tiktok.user_id}/video/{tiktok.id}"

        self.bot.sendMessage(chat_id=chat_id,
                             text=text,
                             disable_web_page_preview=True)
