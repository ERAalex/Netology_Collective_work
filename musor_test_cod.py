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

from vk_folder.people_search import User_vk, some_choice

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
                        print('check1')

                    # дальше проверяем есть такой объект-юзер или нет, если новый человек заносим его как объект в базу
                    # для использования методов и сохранения его персональных данных на момент пользования ботом
                    for item in users_class:
                        if item.id != id:
                            self.id_user_bot = User(id, '')
                            users_class.append(self.id_user_bot)
                            print('check2')
                        else:
                            pass


                    for item in users_class:
                        if item.id not in check:
                            check.append(item.id)
                    print(check)

                    # проверяем есть ли такой пользователь в базе и обновляем
                    data = people_search.get_user_info(id)
                    run_db.add_user(data)

                    # Достаем и сохраняем id в БД текущего пользователя. Внимание это не ID vk!!
                    user_find_from_db = run_db.search_user_from_db('id' + str(id))
                    self.id_user_bot.id_in_db = user_find_from_db['id']
                    print(self.id_user_bot.id_in_db)

                    user_id_saved = user_find_from_db['id']


                    msg = event.text.lower()


                    if msg in iniciate_messages:
                        self.sender(id, 'hello', self.clear_key_board())

                    if msg == 'start':
                        try:
                            run_db.delete_user_mode(user_id_saved)
                        except:
                            pass
                        print('__1___')
                        print(self.id_user_bot.id)
                        print(self.id_user_bot.mode)
                        print('__1___')
                        self.id_user_bot.offset_vk = 0
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
                                                self.sender(id, 'Переходим на поиск людей, Для общего поиска людей выберите '
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
                                            # мы создали словарь, куда будем пересоздавать данные людей
                                            # для ввода в наш поиск, для аргументов.
                                            self.id_user_bot.param_persons['age_girl'] = int(girl_decision_age)
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
                                # if self.id_user_bot.mode == 'girl_find_city':
                                    pprint(check)
                                    if msg:
                                        self.id_user_bot.param_persons['city_girl'] = msg
                                        # # теперь у нас есть два аргумента для функции поиска
                                        # в словаре self.param_persons

                                        # парсим людей получаем список где человек 100 сохраняем
                                        self.id_user_bot.list_of_search_persons = some_choice.get_all_available_people \
                                            (1, self.id_user_bot.param_persons['age_girl'],
                                                self.id_user_bot.param_persons['city_girl'], 50)

                                        # пошел цикл он нужен, чтобы убрать тех у кого мало фото < 3

                                        while_true = True
                                        while while_true == True:

                                            # берем первого человека в списке(это словарь), и увеличиваем self.count..
                                            result = self.id_user_bot.list_of_search_persons[self.id_user_bot.count_in_person_list]
                                            self.id_user_bot.count_in_person_list += 1
                                            result_id = result['vk_id']


                                            # если id можно выразить числом, все хорошо, если id изменен как имя, то
                                            # ищем реальный id человека:
                                            try:
                                                result_id_fin = int(result_id)
                                                # сохраянем временно данные пользователя если вдруг добавлять в базу
                                                self.id_user_bot.param_persons['vk_id'] = result_id_fin
                                            except:
                                                # если vk_id изменен, ищем орининальный функцией
                                                result_id_fin = some_choice.find_id_using_screen(result_id)
                                                self.id_user_bot.param_persons['vk_id'] = result_id_fin
                                                # там словарь приходит, достаем конкретно id номер юзера которогосмотрим


                                            # проверка если человек в бане
                                            list_ban = run_db.get_all_vk_id_of_banned(self.id_user_bot.id_in_db)

                                            if str(self.id_user_bot.param_persons['vk_id']) in list_ban:
                                                print('в бане')
                                                # добавляем offset чтобы пропустить его и идем дальше по людям

                                            else:
                                                self.sender(id,
                                                            f'{result["name"]}  {result["last_name"]} \n'
                                                            f' {some_choice.send_info_in_bot(self.id_user_bot.id, result_id_fin)}',
                                                            self.menu_find_people_key_board())
                                                self.id_user_bot.mode = 'girl_find_run'
                                                while_true = False



                                if self.id_user_bot.mode == 'girl_find_run':
                                    if msg == 'следующий человек':

                                        while_true = True
                                        while while_true == True:

                                            # берем первого человека в списке(это словарь), и увеличиваем self.count..
                                            result = self.id_user_bot.list_of_search_persons[
                                                self.id_user_bot.count_in_person_list]
                                            self.id_user_bot.count_in_person_list += 1
                                            result_id = result['vk_id']

                                            # если id можно выразить числом, все хорошо, если id изменен как имя, то
                                            # ищем реальный id человека:
                                            try:
                                                result_id_fin = int(result_id)
                                                # сохраянем временно данные пользователя если вдруг добавлять в базу
                                                self.id_user_bot.param_persons['vk_id'] = result_id_fin
                                            except:
                                                # если vk_id изменен, ищем орининальный функцией
                                                result_id_fin = some_choice.find_id_using_screen(result_id)
                                                self.id_user_bot.param_persons['vk_id'] = result_id_fin
                                                # там словарь приходит, достаем конкретно id номер юзера которогосмотрим

                                            # проверка если человек в бане
                                            list_ban = run_db.get_all_vk_id_of_banned(self.id_user_bot.id_in_db)

                                            if str(self.id_user_bot.param_persons['vk_id']) in list_ban:
                                                print('в бане')
                                                # добавляем offset чтобы пропустить его и идем дальше по людям

                                            else:
                                                self.sender(id,
                                                            f'{result["name"]}  {result["last_name"]} \n'
                                                            f' {some_choice.send_info_in_bot(self.id_user_bot.id, result_id_fin)}',
                                                            self.menu_find_people_key_board())
                                                self.id_user_bot.mode = 'girl_find_run'
                                                while_true = False



                                    # заносим в БАН в БД, по vk id (причем сохраняется там без приписки id - id232423)
                                    if msg == 'больше не показывать':
                                        #заносим в бан
                                        run_db.add_banned(self.user_id_in_db, self.param_persons['vk_id'])

                                        self.sender(id, 'Данный пользователь больше не будет появляться в рекомендациях'
                                                        ' \n ', self.menu_find_people_key_board())
                                        user.mode = 'girl_find_run'




                                    if msg == 'добавить в контакты':
                                        result_id = self.param_persons['vk_id']

                                        data_people_selected = some_choice.get_rel_people_by_id(result_id)
                                        run_db.add_selected(data_people_selected)
                                        print('человек добавлен')
                                        # ищем id нашего релайтед в базе
                                        info = run_db.search_selected_from_db('id' + str(result_id))
                                        print(info)
                                        run_db.mark_users_selected(self.user_id_in_db, info['id'])
                                        print('связь между юзером и релайтед создана')

                                        self.sender(id, f'Вы добавили {data_people_selected["name"]} '
                                                        f'{data_people_selected["last_name"]} '
                                                        'в Базу данных \n ', self.menu_find_people_key_board())

                                        user.mode = 'girl_find_run'





                                ####### меню выбора с парнем
                                if self.id_user_bot.mode == 'boy_find_age':
                                    # обрабатываем не корректный ввод пользователя + нам надо увериться, что это
                                    # наше сообщение, оно должно быть числом

                                    try:
                                        decision = int(msg)
                                        if decision:
                                            boy_decision_age = msg
                                            # мы создали словарь, куда будем пересоздавать данные людей
                                            # для ввода в наш поиск, для аргументов.
                                            self.id_user_bot.param_persons['age_boy'] = int(boy_decision_age)
                                            self.sender(id, f'напишите город {self.id_user_bot.id}в котором искать, мы начнем поиск \n'
                                                            'это может занять пару минут, что значительно ускорит \n'
                                                            'дальнейший вывод',
                                                        self.clear_key_board())
                                            self.id_user_bot.mode = 'boy_find_city'
                                            break
                                    except:
                                        self.sender(id, 'вы не ввели число, повторите ввод возраста парня',
                                                    self.clear_key_board())
                                        self.id_user_bot.mode = 'boy_find_age'



                                # тут функция с выводом девушки
                                if self.id_user_bot.mode == 'boy_find_city':
                                    if msg:
                                        self.id_user_bot.param_persons['city_boy'] = msg
                                        # # теперь у нас есть два аргумента для функции поиска
                                        # в словаре self.param_persons

                                        # парсим людей получаем список где человек 100 сохраняем
                                        self.id_user_bot.list_of_search_persons = some_choice.get_all_available_people \
                                            (2, self.id_user_bot.param_persons['age_boy'],
                                             self.id_user_bot.param_persons['city_boy'], 100)

                                        # пошел цикл он нужен, чтобы убрать тех у кого мало фото < 3

                                        while_true = True
                                        while while_true == True:

                                            # берем первого человека в списке(это словарь), и увеличиваем self.count..
                                            result = self.id_user_bot.list_of_search_persons[self.id_user_bot.count_in_person_list]
                                            self.id_user_bot.count_in_person_list += 1
                                            result_id = result['vk_id']


                                            # если id можно выразить числом, все хорошо, если id изменен как имя, то
                                            # ищем реальный id человека:
                                            try:
                                                result_id_fin = int(result_id)
                                                # сохраянем временно данные пользователя если вдруг добавлять в базу
                                                self.id_user_bot.param_persons['vk_id'] = result_id_fin
                                            except:
                                                # если vk_id изменен, ищем орининальный функцией
                                                result_id_fin = some_choice.find_id_using_screen(result_id)
                                                self.id_user_bot.param_persons['vk_id'] = result_id_fin
                                                # там словарь приходит, достаем конкретно id номер юзера которогосмотрим


                                            # проверка если человек в бане
                                            list_ban = run_db.get_all_vk_id_of_banned(self.id_user_bot.id_in_db)

                                            if str(self.id_user_bot.param_persons['vk_id']) in list_ban:
                                                print('в бане')
                                                # добавляем offset чтобы пропустить его и идем дальше по людям

                                            else:
                                                self.sender(id,
                                                            f'{result["name"]}  {result["last_name"]} \n'
                                                            f' {some_choice.send_info_in_bot(self.id_user_bot.id, result_id_fin)}',
                                                            self.menu_find_people_key_board())
                                                self.id_user_bot.mode = 'boy_find_run'
                                                while_true = False





                                if user.mode == 'boy_find_run':
                                    if msg == 'следующий человек':

                                        while_true = True
                                        while while_true == True:

                                            # берем первого человека в списке(это словарь), и увеличиваем self.count..
                                            result = self.id_user_bot.list_of_search_persons[self.id_user_bot.count_in_person_list]
                                            self.id_user_bot.count_in_person_list += 1
                                            result_id = result['vk_id']


                                            # если id можно выразить числом, все хорошо, если id изменен как имя, то
                                            # ищем реальный id человека:
                                            try:
                                                result_id_fin = int(result_id)
                                                # сохраянем временно данные пользователя если вдруг добавлять в базу
                                                self.id_user_bot.param_persons['vk_id'] = result_id_fin
                                            except:
                                                # если vk_id изменен, ищем орининальный функцией
                                                result_id_fin = some_choice.find_id_using_screen(result_id)
                                                self.id_user_bot.param_persons['vk_id'] = result_id_fin
                                                # там словарь приходит, достаем конкретно id номер юзера которогосмотрим


                                            # проверка если человек в бане
                                            list_ban = run_db.get_all_vk_id_of_banned(self.id_user_bot.id_in_db)

                                            if str(self.id_user_bot.param_persons['vk_id']) in list_ban:
                                                print('в бане')
                                                # добавляем offset чтобы пропустить его и идем дальше по людям

                                            else:
                                                self.sender(id,
                                                            f'{result["name"]}  {result["last_name"]} \n'
                                                            f' {some_choice.send_info_in_bot(self.id_user_bot.id, result_id_fin)}',
                                                            self.menu_find_people_key_board())
                                                self.id_user_bot.mode = 'boy_find_run'
                                                while_true = False




                                    # заносим в БАН в БД, по vk id (причем сохраняется там без приписки id - id232423)
                                    if msg == 'больше не показывать':
                                        #заносим в бан
                                        run_db.add_banned(self.user_id_in_db, self.param_persons['vk_id'])

                                        self.sender(id, 'Данный пользователь больше не будет появляться в рекомендациях'
                                                        ' \n ', self.menu_find_people_key_board())
                                        user.mode = 'boy_find_run'




                                    if msg == 'добавить в контакты':
                                        result_id = self.param_persons['vk_id']

                                        data_people_selected = some_choice.get_rel_people_by_id(result_id)
                                        run_db.add_selected(data_people_selected)
                                        print('человек добавлен')
                                        # ищем id нашего релайтед в базе
                                        info = run_db.search_selected_from_db('id' + str(result_id))
                                        print(info)
                                        run_db.mark_users_selected(self.user_id_in_db, info['id'])
                                        print('связь между юзером и релайтед создана')


                                        self.sender(id, f'Вы добавили {data_people_selected["name"]} '
                                                        f'{data_people_selected["last_name"] } '
                                                   'в Базу данных \n ', self.menu_find_people_key_board())
                                        user.mode = 'boy_find_run'









bot_start = Bot(vk_token)
bot_start.start_run()






import vk_api
import os
from pprint import pprint
import datetime
from sqlalchemy import select, insert
from random import randint
# from DB.models import Users
# from DB.db import DB, CONNECT, run_db


class User_vk:
    def __init__(self, vk_token):
        self.vk_token_user = vk_token
        self.vk_u = vk_api.VkApi(token=vk_token)
        self.session_api = self.vk_u.get_api()




    def get_user_info(self, vk_id):
        '''
        функция, которая собирает данные пользователя чат-бота в словарь
        '''

        user_dict = {}
        user_profile = self.session_api.users.get(user_ids=vk_id,
                                                fields='domain, relation, city, sex, bdate, personal, activities, interests, movies, books, music, games, education')

        user_dict['vk_id'] = 'id' + str(vk_id)
        user_dict['name'] = user_profile[0]['first_name']
        user_dict['last_name'] = user_profile[0]['last_name']
        if 'relation' in user_profile[0]:
            user_dict['relations'] = user_profile[0]['relation']
        else:
            user_dict['relations'] = ''
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
        if 'personal' in user_profile[0]:
            if 'langs' in user_profile[0]['personal']:
                user_dict['language'] = user_profile[0]['personal']['langs']
            else:
                user_dict['language'] = ''
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

# a = User_vk(os.getenv('token'))
# print(a.get_user_info('71719671')



#список людей, из которых делать выборку
# wishing_city = input('Введите город поиска: ')
# wishing_gender = input('Введите пол собеседника(м/ж): ')
# wishing_age_from = input('Введите начальный возраст собеседника: ')
# wishing_age_till = input('Введите конечный возраст собеседника: ')

class vk_choice:
    def __init__(self, vk_token_user, vk_token):
        self.vk_token_user = vk_token_user
        self.vk_token = vk_token
        self.vk_s = vk_api.VkApi(token=vk_token)
        self.vk_u = vk_api.VkApi(token=vk_token_user)
        self.session_api_user = self.vk_u.get_api()
        self.session_api = self.vk_s.get_api()
        self.count = 0


    # получаем на вход название города, возвращаем его id
    def get_city_id(self, name_city):
        '''на вход получаем название города, на выход даем его номер нужный для поиска по city = ...'''
        result = self.session_api_user.database.getCities(q=name_city, count=1)
        id_city = ''
        for items in result['items']:
            id_city = items['id']
        return id_city

    def find_id_using_screen(self, screen_n):
        '''некоторые пользователи изменили свой id и поставили слова, это может вызвать ошибки, переделываем
        слово обратно в id пользователя (vk_id)'''
        result = self.session_api_user.utils.resolveScreenName(screen_name=screen_n)
        result_obj_id = result['object_id']
        return result_obj_id





    def get_rel_people_by_id(self, id):
        people = self.session_api_user.users.get(user_ids=id,
                                                    fields='domain, relation, personal, city, about, music, '
                                                                          'sex, books,  bdate, birth_year, activities,'
                                                                          'interests, education, games')

        people_dict = {}
        # Список людей не в блэклисте, у которых есть фото,

        people_dict['vk_id'] = 'id' + str(id)

        for el in people:
            if el['sex'] == 1:
                people_dict['gender'] = 'ж'
            else:
                people_dict['gender'] = 'м'

            if 'city' in el:
                people_dict['city'] = el['city']['title']
            else:
                people_dict['city'] = ''
            if 'langs' in el:
                people_dict['language'] = el['personal']['langs']
            else:
                people_dict['language'] = ''

            people_dict['name'] = el['first_name']
            people_dict['last_name'] = el['last_name']

            if 'relation' in el:
                people_dict['relations'] = el['relation']
            else:
                people_dict['relations'] = 0

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
            if 'age' in el:
                people_dict['age'] = el['age']
            else:
                people_dict['age'] = 0
            if 'movies' in el:
                people_dict['movies'] = el['movies']
            else:
                people_dict['movies'] = ''
            if 'books' in el:
                people_dict['books'] = el['books']
            else:
                people_dict['books'] = ''
            if 'music' in el:
                people_dict['music'] = el['music']
            else:
                people_dict['music'] = ''

            # через функцию ниже берем 3 лучших фото и кидаем в список.
            try:
                people_dict['photo'] = self.get_top_3_foto(id)
            except:
                people_dict['photo'] = ['аккаунт закрыт для выборки фото']

            return people_dict





    def get_all_available_people_2(self, gender, age, name_city):
        '''интересный момент чем выше offset тем больше фото найдет. поэтому пусть будет максимум как count'''
        while True:
            city = vk_choice.get_city_id(self, name_city)
            people = self.session_api_user.users.search(sort=0, blacklisted=0, is_closed=False,
                                                        sex=gender, offset=self.count,
                                                        blacklisted_by_me=0, birth_year=(2022 - int(age)),
                                                        has_photo=1, count=100, city_id=city,
                                                        fields='domain, relation, personal, city, about, '
                                                               'sex, books, bdate, birth_year, activities, '
                                                               'interests, education, movies, games')

            filtred_people = []
            # Список людей не в блэклисте, у которых есть фото,
            for el in people['items']:
                try:
                    photos = self.session_api_user.photos.get(owner_id=el['id'], extended=1, album_id='profile')['items']
                    if len(photos) >=3:
                        if 'city' in el and el['city']['title'] == name_city.title():
                            people_dict = {}
                            filtred_people.append(people_dict)
                            people_dict['city'] = el['city']['title']

                            if el['sex'] == 1:
                                people_dict['gender'] = 'ж'
                            else:
                                people_dict['gender'] = 'м'
                            if 'langs' in el:
                                people_dict['languages'] = el['personal']['langs']
                            else:
                                people_dict['languages'] = ''

                            people_dict['name'] = el['first_name']
                            people_dict['last_name'] = el['last_name']
                            people_dict['vk_id'] = photos[0]['owner_id']
                            # people_dict['vk_id'] = el["domain"]
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
                            if 'movies' in el:
                                people_dict['movies'] = el['movies']
                            else:
                                people_dict['movies'] = ''
                            if filtred_people != []:
                                self.count += 1
                                return filtred_people
                            else:
                                self.count += 1
                        else:
                            # i+=1
                            # print('нет города в описании', i)
                            self.count += 1

                    else:
                        # i+=1
                        # print('меньше 3 фоток', i)
                        self.count += 1

                except:
                    # i+=1
                    # print('закрыт профиль', i)
                    self.count += 1







    def get_all_available_people(self, gender, age, name_city, total_and_offset: int):
        '''интересный момент чем выше offset тем больше фото найдет. поэтому пусть будет максимум как count'''
        city = vk_choice.get_city_id(self, name_city)
        people = self.session_api_user.users.search(sort=0, blacklisted=0, is_closed=False,
                                                    sex=gender, offset=total_and_offset,
                                                    blacklisted_by_me=0, birth_year=(2022 - int(age)),
                                                    has_photo=1, count=total_and_offset, city_id=city,
                                                    fields='domain, relation, personal, city, about, '
                                                           'sex, books, bdate, birth_year, activities, '
                                                           'interests, education, movies, games')

        filtred_people = []
        # Список людей не в блэклисте, у которых есть фото,
        for el in people['items']:
            try:
                photos = self.session_api_user.photos.get(owner_id=el['id'], extended=1, album_id='profile')['items']
                if len(photos) >=3:
                    if 'city' in el and el['city']['title'] == name_city.title():
                        people_dict = {}
                        filtred_people.append(people_dict)
                        people_dict['city'] = el['city']['title']

                        if el['sex'] == 1:
                            people_dict['gender'] = 'ж'
                        else:
                            people_dict['gender'] = 'м'
                        if 'langs' in el:
                            people_dict['languages'] = el['personal']['langs']
                        else:
                            people_dict['languages'] = ''

                        people_dict['name'] = el['first_name']
                        people_dict['last_name'] = el['last_name']
                        people_dict['vk_id'] = photos[0]['owner_id']
                        # people_dict['vk_id'] = el["domain"]
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
                        if 'movies' in el:
                            people_dict['movies'] = el['movies']
                        else:
                            people_dict['movies'] = ''

                    else:
                        # i+=1
                        # print('нет города в описании', i)
                        pass

                else:
                    # i+=1
                    # print('меньше 3 фоток', i)
                    pass

            except:
                # i+=1
                # print('закрыт профиль', i)
                pass
        return filtred_people



    def get_top_3_foto(self, id):
        '''функция по сохранению 3 фото из id'''
        profile_photos = self.session_api_user.photos.get(owner_id=id, extended=1, album_id='profile')['items']

        most_liked = sorted(profile_photos, key=lambda likes: likes['likes']['count'], reverse=True)[:3]
        all_photo_attachments = []
        # достаем картинки из топ 3, причем конкретно большого размера
        for item in most_liked:
            for item_s in item['sizes']:
                if item_s['type'] == 'z':
                    all_photo_attachments.append(item_s['url'])

        return all_photo_attachments


    def send_info_in_bot(self, id_user, id_related):
        '''
        функция, которая выводит в чат с ботом информацию о пользователе из функции поиска в нужном формате
        '''
        profile_all_info_to_bd = self.get_rel_people_by_id(id_related)
        name = profile_all_info_to_bd['name']
        surname = profile_all_info_to_bd['last_name']
        profile_id_int = self.session_api_user.users.get(user_ids=profile_all_info_to_bd['vk_id'])[0]['id']
        profile_photos = self.session_api_user.photos.get(owner_id=profile_id_int, extended=1, album_id='profile')['items']
        most_liked = sorted(profile_photos, key=lambda likes: likes['likes']['count'], reverse=True)[:3]
        all_photo_attachments = []
        for el in most_liked:
            all_photo_attachments.append(f'photo{profile_id_int}_{el["id"]}')
        send_info = self.session_api.messages.send(user_id=f'{id_user}',
                                                   random_id=randint(0, 1000),
                                                   message=f'{name} {surname}\nhttps://vk.com/{profile_all_info_to_bd["vk_id"]}',
                                                   attachment=f'{all_photo_attachments[0]},{all_photo_attachments[1]},{all_photo_attachments[2]}')
        return send_info


    def get_list_3_foto(self, id_related):
        '''
        функция, которая выводит в чат с ботом информацию о пользователе из функции поиска в нужном формате
        '''
        profile_all_info_to_bd = self.get_rel_people_by_id(id_related)
        profile_id_int = self.session_api_user.users.get(user_ids=profile_all_info_to_bd['vk_id'])[0]['id']
        # ниже строчка выдает ошибку, ApiError: [30] This profile is private, обойдем try except
        try:
            profile_photos = self.session_api_user.photos.get(owner_id=profile_id_int,
                                                              extended=1, album_id='profile')['items']
            most_liked = sorted(profile_photos, key=lambda likes: likes['likes']['count'], reverse=True)[:3]
            all_photo_attachments = []
            for el in most_liked:
                all_photo_attachments.append(f'photo{profile_id_int}_{el["id"]}')
            # выведем в консоли для контроля почему отбросили
            print(all_photo_attachments)
            if len(all_photo_attachments) < 3:
                return False
            else:
                return all_photo_attachments
        except:
            # если аккаунт закрыт, выдаем тоже False
            return False







# не удалять строчки внизу, используются
some_choice = vk_choice(os.getenv('token_user'), os.getenv('token_community'))
user_need = User_vk(os.getenv('token_user'))

#
# some_choice.find_id_using_screen('s.hussey')

# some_choice.get_city_id('москва')
# some_choice.send_info_in_bot()

# some_choice.get_rel_people_by_id(705169327)

# some_choice.get_top_3_foto(705169327)

# print(some_choice.get_all_available_people(1))

# data = some_choice.get_all_available_people_2(1, 30, 'москва')
# pprint(data)
# pprint(data)