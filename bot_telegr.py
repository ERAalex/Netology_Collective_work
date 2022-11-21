import pymongo
from pymongo import MongoClient
from pprint import pprint
import telebot
from telebot import types
import random
import datetime
from PIL import Image, ImageDraw
import os
import time


client = MongoClient('localhost', 27017)
db = client['vk_finder']
series_collection = db['users_vk']


#### https://ru.stackoverflow.com/questions/1103332/%D0%90%D0%B2%D1%82%D0%BE%D1%80%D0%B8%D0%B7%D0%B0%D1%86%D0%B8%D1%8F-%D0%B2-%D1%82%D0%B5%D0%BB%D0%B5%D0%B3%D1%80%D0%B0%D0%BC%D0%BC-%D0%B1%D0%BE%D1%82%D0%B5-%D0%BD%D0%B0-python

tb = telebot.TeleBot('.....token')


def start_telebot():

    @tb.message_handler(commands=['start', 'go'])
    def start_handler(message):
        msg = tb.send_message(message.chat.id, "Привет, отправь логин и пароль")
        tb.register_next_step_handler(msg, auth)

    def auth(message):
        data = message.text.split()  # создаем список ['логин', 'пароль']
        print(data)

        # Ищем по базе Монго есть такой человек или нет
        check = series_collection.find_one({  # проверяем наличие в базе комбинации логина и пароля
            'name': str(data[0]),
            'last_name': str(data[1]),
        })

        if check is None:  # если такой комбинации не существует, ждём команды /start Опять
            tb.send_message(message.chat.id, r'Неправильно введен логин\пароль')

        else:  # а если существует, переходим к следующему шагу
            msg = tb.send_message(message.chat.id, 'Что будем делать?')
            # tb.register_next_step_handler(msg, next_step_func)

        # теперь у нас есть имя, фамилия (надо переделать под пароль) для дальнейшего взаимодействия с базой и поиска


    tb.polling(none_stop=True)


start_telebot()

