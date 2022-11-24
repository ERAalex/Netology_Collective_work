import sqlalchemy
from psycopg2 import connect
from sqlalchemy.orm import sessionmaker
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
from DB.models import Users, Selected, Gender, Photos, UsersSelected, Banned, create_tables


CONNECT = {
        'drivername': 'postgresql+psycopg2',
        'username': 'postgres',
        'password': 'nazca007',
        'host': 'localhost',
        'port': 5432,
        'database': 'vvvkinder'
        }

class DB:

    def __init__(self, **conn_info):
        self.conn = None
        self.conn_info = conn_info
        DSN = sqlalchemy.engine.url.URL.create(**conn_info)
        self.engine = sqlalchemy.create_engine(DSN)

    def create_database(self):
        self.conn = connect(user=self.conn_info['username'],
                            password=self.conn_info['password'],
                            host=self.conn_info['host'],
                            port=self.conn_info['port'])

        self.conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        self.cur = self.conn.cursor()
        self.cur.execute('CREATE DATABASE ' + f"{self.conn_info['database']}")
        self.cur.close()
        self.conn.close()
    
    def create_table(self):
        create_tables(self.engine)


# Тест запусков
#
# run_db = DB(**CONNECT)
# test = run_db.create_database()
# create = run_db.create_table()
