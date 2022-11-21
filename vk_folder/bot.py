import random, vk_api, vk
from vk_api.keyboard import VkKeyboardColor, VkKeyboard
from vk_api.utils import get_random_id
from vk_api.longpoll import VkLongPoll, VkEventType
import json
from vk_folder.some_frases import iniciate_messages
from db_mongo import find_document, series_collection, insert_document
import os

vk_token = os.getenv('token')

vk_s = vk_api.VkApi(token=vk_token)
session_api = vk_s.get_api()

class Bot:

    # начальные параметры для работы бота
    def __init__(self, token):
        self.token = token
        self.vk_session = vk_api.VkApi(token=token)
        self.longpoll = VkLongPoll(self.vk_session)
        self.vk = self.vk_session.get_api()

    # модуль шаблон для отправки ответа, нам нужно только вписать текущий event и сообщение
    def sender(self, event, message: str):
        self.vk.messages.send(
            user_id=event.user_id,
            message=message,
            random_id=get_random_id(),
            keyboard=self.get_keyboard()
        )

    # создание кнопки
    def get_button(self, text, color):
        return {
            "action": {
                "type": "text",
                "payload": "{\"button\": \"" + "1" + "\"}",
                "label": f"{text}"
            },
            "color": f"{color}"
        }


    # кнопка работает только вкупе с клавиатурой, создаем окончательно кнопку
    def get_keyboard(self):
        self.keyboard = {
            "one_time": True,
            "buttons": [
                [self.get_button('Начать поиск', 'positive'), self.get_button('Посмотреть текущий список', 'positive')],
                [self.get_button('ивет', 'positive'), self.get_button('В начало', 'positive')]
            ]
        }

        self.keyboard = json.dumps(self.keyboard, ensure_ascii=False).encode('utf-8')  # надо передать в json
        self.keyboard = str(self.keyboard.decode('utf-8'))
        return self.keyboard


    def check_user(self, user_id):
        result = find_document(series_collection, {'id_vk': str(user_id)})
        print(result)

        # если такого человека нет в БД, закидываем туда через модули
        if result == None:
            insert_document(user_id)
        else:
            pass


#cамая главная часть, работа бота
    def start_run(self):
        for event in self.longpoll.listen():
            if event.type == VkEventType.MESSAGE_NEW and event.to_me and event.text:
                msg = str(event.text)
                user_id = event.user_id
                # проверяем есть ли в базе, если нет, создаем
                self.check_user(user_id)

                if msg.lower() in iniciate_messages:
                    if event.from_user:
                        self.sender(event, message='Привет! Начнем? Напиши - старт')


                if msg.lower() == 'старт':
                    if event.from_user:
                        self.sender(event, message='ну чтоже')