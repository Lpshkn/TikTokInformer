import tiktokinformerbot.handlers as handlers
import logging
from tiktokinformerbot.persistence import BotPersistence
from database.db import Database
from telegram.ext import Updater, CommandHandler, ConversationHandler, MessageHandler, Filters

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)


class TikTokInformerBot:
    def __init__(self, token: str, database: Database):
        persistence = BotPersistence(database)

        self.database = database

        self.updater = Updater(token=token, use_context=True, persistence=persistence)
        self.dispatcher = self.updater.dispatcher
        self.dispatcher.bot_data['database'] = database
        self.job_queue = self.updater.job_queue

        # Dictionary with the chat_id and entries of this chat that a user want to add.
        # This dict will be cleared when the user will press the "accept" or the "cancel" button
        self.entries = {}

    def run(self):
        """
        The entrypoint of the bot. Define the ConversationHandler and specify all the handlers.
        """
        conversation_handler = ConversationHandler(
            entry_points=[CommandHandler('start', handlers.start_handler)],
            states={
                handlers.MAIN: [MessageHandler(Filters.text & ~Filters.command, handlers.main_menu_handler)],
            },
            fallbacks=[CommandHandler('stop', handlers.stop_bot_handler)],

            name="main_menu_state",
            persistent=True,
            per_user=False
        )

        self.dispatcher.add_handler(conversation_handler)

        self.updater.start_polling()
        self.updater.idle()
