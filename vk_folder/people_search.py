import vk_api
import os
from pprint import pprint
import datetime
from sqlalchemy import select, insert
from random import randint
from DB.models import Users
from DB.db import DB, CONNECT


class User_vk:

    def __init__(self, vk_s, session_api, vk_token):
        self.vk_token = os.getenv('token') #токен владельца сообщества с чат-ботом
        self.vk_s = vk_api.VkApi(token=self.vk_token) #основной класс библиотеки vk_api
        self.session_api = self.vk_s.get_api() #подключение к api

    def get_user_info(self, vk_id: int, token: str):
        '''
        функция, которая собирает данные пользователя чат-бота в словарь
        '''
        user_dict = {}
        user_profile = self.session_api.users.get(user_ids=self.vk_id,
                                                fields='domain, relation, city, sex, bdate, personal, activities, interests, movies, books, music, games, education')

        user_dict['vk_id'] = user_profile[0]['domain']
        user_dict['name'] = user_profile[0]['first_name']
        user_dict['last_name'] = user_profile[0]['last_name']
        user_dict['relations'] = user_profile[0]['relation']
        # 1 — не женат / не замужем;
        # 2 — есть друг / есть подруга;
        # 3 — помолвлен / помолвлена;
        # 4 — женат / замужем;
        # 5 — всё сложно;
        # 6 — в активном поиске;
        # 7 — влюблён / влюблена;
        # 8 — в гражданском браке;
        # 0 — не указано.

        if user_profile[0]['sex'] == 1:
            user_dict['gender'] = 'женщина'
        else:
            user_dict['gender'] = 'мужчина'
        if 'bdate' in user_profile[0]:
            user_dict['b_day'] = user_profile[0]['bdate']
        else:
            user_dict['b_day'] = ''
        if 'city' in user_profile[0]:
            user_dict['city'] = user_profile[0]['city']['title']
        else:
            user_dict['city'] = ''
        if 'langs' in user_profile[0]['personal']:
            user_dict['language'] = user_profile[0]['personal']['langs']
        else:
            user_dict['language'] = ''
        if 'activities' in user_profile[0]:
            user_dict['activities'] = user_profile[0]['activities']
        else:
            user_dict['activities'] = ''
        if 'interests' in user_profile[0]:
            user_dict['interests'] = user_profile[0]['interests']
        else:
            user_dict['interests'] = ''
        if 'movies' in user_profile[0]:
            user_dict['movies'] = user_profile[0]['movies']
        else:
            user_dict['movies'] = ''
        if 'books' in user_profile[0]:
            user_dict['books'] = user_profile[0]['books']
        else:
            user_dict['books'] = ''
        if 'music' in user_profile[0]:
            user_dict['music'] = user_profile[0]['music']
        else:
            user_dict['music'] = ''
        if 'games' in user_profile[0]:
            user_dict['games'] = user_profile[0]['games']
        else:
            user_dict['games'] = ''
        if 'age' in user_profile[0]:
            user_dict['age'] = user_profile[0]['age']
        else:
            user_dict['age'] = 0

        return user_dict



#список людей, из которых делать выборку
# wishing_city = input('Введите город поиска: ')
# wishing_gender = input('Введите пол собеседника(м/ж): ')
# wishing_age_from = input('Введите начальный возраст собеседника: ')
# wishing_age_till = input('Введите конечный возраст собеседника: ')
class vk_choice:
    def __init__(self, vk_token_user, vk_token, vk_s, vk_u, session_api_user, session_api):
        self.vk_token_user = os.getenv('token_user')
        self.vk_token = os.getenv('token')
        self.vk_s = vk_api.VkApi(token=self.vk_token)
        self.vk_u = vk_api.VkApi(token=self.vk_token_user)
        self.session_api_user = self.vk_u.get_api()
        self.session_api = self.vk_s.get_api()

    def get_all_available_people(self):
        people = self.session_api_user.users.search(sort=0, blacklisted= 0, is_closed=False, blacklisted_by_me=0, has_photo=1, fields = 'domain, relation, personal, city, about, sex, bdate, birth_year, activities, interests, education, games')
        people_dict = {}
        # Список людей не в блэклисте, у которых есть фото,
        for el in people['items']:
            if el['sex'] == 1:
                people_dict['gender'] = 'ж'
            else:
                people_dict['gender'] = 'м'
            if 'city' in el:
                people_dict['city'] = el['city']['title']
            else:
                people_dict['city'] = ''
            if 'langs' in el:
                people_dict['languages'] = el['personal']['langs']
            else:
                people_dict['languages'] = ''

            people_dict['name'] = el['first_name']
            people_dict['lastname'] = el['last_name']
            people_dict['vk_id'] = el["domain"]
            if 'relation' in el:
                people_dict['relationship'] = el['relation']
            else:
                people_dict['relationship'] = 0

            # 1 — не женат / не замужем;
            # 2 — есть друг / есть подруга;
            # 3 — помолвлен / помолвлена;
            # 4 — женат / замужем;
            # 5 — всё сложно;
            # 6 — в активном поиске;
            # 7 — влюблён / влюблена;
            # 8 — в гражданском браке;
            # 0 — не указано.

            if 'bdate' in el:
                people_dict['b_day'] = el['bdate']
            else:
                people_dict['b_day'] = ''
            if 'activities' in el:
                people_dict['activities'] = el['activities']
            else:
                people_dict['activities'] = ''
            if 'interests' in el:
                people_dict['interests'] = el['interests']
            else:
                people_dict['interests'] = ''
            if 'games' in el:
                people_dict['games'] = el['games']
            else:
                people_dict['games'] = ''
            return people_dict
    profile_all_info_to_bd = get_all_available_people()

    def send_info_in_bot(self):
        '''
        функция, которая выводит в чат с ботом информацию о пользователе из функции поиска в нужном формате

        '''
        name = profile_all_info_to_bd['name']
        surname = profile_all_info_to_bd['lastname']
        profile_id_int = self.session_api.users.get(user_ids=profile_all_info_to_bd['vk_id'])[0]['id']
        profile_photos = self.session_api_user.photos.get(owner_id=profile_id_int, extended=1, album_id='profile')['items']
        most_liked = sorted(profile_photos, key = lambda likes: likes['likes']['count'], reverse=True)[:3]
        all_photo_attachments = []
        for el in most_liked:
            all_photo_attachments.append(f'photo{profile_id_int}_{el["id"]}')
        send_info = self.session_api.messages.send(user_id = f'{self.vk_id}', random_id=randint(0, 1000), message=f'{name} {surname}\nhttps://vk.com/{profile_all_info_to_bd["vk_id"]}', attachment=f'{all_photo_attachments[0]},{all_photo_attachments[1]},{all_photo_attachments[2]}')
        return send_info

