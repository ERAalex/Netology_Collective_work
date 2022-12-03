import random, vk_api
from vk_api.keyboard import VkKeyboardColor, VkKeyboard
from vk_api.utils import get_random_id
from vk_api.longpoll import VkLongPoll, VkEventType
import json
from vk_folder.some_frases import iniciate_messages
# from db_mongo import find_document, series_collection, insert_document
import os
from pprint import pprint

from DB.db import run_db

from vk_folder.people_search import User_vk, some_choice, user_need

token_user = os.getenv('token_user')
vk_token = os.getenv('token')
vk_s = vk_api.VkApi(token=vk_token)
session_api = vk_s.get_api()

people_search = User_vk(token_user)


class User:
    def __init__(self, id, mode):
        self.id = id

        self.id_in_db = 0
        self.count_in_db = 0

        self.mode = mode
        # записываем данные найденных людей, например для добавления в БД
        self.param_persons = {}
        # список людей, которые выводится функцией get_all_available_people
        self.list_of_search_persons = []
        # для перепора этого списка нам нужен счетчик, для вывода следющего
        self.count_in_person_list = 0
        # сюда идет список людей полученных функцией по показу бана в БД
        self.user_id_in_db = []

        self.name = ''
        self.age = -1
        self.related_finded = {}
        self.offset_vk = 0


users_class = []

check = []


class Bot:

    # начальные параметры для работы бота
    def __init__(self, token):
        self.token = token
        self.vk_session = vk_api.VkApi(token=token)
        self.longpoll = VkLongPoll(self.vk_session)
        self.vk = self.vk_session.get_api()
        user = User(100, 'some')
        self.users = [user]

        # param_persons = нужен нам для сохранения данных по людям, которых искать, и будем перезаписывать каждый раз
        # при подаче новых данных для поиска от пользователя
        self.param_persons = {}
        # offset выводит в вк следующего человека в списке из полученных. т.е. 0 - самый первый в списке, потом
        # 2,3 и т.д., будем увеличивать при пролистывании людей, чтобы не показывать 1 и тех же
        self.offset_vk = 0
        self.id_user_bot = ''
        self.id_user = ''
        self.while_true = True
        self.user_id_in_db = 0
        self.count_in_person_list = 0
        self.users_class = []

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

    # cамая главная часть, работа бота
    def start_run(self):
        for event in self.longpoll.listen():
            if event.type == VkEventType.MESSAGE_NEW:
                if event.to_me:

                    id = event.user_id
                    self.id_user = id

                    # для начала првоеряем если список объектов класса Юзер не равен 0, тк. при запуске бота он = 0
                    # заполним его сразу первым юзером
                    if len(users_class) == 0:
                        self.id_user_bot = User(id, '')
                        users_class.append(self.id_user_bot)

                    # дальше проверяем есть такой объект-юзер или нет, если новый человек заносим его как объект в базу
                    # для использования методов и сохранения его персональных данных на момент пользования ботом
                    for item in users_class:
                        if item.id != id:
                            self.id_user_bot = User(id, '')
                            users_class.append(self.id_user_bot)
                        else:
                            pass

                    for item in users_class:
                        if item.id not in check:
                            check.append(item.id)

                    # проверяем есть ли такой пользователь в базе и обновляем
                    data = people_search.get_user_info(id)

                    run_db.add_user(data)

                    # Достаем и сохраняем id в БД текущего пользователя. Внимание это не ID vk!!
                    user_find_from_db = run_db.search_user_from_db('id' + str(id))
                    # self.id_user_bot.id_in_db = user_find_from_db['id']
                    # print(self.id_user_bot.id_in_db)

                    user_id_saved = user_find_from_db['id']

                    msg = event.text.lower()

                    if msg in iniciate_messages:
                        self.sender(id, 'hello', self.clear_key_board())

                    if msg == 'start':
                        try:
                            run_db.delete_user_mode(user_id_saved)
                        except:
                            pass
                        self.sender(id, 'Что будем делать? Наберите цифру: \n'
                                        '1- Посмотреть добавленные контакты \n'
                                        '2- Расширенный поиск человека (совпадения по книгам, музыке) \n'
                                        '3- Общий поиск людей(указать пол, возраст, город) \n'
                                        '\n'
                                        '\n'
                                        ' ', self.clear_key_board())

                        # сохраняем в БД статус
                        run_db.add_user_mode(user_id_saved, 'start')
                        # self.id_user_bot.mode = 'start'



                    else:
                        for user in users_class:
                            if user.id == id:
                                ##  Логика на Старт меню

                                # if self.id_user_bot.mode == 'start':
                                if run_db.get_user_mode(user_id_saved) == 'start':

                                    if str(msg) == '1':
                                        self.sender(id, 'Ваши контакты: Нажмите "Следующий" \n ',
                                                    self.menu_check_db_key_board())
                                        run_db.update_user_mode(user_id_saved, 'db_check')

                                    if str(msg) == '3':
                                        self.sender(id, 'Для общего поиска людей выберите кого ищем \n ',
                                                    self.menu_sex_key_board())
                                        run_db.update_user_mode(user_id_saved, 'menu_sex')

                                        ##  Логика на 1 пункт

                                    elif run_db.get_user_mode(user_id_saved) == 'db_check':
                                        # достаем id нашего юзера из базы данных
                                        data_us_bd = run_db.search_user_from_db('id' + str(id))
                                        # по нему ищем релайтед людей, и получаем список с id этих людей
                                        all_related = run_db.find_using_users_selected(data_us_bd['id'])
                                        # пробегаемся по списку, и ищем через функцию данные по id
                                        list_related = []

                                        for item in all_related:
                                            result_realted = run_db.search_selected_from_db_using_id(item)
                                            # получаем айди пользователя из БД
                                            related_db_id = result_realted['id']
                                            # проверка на не вхождение в список удаленных пользователем
                                            check_deleted = run_db.get_id_deleted_selected(self.id_user_bot.id_in_db)
                                            if related_db_id not in check_deleted:
                                                list_related.append(f'''{result_realted["name"]}  
                                                                        {result_realted["last_name"]}
                                                                        https://vk.com/{result_realted["vk_id"]}''')

                                        if msg == 'следующий контакт':
                                            # так как у нас список с людьми, при каждом нажатии кнопки count +1, т.е.
                                            # выводим следующего в списке.
                                            try:
                                                self.sender(id, f'{list_related[self.id_user_bot.count_in_db]} \n ',
                                                            self.menu_check_db_key_board())
                                                self.id_user_bot.mode = 'db_check'
                                                self.id_user_bot.count_in_db += 1
                                            except:
                                                self.sender(id, 'Больше нет людей в базе, напишите start \n ',
                                                            self.clear_key_board())
                                                # обязательно обнуляем и счетчик и статус. все сначало через старт
                                                self.id_user_bot.mode = ''
                                                self.id_user_bot.count_in_db = 0

                                            if msg == 'удалить контакт':
                                                self.sender(id, 'Удаляем предыдущий выданный контакты, Функция ДБ \n ',
                                                            self.menu_check_db_key_board())
                                                # помечаем пользователя удаленным
                                                run_db.mark_deleted_from_selected(self.user_id_in_db, related_db_id)
                                                self.id_user_bot.mode = 'db_check'

                                            if msg == 'искать людей':
                                                self.sender(id,
                                                            'Переходим на поиск людей, Для общего поиска людей выберите '
                                                            'кого ищем \n ',
                                                            self.menu_sex_key_board())
                                                self.id_user_bot.mode = 'menu_sex'

                                    ## Логика на 3 пункт бота ###

                                elif run_db.get_user_mode(user_id_saved) == 'menu_sex':
                                    # elif self.id_user_bot.mode == 'menu_sex':
                                    if msg == 'девушку':
                                        self.sender(id, 'напишите возраст девушки, например: 27',
                                                    self.clear_key_board())
                                        run_db.update_user_mode(user_id_saved, 'girl_find_age')
                                        break

                                    if msg == 'парня':
                                        self.sender(id, 'напишите возраст парня, например: 27',
                                                    self.clear_key_board())
                                        run_db.update_user_mode(user_id_saved, 'boy_find_age')
                                        break

                                        # меню выбора с девушкой
                                if run_db.get_user_mode(user_id_saved) == 'girl_find_age':
                                    # if self.id_user_bot.mode == 'girl_find_age':
                                    # обрабатываем не корректный ввод пользователя + нам надо увериться, что это
                                    # наше сообщение, оно должно быть числом
                                    try:
                                        decision = int(msg)
                                        if decision:
                                            girl_decision_age = msg

                                            # сохраняем в БД выбор пользователя лет девушке
                                            run_db.add_user_choise_age(user_id_saved, girl_decision_age)
                                            # self.id_user_bot.param_persons['age_girl'] = int(girl_decision_age)

                                            self.sender(id, 'напишите город в котором искать, мы начнем поиск \n'
                                                            'это может занять пару минут, что значительно ускорит \n'
                                                            'дальнейший вывод',
                                                        self.clear_key_board())
                                            run_db.update_user_mode(user_id_saved, 'girl_find_city')
                                            break

                                    except:
                                        self.sender(id, 'вы не ввели число, повторите ввод возраста девушки',
                                                    self.clear_key_board())
                                        run_db.update_user_mode(user_id_saved, 'girl_find_age')

                                # тут функция с выводом девушки
                                if run_db.get_user_mode(user_id_saved) == 'girl_find_city':

                                    if msg:
                                        # сохраняем выбор города в БД Юзер сессии
                                        run_db.add_user_choise_city(user_id_saved, msg)

                                        # сразу готовим count в виде step
                                        run_db.update_step_session(user_id_saved, 0)

                                        # парсим людей получаем список где человек 100 сохраняем
                                        resul_find_people = some_choice.get_all_available_people \
                                            (1, run_db.get_users_choise_age(user_id_saved),
                                             run_db.get_users_choise_city(user_id_saved))

                                        # сохраняем в базу в Юзер Сессион
                                        run_db.add_user_choise_ids(user_id_saved, resul_find_people)
                                        # пошел цикл он нужен, чтобы убрать тех у кого мало фото < 3

                                        while_true = True
                                        while while_true == True:

                                            # берем из базы данных строку с пользователями
                                            result_1 = run_db.get_users_choise_ids(user_id_saved)
                                            # преобразуем в список
                                            result_2 = result_1.split(',')

                                            # достаем текущий шаг
                                            step_now = run_db.get_step_ids_session(user_id_saved)

                                            # берем человека из списка согласну step
                                            result_next = result_2[step_now]

                                            # сразу увеличиваем step
                                            run_db.update_step_session(user_id_saved, step_now + 1)

                                            # проверка если человек в бане
                                            list_ban = run_db.get_all_vk_id_of_banned(user_id_saved)

                                            if result_next in list_ban:
                                                print('в бане')
                                                # добавляем offset чтобы пропустить его и идем дальше по людям

                                            else:
                                                result = user_need.get_user_info(result_next)
                                                self.sender(id,
                                                            f'{result["name"]}  {result["last_name"]} \n'
                                                            f' {some_choice.send_info_in_bot(self.id_user_bot.id, result_next)}',
                                                            self.menu_find_people_key_board())
                                                run_db.update_user_mode(user_id_saved, 'girl_find_run')
                                                while_true = False

                                if run_db.get_user_mode(user_id_saved) == 'girl_find_run':
                                    if msg == 'следующий человек':

                                        while_true = True
                                        while while_true == True:

                                            # берем из базы данных строку с пользователями
                                            result_1 = run_db.get_users_choise_ids(user_id_saved)
                                            # преобразуем в список
                                            result_2 = result_1.split(',')

                                            # достаем текущий шаг
                                            step_now = run_db.get_step_ids_session(user_id_saved)

                                            # берем человека из списка согласну step
                                            result_next = result_2[step_now]

                                            # сразу увеличиваем step
                                            run_db.update_step_session(user_id_saved, step_now + 1)

                                            # проверка если человек в бане
                                            list_ban = run_db.get_all_vk_id_of_banned(user_id_saved)

                                            if result_next in list_ban:
                                                print('в бане')
                                                # добавляем offset чтобы пропустить его и идем дальше по людям

                                            else:
                                                result = user_need.get_user_info(result_next)
                                                self.sender(id,
                                                            f'{result["name"]}  {result["last_name"]} \n'
                                                            f' {some_choice.send_info_in_bot(self.id_user_bot.id, result_next)}',
                                                            self.menu_find_people_key_board())
                                                run_db.update_user_mode(user_id_saved, 'girl_find_run')
                                                while_true = False

                                    # заносим в БАН в БД, по vk id (причем сохраняется там без приписки id - id232423)
                                    if msg == 'больше не показывать':
                                        # заносим в бан
                                        result_1 = run_db.get_users_choise_ids(user_id_saved)
                                        result_2 = result_1.split(',')
                                        step_now = run_db.get_step_ids_session(user_id_saved)
                                        result_next = result_2[step_now - 1]

                                        run_db.add_banned(user_id_saved, result_next)

                                        self.sender(id, 'Данный пользователь больше не будет появляться в рекомендациях'
                                                        ' \n ', self.menu_find_people_key_board())
                                        run_db.update_user_mode(user_id_saved, 'girl_find_run')

                                    if msg == 'добавить в контакты':
                                        result_1 = run_db.get_users_choise_ids(user_id_saved)
                                        result_2 = result_1.split(',')
                                        step_now = run_db.get_step_ids_session(user_id_saved)
                                        # это наш vk_id текущего человека
                                        result_next = result_2[step_now - 1]

                                        data_people_selected = some_choice.get_rel_people_by_id(result_next)
                                        run_db.add_selected(data_people_selected)
                                        print('человек добавлен')
                                        # ищем id нашего релайтед в базе
                                        info = run_db.search_selected_from_db('id' + str(result_next))

                                        run_db.mark_users_selected(user_id_saved, info['id'])
                                        print('связь между юзером и релайтед создана')

                                        self.sender(id, f'Вы добавили {data_people_selected["name"]} '
                                                        f'{data_people_selected["last_name"]} '
                                                        'в Базу данных \n ', self.menu_find_people_key_board())

                                        run_db.update_user_mode(user_id_saved, 'girl_find_run')

                                ####### меню выбора с парнем
                                if run_db.get_user_mode(user_id_saved) == 'boy_find_age':
                                    # обрабатываем не корректный ввод пользователя + нам надо увериться, что это
                                    # наше сообщение, оно должно быть числом

                                    try:
                                        decision = int(msg)
                                        if decision:
                                            boy_decision_age = msg

                                            # сохраняем в БД выбор пользователя лет девушке
                                            run_db.add_user_choise_age(user_id_saved, boy_decision_age)

                                            self.sender(id, 'напишите город в котором искать, мы начнем поиск \n'
                                                            'это может занять пару минут, что значительно ускорит \n'
                                                            'дальнейший вывод',
                                                        self.clear_key_board())
                                            run_db.update_user_mode(user_id_saved, 'boy_find_city')
                                            break
                                    except:
                                        self.sender(id, 'вы не ввели число, повторите ввод возраста парня',
                                                    self.clear_key_board())
                                        run_db.update_user_mode(user_id_saved, 'boy_find_age')

                                # тут функция с выводом девушки
                                if run_db.get_user_mode(user_id_saved) == 'boy_find_city':

                                    if msg:
                                        # сохраняем выбор города в БД Юзер сессии
                                        run_db.add_user_choise_city(user_id_saved, msg)

                                        # сразу готовим count в виде step
                                        run_db.update_step_session(user_id_saved, 0)

                                        # парсим людей получаем список где человек 100 сохраняем
                                        resul_find_people = some_choice.get_all_available_people \
                                            (2, run_db.get_users_choise_age(user_id_saved),
                                             run_db.get_users_choise_city(user_id_saved))

                                        # сохраняем в базу в Юзер Сессион
                                        run_db.add_user_choise_ids(user_id_saved, resul_find_people)
                                        # пошел цикл он нужен, чтобы убрать тех у кого мало фото < 3

                                        while_true = True
                                        while while_true == True:

                                            # берем из базы данных строку с пользователями
                                            result_1 = run_db.get_users_choise_ids(user_id_saved)
                                            # преобразуем в список
                                            result_2 = result_1.split(',')

                                            # достаем текущий шаг
                                            step_now = run_db.get_step_ids_session(user_id_saved)

                                            # берем человека из списка согласну step
                                            result_next = result_2[step_now]

                                            # сразу увеличиваем step
                                            run_db.update_step_session(user_id_saved, step_now + 1)

                                            # проверка если человек в бане
                                            list_ban = run_db.get_all_vk_id_of_banned(user_id_saved)

                                            if result_next in list_ban:
                                                print('в бане')
                                                # добавляем offset чтобы пропустить его и идем дальше по людям

                                            else:
                                                result = user_need.get_user_info(result_next)
                                                self.sender(id,
                                                            f'{result["name"]}  {result["last_name"]} \n'
                                                            f' {some_choice.send_info_in_bot(self.id_user_bot.id, result_next)}',
                                                            self.menu_find_people_key_board())
                                                run_db.update_user_mode(user_id_saved, 'boy_find_run')
                                                while_true = False

                                if run_db.get_user_mode(user_id_saved) == 'boy_find_run':
                                    if msg == 'следующий человек':

                                        while_true = True
                                        while while_true == True:

                                            # берем из базы данных строку с пользователями
                                            result_1 = run_db.get_users_choise_ids(user_id_saved)
                                            # преобразуем в список
                                            result_2 = result_1.split(',')

                                            # достаем текущий шаг
                                            step_now = run_db.get_step_ids_session(user_id_saved)

                                            # берем человека из списка согласну step
                                            result_next = result_2[step_now]

                                            # сразу увеличиваем step
                                            run_db.update_step_session(user_id_saved, step_now + 1)

                                            # проверка если человек в бане
                                            list_ban = run_db.get_all_vk_id_of_banned(user_id_saved)

                                            if result_next in list_ban:
                                                print('в бане')
                                                # добавляем offset чтобы пропустить его и идем дальше по людям

                                            else:
                                                result = user_need.get_user_info(result_next)
                                                self.sender(id,
                                                            f'{result["name"]}  {result["last_name"]} \n'
                                                            f' {some_choice.send_info_in_bot(self.id_user_bot.id, result_next)}',
                                                            self.menu_find_people_key_board())
                                                run_db.update_user_mode(user_id_saved, 'boy_find_run')
                                                while_true = False

                                    # заносим в БАН в БД, по vk id (причем сохраняется там без приписки id - id232423)
                                    if msg == 'больше не показывать':
                                        # заносим в бан
                                        result_1 = run_db.get_users_choise_ids(user_id_saved)
                                        result_2 = result_1.split(',')
                                        step_now = run_db.get_step_ids_session(user_id_saved)
                                        result_next = result_2[step_now]

                                        run_db.add_banned(user_id_saved, result_next)

                                        self.sender(id, 'Данный пользователь больше не будет появляться в рекомендациях'
                                                        ' \n ', self.menu_find_people_key_board())
                                        run_db.update_user_mode(user_id_saved, 'boy_find_run')

                                    if msg == 'добавить в контакты':
                                        result_1 = run_db.get_users_choise_ids(user_id_saved)
                                        result_2 = result_1.split(',')
                                        step_now = run_db.get_step_ids_session(user_id_saved)
                                        # это наш vk_id текущего человека
                                        result_next = result_2[step_now]

                                        data_people_selected = some_choice.get_rel_people_by_id(result_next)
                                        run_db.add_selected(data_people_selected)
                                        print('человек добавлен')
                                        # ищем id нашего релайтед в базе
                                        info = run_db.search_selected_from_db('id' + str(result_next))

                                        run_db.mark_users_selected(user_id_saved, info['id'])
                                        print('связь между юзером и релайтед создана')

                                        self.sender(id, f'Вы добавили {data_people_selected["name"]} '
                                                        f'{data_people_selected["last_name"]} '
                                                        'в Базу данных \n ', self.menu_find_people_key_board())

                                        run_db.update_user_mode(user_id_saved, 'boy_find_run')


bot_start = Bot(vk_token)
bot_start.start_run()