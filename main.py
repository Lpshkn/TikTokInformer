import asyncio
from tiktokinformer.informer.tiktokinformer import TikTokInformer
from tiktokinformer.utils import get_top_users
from tiktokinformer.database.db import Database


async def main():
    db = Database.connect(host='localhost', port='5432',
                          user='postgres', password='KPN6trvEBaguvix123852951',
                          database='tiktokinformer')

    names = get_top_users(10)

    informer = TikTokInformer(names, database=db)
    await informer.run()


if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
