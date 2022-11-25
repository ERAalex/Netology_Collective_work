import random, vk_api, vk
from vk_api.keyboard import VkKeyboardColor, VkKeyboard
from vk_api.utils import get_random_id
from vk_api.longpoll import VkLongPoll, VkEventType
import json
from vk_folder.some_frases import iniciate_messages
from db_mongo import find_document, series_collection, insert_document
import os

from DB.db import DB, CONNECT
from DB.models import Users
from vk_folder.people_search import get_user_info





token_user = os.getenv('token_user')
vk_token = os.getenv('token')
vk_s = vk_api.VkApi(token=vk_token)
session_api = vk_s.get_api()


class User:
    def __init__(self, id, mode):
        self.id = id
        self.mode = mode
        self.name = ''
        self.age = -1





class Bot:

    # начальные параметры для работы бота
    def __init__(self, token):
        self.token = token
        self.vk_session = vk_api.VkApi(token=token)
        self.longpoll = VkLongPoll(self.vk_session)
        self.vk = self.vk_session.get_api()
        user = User(100, 'some')
        self.users = [user]


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
            [('Добавить в контакты', 'синий')], [('Следующий человек', 'зеленый')]
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


#cамая главная часть, работа бота
    def start_run(self):
        for event in self.longpoll.listen():
            if event.type == VkEventType.MESSAGE_NEW:
                if event.to_me:

                    id = event.user_id

                    # проверяем есть ли такой пользователь в базе
                    user_db = DB(**CONNECT)

                    data = get_user_info(id, token_user)
                    user_db.add_user(data)

                    msg = event.text.lower()

                    if msg in iniciate_messages:

                        self.sender(id, 'hello', self.clear_key_board())


                    if msg == 'start':
                        flag = 0
                        for user in self.users:
                            if user.id == id:
                                flag = 1
                                user.mode = 'start'
                                break
                            if flag == 0:
                                self.users.append(User(id, 'start'))
                                self.sender(id, 'Что будем делать? Наберите цифру: \n'
                                           '1- Посмотреть добавленные контакты \n'
                                           '2- Расширенный поиск человека (совпадения по книгам, музыке) \n'
                                           '3- Общий поиск людей \n'
                                           '\n'
                                           '\n'
                                           ' ', self.clear_key_board())

                    else:
                        for user in self.users:
                            if user.id == id:

                                ##  Логика на Старт меню
                                if user.mode == 'start':
                                    if str(msg) == '1':
                                        self.sender(id, 'Ваши контакты: Функция, выводим людей из БД \n ',
                                               self.menu_check_db_key_board())
                                        user.mode = 'db_check'

                                    if str(msg) == '3':
                                        self.sender(id, 'Для общего поиска людей выберите кого ищем \n ',
                                               self.menu_sex_key_board())
                                        user.mode = 'menu_sex'
                                        print(user.mode)


                                ##  Логика на 1 пункт
                                elif user.mode == 'db_check':
                                    if msg == 'следующий контакт':
                                        self.sender(id, 'Выводим следующий контакт, Функция ДБ \n ',
                                                    self.menu_check_db_key_board())
                                        user.mode = 'db_check'

                                    if msg == 'удалить контакт':
                                        self.sender(id, 'Удаляем предыдущий выданный контакты, Функция ДБ \n ',
                                               self.menu_check_db_key_board())
                                        user.mode = 'db_check'



                                ##  Логика на 3 пункт

                                elif user.mode == 'menu_sex':
                                    if msg == 'девушку':
                                        self.sender(id, 'Выводим девушек, тут идет функция поиска (Девушек) '
                                                   'и вывода \n ', self.menu_find_people_key_board())
                                        user.mode = 'girl_find'

                                    if msg == 'парня':
                                        self.sender(id, 'Выводим парней, тут идет функция поиска (Парней) '
                                                   'и вывода \n ', self.menu_find_people_key_board())
                                        user.mode = 'boy_find'

                                if user.mode == 'girl_find':
                                    if msg == 'следующий человек':
                                        self.sender(id, 'Продолжаем вывод, тут идет функция поиска (Девушек) '
                                                   'и вывода \n ', self.menu_find_people_key_board())
                                        user.mode = 'girl_find'

                                    if msg == 'добавить в контакты':
                                        self.sender(id, 'Добавляем в контакты предыдущий вывод, тут идет функция БД '
                                                   'и вывода \n ', self.menu_find_people_key_board())
                                        user.mode = 'girl_find'

                                if user.mode == 'boy_find':
                                    if msg == 'следующий человек':
                                        self.sender(id, 'Продолжаем вывод, тут идет функция поиска (Парней) '
                                                   'и вывода \n ', self.menu_find_people_key_board())
                                        user.mode = 'boy_find'

                                    if msg == 'добавить в контакты':
                                        self.sender(id, 'Добавляем в контакты предыдущий вывод, тут идет функция БД '
                                                   'и вывода \n ', self.menu_find_people_key_board())
                                        user.mode = 'boy_find'

                                if user.mode == 'db_check':
                                    self.sender(id, 'Смотрим базу тест 2 \n ', self.menu_check_db_key_board())
                                    user.mode = 'db_check'
                    #



bot_start = Bot(vk_token)
bot_start.start_run()


