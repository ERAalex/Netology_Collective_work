import vk_api
import os
from pprint import pprint
from datetime import date
from sqlalchemy import select, insert
from DB.models import Users
from DB.db import DB, CONNECT


vk_token = os.getenv('token')
vk_token_user = os.getenv('token_user')


vk_s = vk_api.VkApi(token=vk_token_user)
session_api = vk_s.get_api()


### надо подать на вход функции id_vk, чтобы понимать кого проверять или у кого собирать данные + поменять user_ids
def get_user_info(vk_id, token):
    '''
    функция, которая собирает данные пользователя чат-бота в словарь
    '''
    vk_s_user = vk_api.VkApi(token=token)
    session_api_us = vk_s_user.get_api()

    user_dict = {}
    user_profile = session_api_us.users.get(user_ids=vk_id, fields='domain, relation, city, sex, bdate, personal, activities, interests, movies, books, music, games, education')

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
        user_dict['languages'] = user_profile[0]['personal']['langs']
    else:
        user_dict['languages'] = ''
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
    if 'zaglushka' in user_profile[0]:
        user_dict['zaglushka'] = user_profile[0]['zaglushka']
    else:
        user_dict['zaglushka'] = 0

    return user_dict

# print(get_user_info())


def put_user_data_in_db(vk_id, token):
    data_user = get_user_info(vk_id, token)
    db_user = DB(**CONNECT)

    db_user.add_user(data_user)

    #
    # done = insert(Users).values(
    #     name=data_user['name'],
    #     last_name=data_user['last_name'],
    #     vk_id=vk_id,
    #     age=data_user['zaglushka'],
    #     relations=data_user['relations'],
    #     b_day=data_user['b_day'],
    #     city=data_user['city'],
    #     language=data_user['languages'],
    #     activities=data_user['activities'],
    #     interests=data_user['interests'],
    #     movies=data_user['movies'],
    #     books=data_user['books'],
    #     games=data_user['games'],
    #     music=data_user['music'],
    #     gender=data_user['gender'])
    # with db_user.engine.connect() as conn:
    #     result = conn.execute(done)
    #     db_user.conn.commit()



# put_user_data_in_db(558826)


#список людей, из которых делать выборку
# wishing_city = input('Введите город поиска: ')
# wishing_gender = input('Введите пол собеседника(м/ж): ')
# wishing_age_from = input('Введите начальный возраст собеседника: ')
# wishing_age_till = input('Введите конечный возраст собеседника: ')
def get_all_available_people():
    people = session_api.users.search(sort=0, blacklisted= 0, is_closed=False, blacklisted_by_me=0, has_photo=1, fields = 'domain, relation, personal, city, about, sex, bdate, birth_year, activities, interests, education, games')
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
# profile_all_info_to_bd = get_all_available_people()
# print(profile_all_info_to_bd)

def show_info_in_bot():
    profile_id_int = session_api.users.get(user_ids=profile_all_info_to_bd['vk_id'])[0]['id']
    profile_photos = session_api.photos.get(owner_id=profile_id_int, count=3, extended=1, album_id='profile')['items']
    for info_about_each_photo in profile_photos:
        pass
    return f'{profile_all_info_to_bd["name"]} {profile_all_info_to_bd["lastname"]}\nhttps://vk.com/{profile_all_info_to_bd["vk_id"]}\n{profile_photos}'

# print(show_info_in_bot())