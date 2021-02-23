import psycopg2
import logging
from tiktokinformer.informer.user import User
from tiktokinformer.informer.tiktok import Tiktok

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
        sql_query = """
                    CREATE TABLE IF NOT EXISTS users
                    (
                        unique_id TEXT PRIMARY KEY,
                        nickname TEXT NOT NULL, 
                        followers_cnt INTEGER NOT NULL,
                        following_cnt INTEGER NOT NULL,
                        heart_cnt INTEGER NOT NULL,
                        video_cnt INTEGER NOT NULL
                    );
                    
                    CREATE TABLE IF NOT EXISTS tiktoks
                    (
                        id BIGINT PRIMARY KEY,
                        user_id TEXT,
                        description TEXT NOT NULL,
                        time TIMESTAMP NOT NULL,
                    
                        CONSTRAINT fk_users FOREIGN KEY (user_id)
                            REFERENCES users (unique_id)
                            ON DELETE CASCADE
                            ON UPDATE CASCADE
                    );
                    """
        cursor = self.connection.cursor()
        cursor.execute(sql_query)
        self.connection.commit()

    @property
    def connection(self):
        if self._connection is None:
            raise ValueError("Connection to the database wasn't made")
        return self._connection

    def add_user(self, user: User):
        """
        Adds a new row of User into the users table.

        :param user: object of informer.user.User
        """
        sql_query = """
                    INSERT INTO users (unique_id, nickname, followers_cnt, following_cnt, heart_cnt, video_cnt)
                    VALUES (%(unique_id)s, %(nickname)s, %(followers_cnt)s, %(following_cnt)s, %(heart_cnt)s, %(video_cnt)s)
                    """
        cursor = self.connection.cursor()
        try: 
            cursor.execute(sql_query, {
                'unique_id': user.unique_id,
                'nickname': user.nickname,
                'followers_cnt': user.followers,
                'following_cnt': user.following,
                'heart_cnt': user.heart_count,
                'video_cnt': user.video_count
            })
            self.connection.commit()
        except psycopg2.errors.UniqueViolation:
            logging.warning('Attempt of inserting duplicate')
