import psycopg2


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

        :return:
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
