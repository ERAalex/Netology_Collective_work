import vk_api
from vk_api import VkTools
import vk_folder
from pprint import pprint
from random import randint
import requests
import json
from time import sleep
from pprint import pprint
import os

from pymongo import MongoClient
# from db_mongo import client, db, insert_document, update_document, series_collection


################______Работа с ВК______################

# токен с доступом к стене, для функции со скачиванием Profiles
vk_token = os.getenv('token')

vk_s = vk_api.VkApi(token=vk_token)
session_api = vk_s.get_api()



def find_data_person(user_id):
    dicc_data = {}
    user_get = session_api.users.get(user_ids=user_id, fields='city, sex, books, bdate, music, relation')

    dicc_data['user_name'] = user_get[0]['first_name']
    dicc_data['user_lastname'] = user_get[0]['last_name']
    dicc_data['user_bdate'] = user_get[0]['bdate']
    dicc_data['user_sex'] = user_get[0]['sex']
    dicc_data['user_relation'] = user_get[0]['relation']
    dicc_data['user_music'] = user_get[0]['music']
    dicc_data['user_books'] = user_get[0]['books']
    dicc_data['user_city'] = user_get[0]['city']['title']

    return dicc_data






list_of_choice = {}

def choice_persons():
    rs = VkTools(session_api).get_all(
        method='users.search',
        max_count='400',
        values={
# https: // dev.vk_folder.com / reference / objects / user
            'age_from': 23,
            'hometown': 'Кировск',
            'age_to': 28,
            'sex': 1,
            'fields': 'domain',
            'relation': 1,
            'is_closed': 'False',
        },
    )

    # посмотреть конкретно людей, номер человека в списке
    # pprint(rs['items'][1])
    # выбираем рандомно 3 девушек(парней). Тут будет выбор от пользователя, сколько показать
    total_persons = int(rs['count'])
    for x in range(4):
        choice = randint(0, total_persons - 1)
        list_of_choice[rs['items'][choice]['id']] = rs['items'][choice]['first_name']+'_'+rs['items'][choice]['last_name']

    return list_of_choice




def _preparing_dic(all_data):
    finish_dic_all = {}
    count = 0

    try:
        for items in all_data['response']['items']:
            dict_testing = (items['sizes'][-1])
            if items['likes']['count'] not in finish_dic_all.keys():
                finish_dic_all[str(items['id']) + f'_{str(count)}'] = [dict_testing['url'], dict_testing['type']]
                count += 1
            else:
                finish_dic_all[items['date']] = [dict_testing['url'], dict_testing['type']]
                count += 1
    except:
        print('аккаунт закрыт')
    return finish_dic_all


# доступ к фото Profile
def get_foto_profile():
    for key_1, value in list_of_choice.items():
        acc_activate = "Петя"
        name_person = value
        profile_api_foto = requests.get('https://api.vk.com/method/photos.get',
                                        params={
                                            'owner_id': key_1,
                                            'album_id': 'profile',
                                            'access_token': vk_token,
                                            'rev': 0,
                                            'extended': 1,
                                            'photo_sizes': 0,
                                            'count': 3,
                                            'v': '5.131',
                                        })
        sleep(2)
        all_data = profile_api_foto.json()
        result = _preparing_dic(all_data)

        pprint(f'Имя девушки: {name_person}, ее id: id{key_1} ee лучшие фото: ')
        for key, value in result.items():
            print(value)

        #### Если пользователю нравится сразу добавляем в базу.
        decision = input('Добавить в список интересных друзей? 1/2: ')
        if decision == '1':
            id_key = "id" + str(key_1)

            # все работает, добавляет во вложенный список девушку, надо только связать с id пользователя
            series_collection.update_one(
                {"name": "Митя"},
                {"$addToSet": {"girls": {
                        "user_id": f"{id_key}",
                        "user": f"{name_person}",
                        "age": 41

                }}}, upsert=True)
        else:
            pass
        print('_____________\n')




choice_persons()
girls_list = get_foto_profile()


