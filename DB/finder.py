from db import run_db 
from fuzzywuzzy import fuzz


def get_match_rating(self, user_vk_id: str, found_persons: list):
    '''На вход принимает список словарей!'''
    data_user = run_db.search_user_from_db(user_vk_id)
    filtered_persons = []
    for person in found_persons:
        count = 0
        count += fuzz.token_sort_ratio(data_user['books'], person['books'])
        count += fuzz.token_sort_ratio(data_user['activities'], person['activities'])
        count += fuzz.token_sort_ratio(data_user['music'], person['music'])
        count += fuzz.token_sort_ratio(data_user['movies'], person['movies'])
        count += fuzz.token_sort_ratio(data_user['interests'], person['interests'])
        count += fuzz.token_sort_ratio(data_user['games'], person['games'])
        filtered_persons.append([count, person])
    filtered_persons = sorted(filtered_persons, key=lambda x: x[0], reverse=True)
    result = [person[1] for person in filtered_persons]
    return result
