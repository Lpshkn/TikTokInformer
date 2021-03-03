import asyncio
import logging
from TikTokApi import TikTokApi
from tiktokinformer.utils import get_sublists
from tiktokinformer.informer.user import User
from tiktokinformer.informer.tiktok import Tiktok
from tiktokinformer.database.db import Database
from tiktokinformer.bot.bot import TikTokInformerBot

logging.basicConfig(format='[%(asctime)s]: %(message)s\n',
                    level=logging.INFO)


class TikTokInformer:
    # Timeout of requests in seconds
    timeout = 300
    # Count of concurrent tasks
    count_tasks = 5
    # Dict of {username: timestamp_of_the_last_video}
    last_timestamps = {}

    def __init__(self, names: list, database: Database, bot: TikTokInformerBot):
        self.database = database
        self.names = names
        self.bot = bot
        self.api = TikTokApi.get_instance(use_selenium=True)

    async def run(self):
        """
        Runs a loop that creates tasks and waits when they will be finished.
        """
        self._init_timestamps()

        names_lists = get_sublists(self.names, self.count_tasks)

        while True:
            tasks = [asyncio.create_task(self._load_profiles(names_list)) for names_list in names_lists]
            await asyncio.gather(*tasks)

    def _init_timestamps(self):
        """
        Gets from the database the timestamp of the last video of each user.
        """
        for name in self.names:
            timestamp = self.database.get_last_timestamp(name)
            self.last_timestamps[name] = timestamp

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
                if tiktok.time > self.last_timestamps.get(user.unique_id, 0):
                    self.last_timestamps[user.unique_id] = tiktok.time
                    self.database.add_tiktok(tiktok)

                    # Send notifications
                    for chat_id in self.database.get_chats_favourite_users(name):
                        await self.bot.send_notification(chat_id, tiktok)

        await asyncio.sleep(self.timeout)
