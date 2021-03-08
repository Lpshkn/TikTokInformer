"""
This method implements the inheritance from the BasePersistence class to provide the persistence of the bot.
"""
from database.db import Database
from telegram.ext import BasePersistence
from collections import defaultdict
from copy import deepcopy


class BotPersistence(BasePersistence):
    def __init__(self, database: Database,
                 store_user_data=True,
                 store_chat_data=True,
                 store_bot_data=True,
                 on_flush=False):
        super(BotPersistence, self).__init__(store_user_data=store_user_data,
                                             store_chat_data=store_chat_data,
                                             store_bot_data=store_bot_data)
        self.database = database
        self.on_flush = on_flush
        self.user_data = None
        self.chat_data = None
        self.bot_data = None
        self.conversations = None

    def get_user_data(self):
        """Returns the user_data from the pickle file if it exsists or an empty defaultdict.
        Returns:
            :obj:`defaultdict`: The restored user data.
        """
        if self.user_data:
            pass
        else:
            data = self.database.get_user_data()
            if not data:
                data = defaultdict(dict)
            else:
                data = defaultdict(dict, data)
            self.user_data = data

        return deepcopy(self.user_data)

    def get_chat_data(self) -> dict:
        """
        Returns the chat_data from the database.
        :return: The restored chat data.
        """
        if self.chat_data:
            pass
        else:
            data = self.database.get_chat_data()
            if not data:
                data = defaultdict(dict)
            else:
                data = defaultdict(dict, data)
            self.chat_data = data

        return deepcopy(self.chat_data)

    def get_conversations(self, name):
        if self.conversations:
            pass
        else:
            data = self.database.get_conversations()
            if not data:
                data = {}
            self.conversations = data

        return self.conversations.get(name, {}).copy()

    def update_chat_data(self, chat_id, data):
        """
        Will update the chat_data (if changed) and save the data into the database.
        :param chat_id: The chat the data might have been changed for.
        :param data: The :attr:`telegram.ext.dispatcher.chat_data` [chat_id].
        """
        if self.chat_data is None:
            self.chat_data = defaultdict(dict)
        if self.chat_data.get(chat_id) == data:
            return
        self.chat_data[chat_id] = data
        if not self.on_flush:
            self.database.update_chat_data(self.chat_data)

    def update_user_data(self, user_id, data):
        """Will update the user_data (if changed) and depending on :attr:`on_flush` save the
        pickle file.
        Args:
            user_id (:obj:`int`): The user the data might have been changed for.
            data (:obj:`dict`): The :attr:`telegram.ext.dispatcher.user_data` [user_id].
        """
        if self.user_data is None:
            self.user_data = defaultdict(dict)
        if self.user_data.get(user_id) == data:
            return
        self.user_data[user_id] = data
        if not self.on_flush:
            self.database.update_user_data(self.user_data)

    def update_conversation(self, name: str, key: tuple, new_state: int):
        """
        Will update the conversations for the given handler and depending on :attr:`on_flush`
        save data in the database.
        :param name: The handlers name.
        :param key: The key the state is changed for.
        :param new_state: The new state for the given key.
        """
        # Since, this bot can't be invited into a group, it has just chat_id (as key) and will have no name
        if self.conversations.setdefault(name, {}).get(key) == new_state:
            return

        self.conversations[name][key] = new_state

        if not self.on_flush:
            self.database.update_conversations(self.conversations)

    def flush(self):
        if self.user_data:
            self.database.update_user_data(self.user_data)
        if self.chat_data:
            self.database.update_chat_data(self.chat_data)
        if self.bot_data:
            self.database.update_bot_data(self.bot_data)
        if self.conversations:
            self.database.update_conversations(self.conversations)

        self.database.connection.close()

    def update_bot_data(self, data):
        if self.bot_data is None:
            self.bot_data = defaultdict(dict)
        if self.bot_data == data:
            return
        self.bot_data = data
        if not self.on_flush:
            self.database.update_bot_data(self.bot_data)

    def get_bot_data(self):
        if self.user_data:
            pass
        else:
            data = defaultdict(dict)
            self.user_data = data

        return deepcopy(self.user_data)
