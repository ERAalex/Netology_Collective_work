from vk_folder.bot import start_run_bot
from DB.db import run_db


if __name__ == '__main__':

    '''при первом включении запустите по очереди функции

    test - создание и подключение к базе данных 
    create - создание всех необходимых таблиц

       далее просто закомментируйте эти функции'''

    test = run_db.create_database()
    create = run_db.create_table()

    start_run_bot()