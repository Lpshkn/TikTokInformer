import os
import asyncio
from tiktokinformer.informer.tiktokinformer import TikTokInformer
from tiktokinformer.database.db import Database
from telegram.ext import Updater


PG_HOST = os.getenv('PG_HOST')
PG_PORT = os.getenv('PG_PORT')
PG_NAME = os.getenv('PG_NAME')
PG_USER = os.getenv('PG_USER')
PG_PASS = os.getenv('PG_PASS')
TOKEN = os.getenv('TOKEN')


async def main():
    informer_db = Database.connect(host=PG_HOST, port=PG_PORT,
                                   user=PG_USER, password=PG_PASS,
                                   database=PG_NAME)

    updater = Updater(token=TOKEN)
    informer = TikTokInformer(database=informer_db, bot=updater.bot)
    await informer.run()


if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
