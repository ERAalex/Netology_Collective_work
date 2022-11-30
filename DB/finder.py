from db import run_db 
from fuzzywuzzy import fuzz

test_user_info = run_db.search_user_from_db('id459484548495')
test_selected_info = run_db.search_selected_from_db('id45655495')


def get_coincidences_by_movies(user_movies, selected_movies):
    ratio = fuzz.token_sort_ratio(user_movies, selected_movies)
    return ratio

def get_coincidences_by_music(user_music, selected_music):
    ratio = fuzz.token_sort_ratio(user_music, selected_music)
    return ratio

def get_coincidences_by_books(user_books, selected_books):
    ratio = fuzz.token_sort_ratio(user_books, selected_books)
    return ratio


print(get_coincidences_by_movies(test_user_info['movies'], test_selected_info['movies']))
print()
print(get_coincidences_by_music(test_user_info['music'], test_selected_info['music']))
print()
print(get_coincidences_by_books(test_user_info['books'], test_selected_info['books']))
print()

