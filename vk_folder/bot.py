import random, vk_api, vk
from vk_api.keyboard import VkKeyboardColor, VkKeyboard
from vk_api.utils import get_random_id
from vk_api.longpoll import VkLongPoll, VkEventType
import json
from vk_folder.some_frases import iniciate_messages
from db_mongo import find_document, series_collection, insert_document
import os

from DB.db import DB, CONNECT, run_db
from DB.models import Users

from vk_folder.people_search import User_vk, some_choice





token_user = os.getenv('token_user')
vk_token = os.getenv('token')
vk_s = vk_api.VkApi(token=vk_token)
session_api = vk_s.get_api()


people_search = User_vk(token_user)



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
        # нам нужен для просмотра людей в БД, это список и при нажатии на кнопку дальше, мы выбираешь следующего
        # как только мы нажали на start count обнуляется и если человек начнет смотреть БД, то снова с 0 список людей
        self.count = 0
        # param_persons = нужен нам для сохранения данных по людям, которых искать, и будем перезаписывать каждый раз
        # при подаче новых данных для поиска от пользователя
        self.param_persons = {}
        # offset выводит в вк следующего человека в списке из полученных. т.е. 0 - самый первый в списке, потом
        # 2,3 и т.д., будем увеличивать при пролистывании людей, чтобы не показывать 1 и тех же
        self.offset_vk = 0


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

                    data = people_search.get_user_info(id)
                    user_db.add_user(data)

                    msg = event.text.lower()

                    if msg in iniciate_messages:

                        self.sender(id, 'hello', self.clear_key_board())


                    if msg == 'start':
                        flag = 0
                        self.count = 0
                        self.offset_vk = 0
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
                                           '3- Общий поиск людей(указать пол, возраст, город) \n'
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
                                        break

                                    if str(msg) == '3':
                                        self.sender(id, 'Для общего поиска людей выберите кого ищем \n ',
                                               self.menu_sex_key_board())
                                        user.mode = 'menu_sex'




                                ##  Логика на 1 пункт
                                elif user.mode == 'db_check':
                                    # достаем id нашего юзера из базы данных
                                    data_us_bd = user_db.search_user_from_db('id'+str(id))
                                    # по нему ищем релайтед людей, и получаем список с id этих людей
                                    all_related = user_db.find_using_users_selected(data_us_bd['id'])
                                    # пробегаемся по списку, и ищем через функцию данные по id
                                    list_related = []
                                    for item in all_related:
                                        result_realted = user_db.search_selected_from_db_using_id(item)
                                        list_related.append(result_realted['name'] + ' ' + result_realted['last_name'])




                                    if msg == 'следующий контакт':
                                        # так как у нас список с людьми, при каждом нажатии кнопки count +1, т.е.
                                        # выводим следующего в списке.
                                        try:
                                            self.sender(id, f'В {list_related[self.count]} \n ',
                                                        self.menu_check_db_key_board())
                                            user.mode = 'db_check'
                                            self.count += 1
                                        except:
                                            self.sender(id, 'Больше нет людей в базе, напишите start \n ',
                                                        self.clear_key_board())
                                            # обязательно обнуляем и счетчик и статус. все сначало через старт
                                            user.mode = ''
                                            self.count = 0


                                    if msg == 'удалить контакт':
                                        self.sender(id, 'Удаляем предыдущий выданный контакты, Функция ДБ \n ',
                                               self.menu_check_db_key_board())
                                        user.mode = 'db_check'

                                    if msg == 'искать людей':
                                        self.sender(id, 'Переходим на поиск людей, Для общего поиска людей выберите '
                                                        'кого ищем \n ',
                                               self.menu_sex_key_board())
                                        user.mode = 'menu_sex'




                                ##  Логика на 3 пункт

                                elif user.mode == 'menu_sex':
                                    if msg == 'девушку':
                                        self.sender(id, 'напишите возраст девушки, например: 27',
                                                    self.clear_key_board())
                                        user.mode = 'girl_find_age'
                                        break


                                    if msg == 'парня':
                                        self.sender(id, 'Выводим парней, тут идет функция поиска (Парней) '
                                                   'и вывода \n ', self.menu_find_people_key_board())
                                        user.mode = 'boy_find'


                                # меню выбора с девушкой
                                if user.mode == 'girl_find_age':
                                    # обрабатываем не корректный ввод пользователя + нам надо увериться, что это
                                    # наше сообщение, оно должно быть числом
                                    try:
                                        decision = int(msg)
                                        if decision:
                                            girl_decision_age = msg
                                            # мы создали словарь, куда будем пересоздавать данные людей
                                            # для ввода в наш поиск, для аргументов.
                                            self.param_persons['age_girl'] = int(girl_decision_age)
                                            self.sender(id, 'напишите город в котором искать',
                                                        self.clear_key_board())
                                            user.mode = 'girl_find_city'
                                            break
                                    except:
                                        self.sender(id, 'вы не ввели число, повторите ввод возраста девушки',
                                                    self.clear_key_board())
                                        user.mode = 'girl_find_age'

                                # тут функция с выводом девушки
                                if user.mode == 'girl_find_city':
                                    if msg:
                                        self.param_persons['city_girl'] = msg
                                        # конвертируем имя города в id
                                        city_decis = some_choice.get_city_id(self.param_persons['city_girl'])

                                        # теперь у нас есть два аргумента для функции в словаре self.param_persons
                                        result_find_girl = some_choice.get_all_available_people\
                                            (1, self.param_persons['age_girl'], city_decis, self.offset_vk)

                                        #сразу сохраянем id_vk в словарь, если кликнут на добавление в БД используем,
                                        #если нет перезапишем следующим выбором.
                                        # если вдруг vk_id имя а не номер, чистим
                                        result_id = result_find_girl['vk_id']
                                        result_id_split = result_id.replace('id', '')
                                        # если id можно выразить числом, все хорошо, если id изменен как имя, то
                                        # ищем реальный id человека
                                        try:
                                            result_id_fin = int(result_id_split)
                                            self.param_persons['vk_id'] = result_id_fin
                                        except:
                                            result_id_fin = some_choice.find_id_using_screen(result_id_split)
                                            self.param_persons['vk_id'] = result_id_fin
                                            # там словарь приходит, достаем конкретно id



#### Тут жуть просто для теста, временно
                                        data_people_selected = some_choice.get_rel_people_by_id(self.param_persons['vk_id'])
                                        foto1 = ''
                                        foto2 = ''
                                        foto3 = ''
                                        count_photo = 0
                                        for item in data_people_selected["photo"]:
                                            if count_photo == 0:
                                                foto1 = item
                                                count_photo += 1
                                            if count_photo == 1:
                                                foto2 = item
                                                count_photo += 1
                                            if count_photo == 2:
                                                foto3 = item
                                                count_photo += 1

                                        self.sender(id, f'{result_find_girl["name"]}  {result_find_girl["last_name"]}'
                                                        f'  https://vk.com/{result_find_girl["vk_id"]}'
                                                        f' foto: {foto1}\n'
                                                        f' foto: {foto1}\n'
                                                        f' foto: {foto1}\n',
                                                    self.menu_find_people_key_board())
                                        # увеличваем offset для вывода следующего человека в поиске  вк
                                        self.offset_vk += 1
                                        user.mode = 'girl_find_run'


                                if user.mode == 'girl_find_run':
                                    if msg == 'следующий человек':
                                        result_find_girl = some_choice.get_all_available_people\
                                            (1, self.param_persons['age_girl'],
                                             some_choice.get_city_id(self.param_persons['city_girl']), self.offset_vk)

                                        # cохраняем vk_id выбора если вдруг хахотят добавит в БД
                                        self.param_persons['vk_id'] = result_find_girl['vk_id']

                                        self.sender(id, f'{result_find_girl["name"]}  {result_find_girl["last_name"]}'
                                                        f'  https://vk.com/{result_find_girl["vk_id"]}'
                                                        f'\n ', self.menu_find_people_key_board())
                                        self.offset_vk += 1
                                        user.mode = 'girl_find_run'



                                    if msg == 'добавить в контакты':
                                        result_id = self.param_persons['vk_id']
                                        # нам надо выкинуть id из id32334342
                                        result_id_split = result_id.replace('id', '')
                                        # если id можно выразить числом, все хорошо, если id изменен как имя, то
                                        # ищем реальный id человека
                                        try:
                                            result_id_fin = int(result_id_split)
                                        except:
                                            result_id_fin = some_choice.find_id_using_screen(result_id_split)
                                            # там словарь приходит, достаем конкретно id

                                        data_people_selected = some_choice.get_rel_people_by_id(result_id_fin)

                                        print(data_people_selected)

                                        run_db.add_selected(data_people_selected)


                                        self.sender(id, 'Добавляем в контакты предыдущий вывод, тут идет функция БД '
                                                   'и вывода \n ', self.menu_find_people_key_board())
                                        user.mode = 'girl_find_run'







                                if user.mode == 'boy_find':
                                    if msg == 'следующий человек':
                                        self.sender(id, 'Продолжаем вывод, тут идет функция поиска (Парней) '
                                                   'и вывода \n ', self.menu_find_people_key_board())
                                        user.mode = 'boy_find'

                                    if msg == 'добавить в контакты':
                                        self.sender(id, 'Добавляем в контакты предыдущий вывод, тут идет функция БД '
                                                   'и вывода \n ', self.menu_find_people_key_board())
                                        user.mode = 'boy_find'

                                # if user.mode == 'db_check':
                                #     self.sender(id, 'Смотрим базу тест 2 \n ', self.menu_check_db_key_board())
                                #     user.mode = 'db_check'
                    #



bot_start = Bot(vk_token)
bot_start.start_run()


