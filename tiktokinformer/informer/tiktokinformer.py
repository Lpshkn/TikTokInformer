import asyncio
import logging
from TikTokApi import TikTokApi
from tiktokinformer.utils import get_sublists
from tiktokinformer.informer.user import User
from tiktokinformer.informer.tiktok import Tiktok
from tiktokinformer.database.db import Database
from datetime import datetime, timedelta

logging.basicConfig(format='[%(asctime)s]: %(message)s\n',
                    level=logging.INFO)


class TikTokInformer:
    # Timeout of requests in seconds
    timeout = 5
    # Count of concurrent tasks
    count_tasks = 5

    def __init__(self, database: Database, bot):
        self.database = database
        self.names = []
        self.bot = bot
        self.api = TikTokApi.get_instance(use_selenium=True)

    async def run(self):
        """
        Runs a loop that creates tasks and waits when they will be finished.
        """
        while True:
            self.names = self.database.get_favourite_users()

            if not self.names:
                await asyncio.sleep(self.timeout)
                continue

            names_lists = get_sublists(self.names, self.count_tasks)

            tasks = [asyncio.create_task(self._load_profiles(names_list)) for names_list in names_lists]
            await asyncio.gather(*tasks)

    async def _load_profiles(self, names: list):
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

                # Check whether it's a new video or not
                if tiktok.time > datetime.now() - timedelta(seconds=self.timeout):
                    self.database.add_tiktok(tiktok)

                    # Send notifications
                    for chat_id in self.database.get_chats_favourite_users(name):
                        await self.send_notification(chat_id, tiktok)

        await asyncio.sleep(self.timeout)

    async def send_notification(self, chat_id: int, tiktok: Tiktok):
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
