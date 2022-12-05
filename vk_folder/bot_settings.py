import vk_api
from vk_api.longpoll import VkLongPoll
import json
from fuzzywuzzy import fuzz

from DB.db import run_db
from vk_folder.people_search import User_vk
from config import token_user, token_community


vk_s = vk_api.VkApi(token=token_community)
session_api = vk_s.get_api()
people_search = User_vk(token_user)


class User:
    def __init__(self, id):
        self.id = id
        self.id_in_db = 0


class Bot:
    # начальные параметры для работы бота
    def __init__(self, token):
        """Инициализация потока"""

        self.token = token
        self.vk_session = vk_api.VkApi(token=token)
        self.longpoll = VkLongPoll(self.vk_session)
        self.vk = self.vk_session.get_api()
        user = User(100)
        self.users = [user]

        self.id_user_bot = ''
        self.id_user = ''


    def sender(self, id, text, key):
        self.vk_session.method('messages.send', {'user_id': id, 'message': text, 'random_id': 0, 'keyboard': key})

    def _get_keyboard(self, buts):
        nb = []
        for i in range(len(buts)):
            nb.append([])
            for k in range(len(buts[i])):
                nb[i].append(None)
        for i in range(len(buts)):
            for k in range(len(buts[i])):
                text = buts[i][k][0]
                color = {'зеленый': 'positive', 'красный': 'negative', 'синий': 'primary'}[buts[i][k][1]]
                nb[i][k] = {
                    "action": {
                        "type": "text",
                        "payload": "{\"button\": \"" + "1" + "\"}",
                        "label": f"{text}"
                    },
                    "color": f"{color}"
                }
        first_keyboard = {'one_time': False, 'buttons': nb, 'inline': False}
        first_keyboard = json.dumps(first_keyboard, ensure_ascii=False).encode('utf-8')
        first_keyboard = str(first_keyboard.decode('utf-8'))
        return first_keyboard

    def clear_key_board(self):
        clear_key = self._get_keyboard([])
        return clear_key

    def menu_find_people_key_board(self):
        menu_find_people = self._get_keyboard([
            [('Добавить в контакты', 'синий')], [('Следующий человек', 'зеленый')],
            [('Больше не показывать', 'красный')]
        ])
        return menu_find_people

    def menu_sex_key_board(self):
        menu_sex = self._get_keyboard([
            [('Девушку', 'синий')], [('Парня', 'зеленый')]
        ])
        return menu_sex

    def menu_check_db_key_board(self):
        menu_check_db = self._get_keyboard([
            [('Следующий контакт', 'зеленый')], [('Удалить контакт', 'красный')], [('Искать людей', 'синий')]
        ])
        return menu_check_db

    def get_match_rating(self, user_vk_id: str, found_persons: list):
        '''Функция анализа текста интересов между пользователем и найденными людьми!'''
        data_user = run_db.search_user_from_db(user_vk_id)
        filtered_persons = []
        for person in found_persons:
            count = 0
            count += fuzz.token_sort_ratio(data_user['books'], person['books'])
            count += fuzz.token_sort_ratio(data_user['activities'], person['activities'])
            count += fuzz.token_sort_ratio(data_user['music'], person['music'])
            count += fuzz.token_sort_ratio(data_user['movies'], person['movies'])
            count += fuzz.token_sort_ratio(data_user['interests'], person['interests'])
            count += fuzz.token_sort_ratio(data_user['games'], person['games'])
            filtered_persons.append([count, person['id']])
        filtered_persons = sorted(filtered_persons, key=lambda x: x[0])
        result = [person[1] for person in filtered_persons]
        result_final = ",".join(map(str, result))
        return result_final


bot = Bot(token_community)