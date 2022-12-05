from vk_api.longpoll import VkEventType
from vk_folder.some_frases import iniciate_messages

from DB.db import run_db
from vk_folder.people_search import some_choice, user_need
from vk_folder.bot_settings import User, bot, people_search

from threading import Thread


users_class = []
check = []


def start_run(event):
    id = event.user_id

    if len(users_class) == 0:
        id_user_bot = User(id)
        users_class.append(id_user_bot)

    for item in users_class:
        if item.id != id:
            id_user_bot = User(id)
            users_class.append(id_user_bot)
        else:
            pass

    for item in users_class:
        if item.id not in check:
            check.append(item.id)

    data = people_search.get_user_info(id)
    run_db.add_user(data)
    user_find_from_db = run_db.search_user_from_db('id' + str(id))
    user_id_saved = user_find_from_db['id']
    msg = event.text.lower()

    if msg in iniciate_messages:
        bot.sender(id, 'hello', bot.clear_key_board())

    if msg == 'start':
        try:
            run_db.delete_user_mode(user_id_saved)
        except:
            pass
        bot.sender(id, 'Что будем делать? Наберите цифру: \n'
                        '1 - Посмотреть добавленные контакты \n'
                        '2 - Общий поиск людей(указать пол, возраст, город) \n'
                        'так же мы отсортируем выдачу по Вашим интересам (если будут)\n'
                        '\n'
                        ' ', bot.clear_key_board())

        run_db.add_user_mode(user_id_saved, 'start')

    else:
        for user in users_class:
            if user.id == id:
                if run_db.get_user_mode(user_id_saved) == 'start':
                    if str(msg) == '1':
                        bot.sender(id, 'Ваши контакты: Нажмите "Следующий" \n ',
                                    bot.menu_check_db_key_board())

                        run_db.update_user_mode(user_id_saved, 'db_check')
                        run_db.update_step_session(user_id_saved, 0)

                    if str(msg) == '2':
                        bot.sender(id, 'Для общего поиска людей выберите кого ищем \n ',
                                    bot.menu_sex_key_board())

                        run_db.update_user_mode(user_id_saved, 'menu_sex')

                elif run_db.get_user_mode(user_id_saved) == 'db_check':
                    data_us_bd = run_db.search_user_from_db('id' + str(id))
                    all_related = run_db.find_using_users_selected(data_us_bd['id'])
                    list_related = []
                    related_db_id_list = []

                    for item in all_related:
                        result_realted = run_db.search_selected_from_db_using_id(item)
                        related_db_id = result_realted['id']
                        check_deleted = run_db.get_id_deleted_selected(user_id_saved)

                        if related_db_id not in check_deleted:
                            related_db_id_list.append(related_db_id)
                            list_related.append(f'''{result_realted["name"]}  
                                                    {result_realted["last_name"]}
                                                    https://vk.com/{result_realted["vk_id"]}''')

                    if msg == 'следующий контакт':
                        step_now = run_db.get_step_ids_session(user_id_saved)
                        try:
                            bot.sender(id, f'{list_related[step_now]} \n ',
                                        bot.menu_check_db_key_board())

                            run_db.update_user_mode(user_id_saved, 'db_check')
                            run_db.update_step_session(user_id_saved, step_now + 1)
                        except:
                            bot.sender(id, 'Больше нет людей в базе, напишите start \n ',
                                        bot.clear_key_board())
                            run_db.update_user_mode(user_id_saved, 'db_check')

                    if msg == 'удалить контакт':
                        step_now = run_db.get_step_ids_session(user_id_saved)
                        bot.sender(id, 'Удален предыдущий выданный контакт из базы\n ',
                                    bot.menu_check_db_key_board())
            
                        run_db.mark_deleted_from_selected(user_id_saved, related_db_id_list[step_now - 1])
                        run_db.update_user_mode(user_id_saved, 'db_check')

                    if msg == 'искать людей':
                        bot.sender(id,
                                    'Переходим на поиск людей. Для общего поиска людей выберите '
                                    'кого ищем \n ',
                                    bot.menu_sex_key_board())

                        run_db.update_user_mode(user_id_saved, 'menu_sex')

                elif run_db.get_user_mode(user_id_saved) == 'menu_sex':
                    if msg == 'девушку':
                        bot.sender(id, 'Напишите возраст девушки, например: 27',
                                    bot.clear_key_board())
                        run_db.update_user_mode(user_id_saved, 'girl_find_age')
                        break

                    if msg == 'парня':
                        bot.sender(id, 'Напишите возраст парня, например: 27',
                                    bot.clear_key_board())
                        run_db.update_user_mode(user_id_saved, 'boy_find_age')
                        break

                if run_db.get_user_mode(user_id_saved) == 'girl_find_age':
                    try:
                        decision = int(msg)
                        if decision:
                            girl_decision_age = msg
                            run_db.add_user_choise_age(user_id_saved, girl_decision_age)

                            bot.sender(id, 'Введите город по которому искать, мы начнем поиск \n'
                                           'это может занять пару минут, что значительно ускорит \n'
                                           'дальнейший вывод',
                                        bot.clear_key_board())
                            run_db.update_user_mode(user_id_saved, 'girl_find_city')
                            break
                    except:
                        bot.sender(id, 'вы не ввели число, повторите ввод возраста девушки',
                                    bot.clear_key_board())
                        run_db.update_user_mode(user_id_saved, 'girl_find_age')

                if run_db.get_user_mode(user_id_saved) == 'girl_find_city':
                    if msg:
                        run_db.add_user_choise_city(user_id_saved, msg)
                        run_db.update_step_session(user_id_saved, 0)
                        resul_find_people_2 = some_choice.get_all_available_people \
                            (1, run_db.get_users_choise_age(user_id_saved),
                             run_db.get_users_choise_city(user_id_saved))

                        resul_find_people = bot.get_match_rating('id' + str(id), resul_find_people_2)

                        run_db.add_user_choise_ids(user_id_saved, resul_find_people)
    
                        while_true = True
                        while while_true == True:
                            result_1 = run_db.get_users_choise_ids(user_id_saved)
                            result_2 = result_1.split(',')
                            step_now = run_db.get_step_ids_session(user_id_saved)
                            result_next = result_2[step_now]
                            run_db.update_step_session(user_id_saved, step_now + 1)
                            list_ban = run_db.get_all_vk_id_of_banned(user_id_saved)
                            check_id_in_related_already = run_db.find_using_users_selected(user_id_saved)
                            banned_already_in_related = []
                            for item in check_id_in_related_already:
                                result = run_db.search_selected_from_db_using_id(item)
                                banned_already_in_related.append(result['vk_id'][2:])

                            if result_next in list_ban or result_next in banned_already_in_related:
                                print('в бане или уже добавлен в БД')
                            else:
                                result = user_need.get_user_info(result_next)
                                bot.sender(id,
                                            f'{result["name"]}  {result["last_name"]} \n'
                                            f' {some_choice.send_info_in_bot(id, result_next)}',
                                            bot.menu_find_people_key_board())
                                run_db.update_user_mode(user_id_saved, 'girl_find_run')
                                while_true = False

                if run_db.get_user_mode(user_id_saved) == 'girl_find_run':
                    if msg == 'следующий человек':

                        while_true = True
                        while while_true == True:
                            result_1 = run_db.get_users_choise_ids(user_id_saved)
                            result_2 = result_1.split(',')
                            step_now = run_db.get_step_ids_session(user_id_saved)
                            if step_now >= len(result_2):
                                bot.sender(id, 'Что будем делать? Наберите цифру: \n'
                                               '1 - Посмотреть добавленные контакты \n'
                                               '2 - Общий поиск людей(указать пол, возраст, город) \n'
                                               'так же мы отсортируем выдачу по Вашим интересам (если будут)\n'
                                               '\n'
                                                ' ', bot.clear_key_board())
                                run_db.update_user_mode(user_id_saved, 'start')
                                while_true = False
                            else:
                                result_next = result_2[step_now]
                                run_db.update_step_session(user_id_saved, step_now + 1)
                                list_ban = run_db.get_all_vk_id_of_banned(user_id_saved)
                                check_id_in_related_already = run_db.find_using_users_selected(user_id_saved)
                                banned_already_in_related = []
                                for item in check_id_in_related_already:
                                    result = run_db.search_selected_from_db_using_id(item)
                                    banned_already_in_related.append(result['vk_id'][2:])

                                if result_next in list_ban or result_next in banned_already_in_related:
                                    print('в бане или уже добавлен в БД')
                                else:
                                    result = user_need.get_user_info(result_next)
                                    bot.sender(id,
                                                f'{result["name"]}  {result["last_name"]} \n'
                                                f' {some_choice.send_info_in_bot(id, result_next)}',
                                                bot.menu_find_people_key_board())
                                    run_db.update_user_mode(user_id_saved, 'girl_find_run')
                                    while_true = False

                    if msg == 'больше не показывать':
                        result_1 = run_db.get_users_choise_ids(user_id_saved)
                        result_2 = result_1.split(',')
                        step_now = run_db.get_step_ids_session(user_id_saved)
                        result_next = result_2[step_now - 1]
                        run_db.add_banned(user_id_saved, result_next)

                        bot.sender(id, 'Данный пользователь больше не будет появляться в рекомендациях'
                                        ' \n ', bot.menu_find_people_key_board())
                        run_db.update_user_mode(user_id_saved, 'girl_find_run')

                    if msg == 'добавить в контакты':
                        result_1 = run_db.get_users_choise_ids(user_id_saved)
                        result_2 = result_1.split(',')
                        step_now = run_db.get_step_ids_session(user_id_saved)
                        result_next = result_2[step_now - 1]

                        data_people_selected = some_choice.get_rel_people_by_id(result_next)
                        run_db.add_selected(data_people_selected)
                        info = run_db.search_selected_from_db('id' + str(result_next))
                        run_db.mark_users_selected(user_id_saved, info['id'])

                        bot.sender(id, f'Вы добавили {data_people_selected["name"]} '
                                        f'{data_people_selected["last_name"]} '
                                        'в Базу данных \n ', bot.menu_find_people_key_board())

                        run_db.update_user_mode(user_id_saved, 'girl_find_run')

                if run_db.get_user_mode(user_id_saved) == 'boy_find_age':
                    try:
                        decision = int(msg)
                        if decision:
                            boy_decision_age = msg
                            run_db.add_user_choise_age(user_id_saved, boy_decision_age)

                            bot.sender(id, 'Введите город в котором искать, мы начнем поиск \n'
                                            'это может занять пару минут, что значительно ускорит \n'
                                            'дальнейший вывод',
                                        bot.clear_key_board())
                            run_db.update_user_mode(user_id_saved, 'boy_find_city')
                            break
                    except:
                        bot.sender(id, 'вы не ввели число, повторите ввод возраста парня',
                                    bot.clear_key_board())
                        run_db.update_user_mode(user_id_saved, 'boy_find_age')

                if run_db.get_user_mode(user_id_saved) == 'boy_find_city':
                    if msg:
                        run_db.add_user_choise_city(user_id_saved, msg)
                        run_db.update_step_session(user_id_saved, 0)
                        resul_find_people_2 = some_choice.get_all_available_people \
                            (2, run_db.get_users_choise_age(user_id_saved),
                             run_db.get_users_choise_city(user_id_saved))

                        resul_find_people = bot.get_match_rating('id' + str(id), resul_find_people_2)
                        run_db.add_user_choise_ids(user_id_saved, resul_find_people)

                        while_true = True
                        while while_true == True:
                            result_1 = run_db.get_users_choise_ids(user_id_saved)
                            result_2 = result_1.split(',')
                            step_now = run_db.get_step_ids_session(user_id_saved)
                            result_next = result_2[step_now]
                            run_db.update_step_session(user_id_saved, step_now + 1)
                            list_ban = run_db.get_all_vk_id_of_banned(user_id_saved)

                            if result_next in list_ban:
                                print('в бане')
                            else:
                                result = user_need.get_user_info(result_next)
                                bot.sender(id,
                                            f'{result["name"]}  {result["last_name"]} \n'
                                            f' {some_choice.send_info_in_bot(id, result_next)}',
                                            bot.menu_find_people_key_board())
                                run_db.update_user_mode(user_id_saved, 'boy_find_run')
                                while_true = False

                if run_db.get_user_mode(user_id_saved) == 'boy_find_run':
                    if msg == 'следующий человек':

                        while_true = True
                        while while_true == True:
                            result_1 = run_db.get_users_choise_ids(user_id_saved)
                            result_2 = result_1.split(',')
                            step_now = run_db.get_step_ids_session(user_id_saved)
                            if step_now >= len(result_2):
                                bot.sender(id, 'Что будем делать? Наберите цифру: \n'
                                               '1 - Посмотреть добавленные контакты \n'
                                               '2 - Общий поиск людей(указать пол, возраст, город) \n'
                                               'так же мы отсортируем выдачу по Вашим интересам (если будут)\n'
                                               '\n'
                                               ' ', bot.clear_key_board())
                                run_db.update_user_mode(user_id_saved, 'start')
                                while_true = False
                            else:
                                result_next = result_2[step_now]
                                run_db.update_step_session(user_id_saved, step_now + 1)
                                list_ban = run_db.get_all_vk_id_of_banned(user_id_saved)

                                if result_next in list_ban:
                                    print('в бане')
                                else:
                                    result = user_need.get_user_info(result_next)
                                    bot.sender(id,
                                                f'{result["name"]}  {result["last_name"]} \n'
                                                f' {some_choice.send_info_in_bot(id, result_next)}',
                                                bot.menu_find_people_key_board())
                                    run_db.update_user_mode(user_id_saved, 'boy_find_run')
                                    while_true = False

                    if msg == 'больше не показывать':
                        result_1 = run_db.get_users_choise_ids(user_id_saved)
                        result_2 = result_1.split(',')
                        step_now = run_db.get_step_ids_session(user_id_saved)
                        result_next = result_2[step_now]
                        run_db.add_banned(user_id_saved, result_next)
                        bot.sender(id, 'Данный пользователь больше не будет появляться в рекомендациях'
                                        ' \n ', bot.menu_find_people_key_board())
                        run_db.update_user_mode(user_id_saved, 'boy_find_run')

                    if msg == 'добавить в контакты':
                        result_1 = run_db.get_users_choise_ids(user_id_saved)
                        result_2 = result_1.split(',')
                        step_now = run_db.get_step_ids_session(user_id_saved)
                        result_next = result_2[step_now - 1]

                        data_people_selected = some_choice.get_rel_people_by_id(result_next)
                        run_db.add_selected(data_people_selected)
                        info = run_db.search_selected_from_db('id' + str(result_next))
                        run_db.mark_users_selected(user_id_saved, info['id'])

                        bot.sender(id, f'Вы добавили {data_people_selected["name"]} '
                                        f'{data_people_selected["last_name"]} '
                                        'в Базу данных \n ', bot.menu_find_people_key_board())

                        run_db.update_user_mode(user_id_saved, 'boy_find_run')

def start_run_bot():
    for event in bot.longpoll.listen():
        if event.type == VkEventType.MESSAGE_NEW:
            if event.to_me:
                Thread(target=start_run, args=(event, ), daemon=True).start()