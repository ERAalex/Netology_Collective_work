import vk_api
import os
from pprint import pprint
import datetime
from sqlalchemy import select, insert
from random import randint



class vk_choice:
    def __init__(self, vk_token_user):
        self.vk_token_user = vk_token_user
        # self.vk_token = vk_token
        # self.vk_s = vk_api.VkApi(token=vk_token)
        self.vk_u = vk_api.VkApi(token=vk_token_user)
        self.session_api_user = self.vk_u.get_api()
        # self.session_api = self.vk_s.get_api()


    def get_city_id(self, name_city):
            '''на вход получаем название города, на выход даем его номер нужный для поиска по city = ...'''
            result = self.session_api_user.database.getCities(q=name_city, count=1)
            id_city = ''
            for items in result['items']:
                id_city = items['id']
            return id_city

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

# a = vk_choice(os.getenv('token_user'))
#
# pprint(a.get_all_available_people(1, 30, 'Челябинск', 100))
