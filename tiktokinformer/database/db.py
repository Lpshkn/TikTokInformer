import psycopg2
import logging
from psycopg2 import sql
from collections import defaultdict
from tiktokinformer.informer.user import User
from tiktokinformer.informer.tiktok import Tiktok
from datetime import datetime as dt

logging.basicConfig(format='[%(asctime)s]: %(message)s\n',
                    level=logging.WARNING)


class Database:
    def __init__(self):
        self._connection = None

    @staticmethod
    def connect(host: str,
                port: str,
                user: str,
                password: str,
                database: str):
        """
        Creates connection to the database using the passed credentials.

        :return: the connection object
        """
        db_object = Database()
        db_object._connection = psycopg2.connect(host=host,
                                                 port=port,
                                                 user=user,
                                                 password=password,
                                                 database=database)
        db_object._init_tables()
        return db_object

    def _init_tables(self):
        """
        Creates tables if it weren't created.
        """
        with self.connection.cursor() as cur:
            cur.execute("CREATE TABLE IF NOT EXISTS users ("
                        "unique_id TEXT PRIMARY KEY, "
                        "nickname TEXT NOT NULL, "
                        "followers_cnt INTEGER NOT NULL, "
                        "following_cnt INTEGER NOT NULL, "
                        "heart_cnt INTEGER NOT NULL, "
                        "video_cnt INTEGER NOT NULL); ")
                    
            cur.execute("CREATE TABLE IF NOT EXISTS tiktoks ("
                        "id BIGINT PRIMARY KEY, "
                        "user_id TEXT, "
                        "description TEXT NOT NULL, "
                        "time TIMESTAMP NOT NULL, "
                        "CONSTRAINT fk_users FOREIGN KEY (user_id) "
                        "REFERENCES users (unique_id) "
                        "ON DELETE CASCADE "
                        "ON UPDATE CASCADE);")
                    
            cur.execute("CREATE TABLE IF NOT EXISTS conversations ("
                        "chat_id INTEGER PRIMARY KEY, "
                        "main_menu_state INTEGER NULL); ")

            cur.execute("CREATE TABLE IF NOT EXISTS chats ("
                        "chat_id INTEGER PRIMARY KEY REFERENCES conversations "
                        "ON DELETE CASCADE ON UPDATE CASCADE, "
                        "title VARCHAR(256), "
                        "description VARCHAR(256), "
                        "photo VARCHAR(1000));")

            cur.execute("CREATE TABLE IF NOT EXISTS bot_users ("
                        "user_id INTEGER PRIMARY KEY, "
                        "chat_id INTEGER REFERENCES conversations ON DELETE SET NULL ON UPDATE CASCADE, "
                        "username VARCHAR(32), "
                        "first_name VARCHAR(256), "
                        "last_name VARCHAR(256));")

            cur.execute("CREATE TABLE IF NOT EXISTS favourite_users ("
                        "id SERIAL PRIMARY KEY, "
                        "unique_id TEXT REFERENCES users ON DELETE CASCADE ON UPDATE CASCADE, "
                        "chat_id INTEGER REFERENCES conversations ON DELETE CASCADE ON UPDATE CASCADE);")

        self.connection.commit()

    @property
    def connection(self):
        if self._connection is None:
            raise ValueError("Connection to the database wasn't made")
        return self._connection

    def _add_row(self, sql_query: str, **kwargs):
        """
        Performs the sql query with passed arguments.

        :param sql_query: sql query to the database
        :param kwargs: arguments of the query
        """
        try:
            cursor = self.connection.cursor()
            cursor.execute(sql_query, kwargs)
            self.connection.commit()
        except Exception as e:
            self.connection.rollback()
            logging.warning(e)

    def add_user(self, user: User):
        """
        Adds a new row of User into the users table.

        :param user: object of informer.user.User
        """
        sql_query = """
                    INSERT INTO users (unique_id, nickname, followers_cnt, following_cnt, heart_cnt, video_cnt)
                    VALUES (%(unique_id)s, %(nickname)s, %(followers_cnt)s, %(following_cnt)s, %(heart_cnt)s, %(video_cnt)s)
                    ON CONFLICT (unique_id) DO UPDATE SET nickname = EXCLUDED.nickname,
                                                          followers_cnt = EXCLUDED.followers_cnt,
                                                          following_cnt = EXCLUDED.following_cnt,
                                                          heart_cnt = EXCLUDED.heart_cnt,
                                                          video_cnt = EXCLUDED.video_cnt
                    """
        self._add_row(sql_query,
                      unique_id=user.unique_id,
                      nickname=user.nickname,
                      followers_cnt=user.followers,
                      following_cnt=user.following,
                      heart_cnt=user.heart_count,
                      video_cnt=user.video_count)

    def add_tiktok(self, tiktok: Tiktok):
        """
        Adds a new row of Tiktok into the tiktoks table.

        :param tiktok: object of informer.tiktok.Tiktok
        """
        sql_query = """
                    INSERT INTO tiktoks (id, user_id, description, time)
                    VALUES (%(id)s, %(unique_id)s, %(description)s, %(time)s)
                    ON CONFLICT (id) DO UPDATE SET user_id = EXCLUDED.user_id,
                                                   description = EXCLUDED.description,
                                                   time = EXCLUDED.time
                    """

        self._add_row(sql_query,
                      id=tiktok.id,
                      unique_id=tiktok.user_id,
                      description=tiktok.desc,
                      time=tiktok.time)

    def get_last_timestamp(self, username: str):
        """
        Returns the timestamp of the last video of $username.

        :param username: the name of a user
        :return: datetime
        """
        sql_query = """
                    SELECT MAX(time)
                    FROM tiktoks
                    WHERE user_id = %(username)s;
                    """
        cursor = self.connection.cursor()
        cursor.execute(sql_query, {'username': username})
        timestamp = cursor.fetchone()[0]

        return timestamp if timestamp else dt.now()

    def update_conversations(self, conversations: dict):
        """
        Method updates a conversation's state in the database.

        :param conversations: a dictionary containing chat_id and conversation state
        """

        # Conversations is dict containing items like: "name_conversation_handler: {chat_id: state}"
        # And it's necessary to swap these values to pass it into the updating data method
        # Now it will be like: "chat_id: {name_conversation_handler: state}"
        _conversations = defaultdict(dict, {})
        for name, id_states in conversations.items():
            for chat_id, state in id_states.items():
                _conversations[chat_id[0]][name] = state
        self.update_data('conversations', _conversations)

    def get_conversations(self) -> dict:
        """
        Method gets conversation states from the database.
        This method returns a dictionary consisting of a tuple and a state of the handler.
        The tuple contains the chat_id. It returns a tuple because of the handler requires it and besides the chat_id,
        the user_id and the message_id may be passed. But now it isn't required and just user_id will be sent.
        This fact may be changed in the ConversationHandler constructor (parameters per_chat, per_user, per_message)

        :return: dictionary
        """

        # It's necessary for the handler that the dictionary will contain the name of the handler like the key
        # Therefore, it must be swapped
        conversations = defaultdict(dict, {})
        for chat_id, names_states in self.get_data('conversations').items():
            for name, state in names_states.items():
                conversations[name][(chat_id,)] = state
        return conversations

    def get_chat_data(self) -> dict:
        """
        Method to getting chat_data from the database.
        Returns dictionary containing the chat_id and a list of arguments.

        :return: dictionary
        """
        return self.get_data("chats")

    def get_user_data(self) -> dict:
        """
        Method to getting user_data from the database.
        Returns dictionary containing the user_id and a list of arguments.

        :return: dictionary
        """
        return self.get_data("users")

    def get_data(self, table_name: str) -> dict:
        """
        Method builds a query to get all data from the table of the database.

        :param table_name: the name of a table
        :return: dictionary containing id and a list of arguments
        """
        with self.connection.cursor() as cur:
            query = sql.SQL("SELECT column_name FROM information_schema.columns WHERE table_name = {};").format(
                sql.Literal(table_name))
            cur.execute(query)

            columns = [column[0] for column in cur.fetchall()]

            if not columns:
                logging.warning("The names of columns from the Chats table weren't received")
                return {}

            # Get all data and create a dictionary
            query = sql.SQL("SELECT * FROM {}").format(sql.Identifier(table_name))
            cur.execute(query)
            data = cur.fetchall()

            if data:
                return {row[0]: {columns[i]: row[i] for i in range(1, len(columns))} for row in data}
            else:
                return {}

    def update_data(self, table_name: str, data: dict):
        """
        Method builds a query to update all data of the table of the database.

        :param table_name: the name of a table
        :param data: dictionary containing ids and a list of arguments with it
        """
        if data:
            # Iterate through all ids
            for id, data_dict in data.items():
                with self.connection.cursor() as cur:
                    # Get all the names of the columns of the table
                    query = sql.SQL("SELECT column_name FROM information_schema.columns WHERE table_name = {};").format(
                        sql.Literal(table_name))
                    cur.execute(query)
                    columns = [column[0] for column in cur.fetchall() if column[0] in data[id] or 'id' in column[0]]

                    # Build a list containing all values of this id
                    values = [id]
                    values.extend(data[id].get(column) for column in columns[1:])

                    if not columns:
                        logging.warning("The names of columns from the {} table weren't received".format(table_name))
                        return {}

                    # Build the SQL-string to use "UPSERT" function
                    setting_columns = list(
                        map(lambda x: sql.SQL("{0} = excluded.{0}").format(sql.Identifier(x)), columns[1:]))

                    # Build a query
                    query = sql.SQL("INSERT INTO {0}({1}) "
                                    "VALUES ({2}) "
                                    "ON CONFLICT ({3}) DO UPDATE SET "
                                    "{4}").format(
                        sql.Identifier(table_name),
                        sql.SQL(',').join(map(sql.Identifier, columns)),
                        sql.SQL(',').join(map(sql.Literal, values)),
                        sql.Identifier(columns[0]),
                        sql.SQL(',').join(setting_columns))
                    cur.execute(query)
            self.connection.commit()

    def update_chat_data(self, chat_data: dict):
        """
        Method updates the data of chats in the database (if it was changed).

        :param chat_data: a new data
        """
        self.update_data('chats', chat_data)

    def update_user_data(self, user_data: dict):
        """
        Method updates the data of users in the database (if it was changed).

        :param user_data:
        :return:
        """
        self.update_data('bot_users', user_data)