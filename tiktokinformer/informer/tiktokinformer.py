import asyncio
from TikTokApi import TikTokApi
from tiktokinformer.utils import get_sublists
from tiktokinformer.informer.user import User
from tiktokinformer.informer.tiktok import Tiktok
from tiktokinformer.database.db import Database


class TikTokInformer:
    # Timeout of requests in seconds
    timeout = 300
    # Count of concurrent tasks
    count_tasks = 5

    def __init__(self, names: list, database: Database):
        self.database = database
        self.names = names
        self.api = TikTokApi.get_instance()

    async def run(self):
        """
        Runs a loop that creates tasks and waits when they will be finished.
        """
        names_lists = get_sublists(self.names, self.count_tasks)

        while True:
            tasks = [asyncio.create_task(self._load_profiles(names_list)) for names_list in names_lists]
            await asyncio.gather(tasks)

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

            tiktok = Tiktok(user_dict['items'][0])
            self.database.add_tiktok(tiktok)

        await asyncio.sleep(self.timeout)
