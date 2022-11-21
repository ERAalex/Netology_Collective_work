import random, vk_api, vk_folder
from vk_api.keyboard import VkKeyboard, VkKeyboardColor
from vk_api.utils import get_random_id
from vk_api.bot_longpoll import VkBotLongPoll, VkBotEventType
from vk_api.longpoll import VkLongPoll, VkEventType
import json
import os


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
            nb[i][k] = {'action': {'type': 'text', 'payload': '{\'button\': \'' + '1' + '\'}', 'label': f'{text}'}, 'color': f'{color}'}
    first_keyboard = {'one_time': False, 'buttons': nb, 'inline': False}
    first_keyboard = json.dumps(first_keyboard, ensure_ascii=False).encode('utf-8')
    first_keyboard = str(first_keyboard.decode('utf-8'))
    return first_keyboard

def sender (id, text, key):
    vk_session.method('messages.send', {'user_id': id, 'message': text, 'random_id': 0, 'keyboard': key})

# пустая клваиатура, чтобы ее передавать.
clear_key = get_keyboard(
    []
)


menu_key = get_keyboard([
    [('Информация', 'синий')]
])

user = User(100, 'some')

users = [user]

for event in longpoll.listen():
    if event.type == VkEventType.MESSAGE_NEW:
        if event.to_me:

            id = event.user_id
            msg = event.text.lower()

            if msg:
                sender(id, 'hello', clear_key)


            if msg == 'start':
                flag = 0
                for user in users:
                    if user.id == id:
                        flag = 1
                        user.mode = 'decision_start'
                        break
                    if flag == 0:
                        users.append(User(id, 'decision_start'))
                        sender(id, 'Что будем делать? Наберите цифру: \n'
                                   '1- Поиск человека \n'
                                   '2- Посмотреть БД \n'
                                   '3- Удалить из БД \n'
                                   '\n'
                                   '\n'
                                   ' ', clear_key)
                    elif flag == 1:
                        for user in users:
                            if user.id == id:
                                if not(user.mode in ['reg1', 'reg2']):
                                    sender(id, 'Зарегестрируйтесь в боте. \nВведите свое имя: ', clear_key)

            else:
                for user in users:
                    if user.id == id:
                        #
                        if user.mode == 'decision_start':
                            if str(msg) == '1':
                                sender(id, 'Начнем поиск человека, '
                                           'смотрим по настраиваемым параметрам? Да/ Нет: ', clear_key)
                                user.mode = '1_decision_parametrs'

                        elif user.mode == 'reg2':
                            try:
                                user.age = int(msg)
                                sender(id, 'Вы успешно зарегестрировались!', menu_key)
                                user.mode = 'menu'
                            except:
                                sender(id, 'Значение возраста не подходит!', clear_key)




#
#
# user = User(100, 'some')
#
# users = [user]
#
#             for event in longpoll.listen():
#                 if event.type == VkEventType.MESSAGE_NEW:
#                     if event.to_me:
#
#                         id = event.user_id
#                         msg = event.text.lower()
#
#                         if msg:
#                             sender(id, 'hello', clear_key)
#
#                         if msg == 'start':
#                             flag = 0
#                             for user in users:
#                                 if user.id == id:
#                                     flag = 1
#                                     break
#                                 if flag == 0:
#                                     users.append(User(id, 'reg1'))
#                                     print(users)
#                                     sender(id, 'Зарегестрируйтесь в боте. \nВведите свое имя: ', clear_key)
#                                 elif flag == 1:
#                                     for user in users:
#                                         if user.id == id:
#                                             if not (user.mode in ['reg1', 'reg2']):
#                                                 sender(id, 'Зарегестрируйтесь в боте. \nВведите свое имя: ', clear_key)
#
#                         else:
#                             for user in users:
#                                 if user.id == id:
#                                     # если человек прислал нам сообщение и его статус reg1 значит он нам прислал имя
#                                     if user.mode == 'reg1':
#                                         user.name = msg.title()
#                                         sender(id, 'Введите свой возраст: ', clear_key)
#                                         user.mode = 'reg2'
#
#                                     elif user.mode == 'reg2':
#                                         try:
#                                             user.age = int(msg)
#                                             sender(id, 'Вы успешно зарегестрировались!', menu_key)
#                                             user.mode = 'menu'
#                                         except:
#                                             sender(id, 'Значение возраста не подходит!', clear_key)
#





            #
            # vars1 = ['Привет', 'Ку', 'Хай', 'Хеллоу', 'Хелп']
            # vars2 = ['Клавиатура', 'клавиатура']
            # check_words = [vars1, vars2, '1', '2']
            #
            # if event.text == 'старт':
            #     Lsvk.messages.send(
            #         user_id=event.user_id,
            #         message=message_start,
            #         random_id=get_random_id()
            #     )
            #     break
            #
            #
            # if event.text == '1':
            #     if event.from_user:
            #         Lsvk.messages.send(
            #             user_id=event.user_id,
            #             message='Введите параметры, название города где живет: "город - Москва"',
            #             random_id=get_random_id()
            #             )
            #         break
            #
            #
            # if 'город' in str(event.text):
            #     print('yes')
            #     if event.from_user:
            #         Lsvk.messages.send(
            #             user_id=event.user_id,
            #             message=f'Вы ввели: {event.text}, кого Вы ищете? напишите: М или Ж',
            #             random_id=get_random_id()
            #         )
            #         city_received = str(event.text)
            #         print(city_received)
            #     break
            #
            #
            #
            #
            # if event.text in vars2:
            #     if event.from_user:
            #         Lsvk.messages.send(
            #             user_id = event.user_id,
            #             random_id = get_random_id(),
            #             keyboard = keyboard.get_keyboard(),
            #             message = 'Держи'
            #             )
            #
            #
            #
            #
            #
            #
