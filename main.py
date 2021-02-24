import asyncio
import os
from tiktokinformer.informer.tiktokinformer import TikTokInformer
from tiktokinformer.utils import get_top_users
from tiktokinformer.database.db import Database

PG_HOST = os.getenv('PG_HOST')
PG_PORT = os.getenv('PG_PORT')
PG_NAME = os.getenv('PG_NAME')
PG_USER = os.getenv('PG_USER')
PG_PASS = os.getenv('PG_PASS')


async def main():
    db = Database.connect(host=PG_HOST, port=PG_PORT,
                          user=PG_USER, password=PG_PASS,
                          database=PG_NAME)

    names = get_top_users(10)

    informer = TikTokInformer(names, database=db)
    await informer.run()


if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
