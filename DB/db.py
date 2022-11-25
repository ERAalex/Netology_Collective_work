import sqlalchemy
from psycopg2 import connect
######
import psycopg2
import psycopg2.extras
######
from sqlalchemy.orm import sessionmaker
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
from DB.models import Users, Selected, Photos, UsersSelected, Banned, create_tables

from DB.models import Users, Selected, Photos, UsersSelected, Banned, create_tables




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
        ######
        # Нужен коннектор и кур. + сессия, для запросов sqlalchemy в боте + пришлось приписать пару библиотек
        self.conn = psycopg2.connect(dbname="vvvkinder", user="postgres", password="nazca007", host="localhost")
        self.cur = self.conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
        Session = sessionmaker(bind=self.engine)
        self.session = Session()
        ######

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

    
    def add_user(self, user_info: dict):
        Session = sessionmaker(bind=self.engine)
        db_session = Session()
        chek_query = db_session.query(Users).filter(Users.vk_id == user_info['vk_id']).all()
        if not chek_query:
            add_query = Users(name=user_info['name'],
                              last_name=user_info['last_name'],
                              vk_id=user_info['vk_id'],
                              age=user_info['age'], 
                              relations=user_info['relations'],
                              b_day=user_info['b_day'],
                              city=user_info['city'],
                              language=user_info['language'],
                              activities=user_info['activities'],
                              interests=user_info['interests'],
                              movies=user_info['movies'],
                              books=user_info['books'],
                              games=user_info['games'],
                              music=user_info['music'],
                              gender=user_info['gender']
                              )
            db_session.add(add_query)
            db_session.commit()
            db_session.close()

    def add_selected(self, selected_info: dict):
        Session = sessionmaker(bind=self.engine)
        db_session = Session()
        add_query = Selected(name=selected_info['name'],
                             last_name=selected_info['last_name'],
                             vk_id=selected_info['vk_id'],
                             age=selected_info['age'], 
                             relations=selected_info['relations'],
                             b_day=selected_info['b_day'],
                             city=selected_info['city'],
                             language=selected_info['language'],
                             activities=selected_info['activities'],
                             interests=selected_info['interests'],
                             movies=selected_info['movies'],
                             books=selected_info['books'],
                             games=selected_info['games'],
                             music=selected_info['music'],
                             gender=selected_info['gender']
                             )
        db_session.add(add_query)
        db_session.flush()
        id_query = add_query.id
        selected_photos = []
        for photo in selected_info['photo']:
            selected_photos.append(Photos(photo_id=photo, id_selected=id_query))
        db_session.add_all(selected_photos)
        db_session.commit()
        db_session.close()


test_user = {
    'name': 'Sergey',
    'last_name': 'Niceone',
    'vk_id': 'id459484548495',
    'age': 33,
    'relations': 'married',
    'b_day': '09.09.1989',
    'city': 'Moscow',
    'language': 'English',
    'activities': 'noone',
    'interests': 'nouse',
    'movies': 'psy',
    'books': 'Martin Eden',
    'games': 'The Witcher 3',
    'music': 'melodic',
    'gender': 'male',
}

test_selected = {
    'name': 'Sergey',
    'last_name': 'Niceone',
    'vk_id': 'id459484548495',
    'age': 33,
    'relations': 'married',
    'b_day': '09.09.1989',
    'city': 'Moscow',
    'language': 'English',
    'activities': 'noone',
    'interests': 'nouse',
    'movies': 'psy',
    'books': 'Martin Eden',
    'games': 'The Witcher 3',
    'music': 'melodic',
    'gender': 'male',
    'photo': ['6465465165', '65465161651', '65465151651']
}


# Тест запусков

run_db = DB(**CONNECT)
# test = run_db.create_database()
# create = run_db.create_table()

# test2 = run_db.add_user(test_user)
#
# test3 = run_db.add_selected(test_selected)