import random, vk_api, vk_folder
from pprint import pprint
from vk_api.keyboard import VkKeyboard, VkKeyboardColor
from vk_api.utils import get_random_id
from vk_api.bot_longpoll import VkBotLongPoll, VkBotEventType
from vk_api.longpoll import VkLongPoll, VkEventType
import json
import os
from vk_folder.some_frases import iniciate_messages
from DB.database import DB, CONNECT
from DB.models import Users
from vk_folder.people_search import vk_token_user, get_user_info
from sqlalchemy import select, insert

token_user = os.getenv('token_user')

token = os.getenv('token')
vk_session = vk_api.VkApi(token=token)
longpoll = VkLongPoll(vk_session)

vk = vk_session.get_api()

class User:

    def __init__(self, id, mode):
        self.id = id
        self.mode = mode
        self.name = ''
        self.age = -1




def get_keyboard(buts):
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

def sender (id, text, key):
    vk_session.method('messages.send', {'user_id': id, 'message': text, 'random_id': 0, 'keyboard': key})

# пустая клваиатура, чтобы ее передавать.

def clear_key():
    clear_key = get_keyboard(
        []
    )
    return clear_key

# clear_key = get_keyboard(
#     []
# )

menu_find_people = get_keyboard([
    [('Добавить в контакты', 'синий')], [('Следующий человек', 'зеленый')]
])

menu_sex = get_keyboard([
    [('Девушку', 'синий')], [('Парня', 'зеленый')]
])

menu_check_db = get_keyboard([
    [('Следующий контакт', 'зеленый')], [('Удалить контакт', 'красный')], [('Искать людей', 'синий')]
])


user_db = DB(**CONNECT)


user = User(100, 'some')
users = [user]

for event in longpoll.listen():
    if event.type == VkEventType.MESSAGE_NEW:
        if event.to_me:

            id = event.user_id


            # проверяем есть ли такой пользователь в базе
            data = get_user_info(id, token_user)
            user_db.add_user(data)




            msg = event.text.lower()

            if msg in iniciate_messages:
                sender(id, 'hello', clear_key())


            if msg == 'start':
                flag = 0
                for user in users:
                    if user.id == id:
                        flag = 1
                        user.mode = 'start'
                        break
                    if flag == 0:
                        users.append(User(id, 'start'))
                        sender(id, 'Что будем делать? Наберите цифру: \n'
                                   '1- Посмотреть добавленные контакты \n'
                                   '2- Расширенный поиск человека (совпадения по книгам, музыке) \n'
                                   '3- Общий поиск людей \n'
                                   '\n'
                                   '\n'
                                   ' ', clear_key)

            else:
                for user in users:
                    if user.id == id:

                        ##  Логика на Старт меню
                        if user.mode == 'start':
                            if str(msg) == '1':
                                sender(id, 'Ваши контакты: Функция, выводим людей из БД \n ', menu_check_db)
                                user.mode = 'db_check'

                            if str(msg) == '3':
                                sender(id, 'Для общего поиска людей выберите кого ищем \n ', menu_sex)
                                user.mode = 'menu_sex'
                                print(user.mode)


                        ##  Логика на 1 пункт
                        elif user.mode == 'db_check':
                            if msg == 'следующий контакт':
                                sender(id, 'Выводим следующий контакт, Функция ДБ \n ', menu_find_people)
                                user.mode = 'db_check'

                            if msg == 'удалить контакт':
                                sender(id, 'Удаляем предыдущий выданный контакты, Функция ДБ \n ', menu_find_people)
                                user.mode = 'db_check'



                        ##  Логика на 3 пункт

                        elif user.mode == 'menu_sex':
                            if msg == 'девушку':
                                sender(id, 'Выводим девушек, тут идет функция поиска (Девушек) '
                                           'и вывода \n ', menu_find_people)
                                user.mode = 'girl_find'

                            if msg == 'парня':
                                sender(id, 'Выводим парней, тут идет функция поиска (Парней) '
                                           'и вывода \n ', menu_find_people)
                                user.mode = 'boy_find'


                        if user.mode == 'girl_find':
                            if msg == 'следующий человек':
                                sender(id, 'Продолжаем вывод, тут идет функция поиска (Девушек) '
                                           'и вывода \n ', menu_find_people)
                                user.mode = 'girl_find'

                            if msg == 'добавить в контакты':
                                sender(id, 'Добавляем в контакты предыдущий вывод, тут идет функция БД '
                                           'и вывода \n ', menu_find_people)
                                user.mode = 'girl_find'


                        if user.mode == 'boy_find':
                            if msg == 'следующий человек':
                                sender(id, 'Продолжаем вывод, тут идет функция поиска (Парней) '
                                           'и вывода \n ', menu_find_people)
                                user.mode = 'boy_find'

                            if msg == 'добавить в контакты':
                                sender(id, 'Добавляем в контакты предыдущий вывод, тут идет функция БД '
                                           'и вывода \n ', menu_find_people)
                                user.mode = 'boy_find'


                        if user.mode == 'db_check':
                            sender(id, 'Смотрим базу тест 2 \n ', menu_check_db)
                            user.mode = 'db_check'











#################
#
#
# for event in longpoll.listen():
#     if event.type == VkEventType.MESSAGE_NEW:
#         if event.to_me:
#
#             id = event.user_id
#             msg = event.text.lower()
#
#             if msg in iniciate_messages:
#                 sender(id, 'hello', clear_key)
#
#
#             if msg == 'start':
#                 flag = 0
#                 for user in users:
#                     if user.id == id:
#                         flag = 1
#                         user.mode = 'start'
#                         break
#                     if flag == 0:
#                         users.append(User(id, 'start'))
#                         sender(id, 'Что будем делать? Наберите цифру: \n'
#                                    '1- Посмотреть добавленные контакты \n'
#                                    '2- Расширенный поиск человека (город, пол, книги, музыка) \n'
#                                    '3- Общий поиск людей \n'
#                                    '\n'
#                                    '\n'
#                                    ' ', clear_key)
#                     elif flag == 1:
#                         for user in users:
#                             if user.id == id:
#                                 if not(user.mode in ['reg1', 'reg2']):
#                                     sender(id, 'Зарегестрируйтесь в боте. \nВведите свое имя: ', clear_key)
#
#             else:
#                 for user in users:
#                     if user.id == id:
#                         #
#                         if user.mode == 'start':
#                             if str(msg) == '1':
#                                 sender(id, 'Ваши контакты: \n ', menu_check_db)
#                                 user.mode = '1_decision_parametrs'
#
#                         elif user.mode == 'reg2':
#                             try:
#                                 user.age = int(msg)
#                                 sender(id, 'Вы успешно зарегестрировались!', menu_key)
#                                 user.mode = 'menu'
#                             except:
#                                 sender(id, 'Значение возраста не подходит!', clear_key)
#
#
