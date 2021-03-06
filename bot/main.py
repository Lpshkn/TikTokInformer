import os
from database.db import Database
from tiktokinformerbot.bot import TikTokInformerBot

PG_HOST = os.getenv('PG_HOST')
PG_PORT = os.getenv('PG_PORT')
PG_NAME = os.getenv('PG_NAME')
PG_USER = os.getenv('PG_USER')
PG_PASS = os.getenv('PG_PASS')
TOKEN = os.getenv('TOKEN')


def main():
    bot_db = Database.connect(host=PG_HOST, port=PG_PORT,
                              user=PG_USER, password=PG_PASS,
                              database=PG_NAME)

    bot = TikTokInformerBot(token=TOKEN, database=bot_db)
    bot.run()


if __name__ == '__main__':
    main()
