import vk_api
from random import randint

from config import token_user, token_community


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


class vk_choice:
    def __init__(self, vk_token_user, vk_token):
        self.vk_token_user = vk_token_user
        self.vk_token = vk_token
        self.vk_s = vk_api.VkApi(token=vk_token)
        self.vk_u = vk_api.VkApi(token=vk_token_user)
        self.session_api_user = self.vk_u.get_api()
        self.session_api = self.vk_s.get_api()
        self.count = 0


    def get_city_id(self, name_city):
        '''на вход получаем название города, на выход даем его номер нужный для поиска по city = ...'''
        result = self.session_api_user.database.getCities(q=name_city, count=1)
        id_city = ''
        for items in result['items']:
            id_city = items['id']
        return id_city


    def get_rel_people_by_id(self, id):
        people = self.session_api_user.users.get(user_ids=id,
                                                    fields='domain, relation, personal, city, about, music, '
                                                                          'sex, books,  bdate, birth_year, activities,'
                                                                          'interests, education, games')

        people_dict = {}

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

            try:
                people_dict['photo'] = self.get_top_3_foto(id)
            except:
                people_dict['photo'] = ['аккаунт закрыт для выборки фото']

            return people_dict



    def get_all_available_people(self, gender, age, name_city):
        '''функция, которая ищет людей вк по параметрам пользователя, выводит в виде списка словарей'''
        city = vk_choice.get_city_id(self, name_city)
        people = self.session_api_user.users.search(sort=0, blacklisted=0, is_closed=False,
                                                    sex=gender, offset=100,
                                                    blacklisted_by_me=0, birth_year=(2022 - int(age)),
                                                    has_photo=1, count=100, city_id=city,
                                                    fields='domain, relation, personal, city, about, '
                                                           'sex, books, bdate, birth_year, activities, '
                                                           'interests, education, movies, games, music')

        filtred_people = []
        for el in people['items']:
            try:
                photos = self.session_api_user.photos.get(owner_id=el['id'], extended=1, album_id='profile')['items']
                if len(photos) >=3:
                    if 'city' in el and el['city']['title'] == name_city.title():
                        if 'books' not in el:
                            el['books'] == ''
                        if 'activities' not in el:
                            el['activities'] == ''
                        if 'music' not in el:
                            el['music'] == ''
                        if 'movies' not in el:
                            el['movies'] == ''
                        if 'interests' not in el:
                            el['interests'] == ''
                        if 'games' not in el:
                            el['games'] == ''
                        filtred_people.append(el)

                    else:
                        # нет города в описании
                        pass

                else:
                    # меньше 3 фоток
                    pass

            except:
                # закрыт профиль
                pass
        return filtred_people


    def get_top_3_foto(self, id):
        '''функция по сохранению 3 фото из id'''
        profile_photos = self.session_api_user.photos.get(owner_id=id, extended=1, album_id='profile')['items']

        most_liked = sorted(profile_photos, key=lambda likes: likes['likes']['count'], reverse=True)[:3]
        all_photo_attachments = []
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



some_choice = vk_choice(token_user, token_community)
user_need = User_vk(token_user)