import sqlalchemy
from psycopg2 import extras, connect
from sqlalchemy.orm import sessionmaker
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
from pprint import pprint

from DB.models import Users, Selected, Photos, UsersSelected, Banned, DeletedSelected, create_tables, User_session


CONNECT = {
        'drivername': 'postgresql+psycopg2',
        'username': 'postgres',
        'password': 'nazca007', # поставить свой пароль от postgres
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
        '''создание новой БД'''
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
        '''запуск создания всех таблиц'''
        create_tables(self.engine)


#########################################

    # Поместить в файл db.py
    def add_user_choise_ids(self, user_id, ids):
        '''добавление айди выбранных страниц для пользователя'''
        Session = sessionmaker(bind=self.engine)
        db_session = Session()
        add_query = db_session.query(User_session).get(user_id)
        add_query.ids_found = ids
        db_session.add(add_query)
        db_session.commit()
        db_session.close()



    def add_user_choise_age(self, user_id, age):
        '''добавление выбранного возраста для поиска'''
        Session = sessionmaker(bind=self.engine)
        db_session = Session()
        add_query = db_session.query(User_session).get(user_id)
        add_query.age_find = age
        db_session.add(add_query)
        db_session.commit()
        db_session.close()


    def add_user_choise_city(self, user_id, city):
        '''добавление выбранного для поиска города пользователя'''
        Session = sessionmaker(bind=self.engine)
        db_session = Session()
        add_query = db_session.query(User_session).get(user_id)
        add_query.city_find = city
        db_session.add(add_query)
        db_session.commit()
        db_session.close()


    def get_users_choise_age(self, user_id):
        '''получить список с информацией, которую польщователь вводил для поиска в сессии(город возраст)'''
        Session = sessionmaker(bind=self.engine)
        db_session = Session()
        query = db_session.query(User_session).filter(User_session.id_user == user_id).all()
        db_session.close()
        for item in query:
            return item.age_find


    def get_users_choise_ids(self, user_id):
        '''получить список с информацией, которую польщователь вводил для поиска в сессии(vk_id людей)'''
        Session = sessionmaker(bind=self.engine)
        db_session = Session()
        query = db_session.query(User_session).filter(User_session.id_user == user_id).all()
        db_session.close()
        for item in query:
            return item.ids_found


    def get_users_choise_city(self, user_id):
        '''получить список с информацией, которую польщователь вводил для поиска в сессии(город)'''
        Session = sessionmaker(bind=self.engine)
        db_session = Session()
        query = db_session.query(User_session).filter(User_session.id_user == user_id).all()
        db_session.close()
        for item in query:
            return item.city_find


####################################### CONSTANT INTERACTION WITH DATABASE #######################################

    def add_user(self, user_info: dict):
        '''добавление нового пользователя в БД'''
        Session = sessionmaker(bind=self.engine)
        db_session = Session()
        # проверка на нахождение пользователя в базе
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
        '''добавление пользователей в БД'''
        Session = sessionmaker(bind=self.engine)
        db_session = Session()
        chek_query = db_session.query(Selected).filter(Selected.vk_id == selected_info['vk_id']).all()
        if not chek_query:
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
            # получение id только что внесенной записи выбранного пользователя
            db_session.flush()
            id_query = add_query.id
            # добавление фотографий выбранного пользователя в таблицу Photos
            selected_photos = []
            for photo in selected_info['photo']:
                selected_photos.append(Photos(photo_id=photo, id_selected=id_query))
            db_session.add_all(selected_photos)
            db_session.commit()
            db_session.close()


    def mark_users_selected(self, user_id, selected_id):
        '''добавление связи пользователя с его выбранным пользоваетелем'''
        Session = sessionmaker(bind=self.engine)
        db_session = Session()
        add_query = UsersSelected(id_user=user_id, id_selected=selected_id)
        db_session.add(add_query)
        db_session.commit()
        db_session.close()


    def find_using_users_selected(self, user_id):
        '''у нас есть id пользователя бота, надо найти по нему всех релайтед людей из UsersSelected'''
        Session = sessionmaker(bind=self.engine)
        db_session = Session()
        query = db_session.query(UsersSelected).filter(UsersSelected.id_user == user_id).all()
        db_session.close()
        result = []
        for item in query:
            result.append(item.id_selected)
        return result

    
    def add_banned(self, user_id, selected_vk_id):
        '''добавление в бан лист'''
        Session = sessionmaker(bind=self.engine)
        db_session = Session()
        add_query = Banned(id_user=user_id, banned_vk_id=selected_vk_id)
        db_session.add(add_query)
        db_session.commit()
        db_session.close()


    def get_all_vk_id_of_banned(self, user_id):
        '''вывести список всех забаненных пользователей, чтобы потом проверять по ним и не выводить'''
        Session = sessionmaker(bind=self.engine)
        db_session = Session()
        query = db_session.query(Banned).filter(Banned.id_user == user_id).all()
        db_session.close()
        result = []
        for item in query:
            result.append(item.banned_vk_id)
        return result


    def get_id_deleted_selected(self, user_id):
        '''получить айди удаленной анкеты, чтобы не показывать её пользователю '''
        Session = sessionmaker(bind=self.engine)
        db_session = Session()
        query = db_session.query(DeletedSelected).filter(DeletedSelected.id_user == user_id).all()
        db_session.close()
        result = []
        for item in query:
            result.append(item.id_selected)
        return result


    def mark_deleted_from_selected(self, user_id, selected_id):
        '''отметка пользователя удаленным из БД (не показывать потзователю аккаунты в флагом deleted)'''
        Session = sessionmaker(bind=self.engine)
        db_session = Session()
        add_query = DeletedSelected(id_user=user_id, id_selected=selected_id)
        db_session.add(add_query)
        db_session.commit()
        db_session.close()


    def search_user_from_db(self, user_vk_id):
        '''получения словаря с информацией о пользователе из БД'''
        Session = sessionmaker(bind=self.engine)
        session = Session()
        query = session.query(Users).filter(Users.vk_id == user_vk_id).all()
        session.close()
        result = {}
        for column in query:
            ###### Дописал id он нам нужен в выводе для поиска по UserRelated
            result = {'id': column.id,
                      'name': column.name,
                      'last_name': column.last_name,
                      'vk_id': column.vk_id,
                      'age': column.age,
                      'relations': column.relations,
                      'b_day': column.b_day,
                      'city': column.city,
                      'language': column.language,
                      'activities': column.activities, 
                      'interests': column.interests,
                      'movies': column.movies,
                      'books': column.books,
                      'games': column.games, 
                      'music': column.music, 
                      'gender': column.gender
                      }
        return result


    def search_selected_from_db_using_id(self, id):
        '''получения словаря с информацией о выбранном пользователе из БД'''
        Session = sessionmaker(bind=self.engine)
        session = Session()
        query = session.query(Selected).filter(Selected.id == id).all()
        session.close()
        result = {}
        for column in query:
            result = {'id': column.id,
                      'name': column.name,
                      'last_name': column.last_name,
                      'vk_id': column.vk_id,
                      'age': column.age,
                      'relations': column.relations,
                      'b_day': column.b_day,
                      'city': column.city,
                      'language': column.language,
                      'activities': column.activities,
                      'interests': column.interests,
                      'movies': column.movies,
                      'books': column.books,
                      'games': column.games,
                      'music': column.music,
                      'gender': column.gender
                      }
        return result


    def search_selected_from_db(self, selected_vk_id):
        '''получения словаря с информацией о выбранном пользователе из БД'''
        Session = sessionmaker(bind=self.engine)
        session = Session()
        query = session.query(Selected).filter(Selected.vk_id == selected_vk_id).all()
        session.close()
        result = {}
        for column in query:
            result = {'name': column.name,
                      'id': column.id,
                      'last_name': column.last_name,
                      'vk_id': column.vk_id,
                      'age': column.age,
                      'relations': column.relations,
                      'b_day': column.b_day,
                      'city': column.city,
                      'language': column.language,
                      'activities': column.activities, 
                      'interests': column.interests,
                      'movies': column.movies,
                      'books': column.books,
                      'games': column.games, 
                      'music': column.music, 
                      'gender': column.gender
                      }
        return result
        
####################################### SESSION INTERACTION WITH DATABASE #######################################

    def get_step_ids_session(self, user_id):
        '''получить номер шага для показа пользователей сессии по айди из списка'''
        Session = sessionmaker(bind=self.engine)
        db_session = Session()
        query = db_session.query(User_session).filter(User_session.id_user == user_id).all()
        db_session.close()
        for item in query:
            return item.step


    def update_step_session(self, user_id, next_step):
        '''обновить шаг для выдачи следующего айди из найденных в сессии'''
        Session = sessionmaker(bind=self.engine)
        db_session = Session()
        add_query = db_session.query(User_session).get(user_id)
        add_query.step = next_step
        db_session.add(add_query)
        db_session.commit()
        db_session.close()

    
    def get_users_choise(self, user_id):
        '''получить список с информацией, которую польщователь вводил для поиска в сессии(город возраст)'''
        Session = sessionmaker(bind=self.engine)
        db_session = Session()
        query = db_session.query(User_session).filter(User_session.id_user == user_id).all()
        db_session.close()
        result = []
        for item in query:
            result.append(item.age_find)
            result.append(item.ids_found)


    def add_user_mode(self, user_id, mode):
        '''добавление режима юзера'''
        Session = sessionmaker(bind=self.engine)
        db_session = Session()
        add_query = User_session(id=user_id, id_user=user_id, mode_name=mode)
        db_session.add(add_query)
        db_session.commit()
        db_session.close()


    def get_user_mode(self, user_id):
        '''получить режим пользователя из базы'''
        Session = sessionmaker(bind=self.engine)
        db_session = Session()
        query = db_session.query(User_session).filter(User_session.id_user == user_id).all()
        db_session.close()
        for item in query:
            return item.mode_name


    def update_user_mode(self, user_id, mode):
        '''обновить режим юзера, когда он поменяется'''
        Session = sessionmaker(bind=self.engine)
        db_session = Session()
        add_query = db_session.query(User_session).get(user_id)
        add_query.mode_name = mode
        db_session.add(add_query)
        db_session.commit()
        db_session.close()


    def delete_user_mode(self, user_id):
        '''удалить юзера из таблицы режимов'''
        Session = sessionmaker(bind=self.engine)
        db_session = Session()
        del_query = db_session.query(User_session).filter(User_session.id_user == user_id).one()
        db_session.delete(del_query)
        db_session.commit()
        db_session.close()
    

# не трогать ниже строчку, я ею пользуюсь в bot
run_db = DB(**CONNECT)

# print(run_db.get_all_vk_id_of_banned(12))

# test = run_db.create_database()
# create = run_db.create_table()
#
# test2 = run_db.add_user(test_user)
#
# test3 = run_db.add_selected(test_selected)

# run_db.mark_users_selected(12, 2)


# run_db.find_using_users_selected(12)

# test_user_info = run_db.search_user_from_db('id459484548495')
# print(test_user_info)