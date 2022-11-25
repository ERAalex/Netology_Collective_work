import pymongo
from pymongo import MongoClient



# Create the client
client = MongoClient('localhost', 27017)
# Connect to our database
db = client['vk_finder']
# Fetch our series collection
series_collection = db['users_vk']



def insert_document(user_id):
    """ Function to insert a document into a collection and
    return the document's id.
    """
    # получаем поиск человека(словарь) из модуля vk_finder
    data = find_data_person(user_id)
    # заполняем через словарь запрос в базу
    series_collection.insert_one({
        "id_vk": f"{user_id}",
        "name": f"{data['user_name']}",
        "last_name": f"{data['user_lastname']}",
        "bdate": f"{data['user_bdate']}",
        "sex": f"{data['user_sex']}",
        "city": f"{data['user_city']}",
        "relation": f"{data['user_relation']}",
        "music": f"{data['user_music']}",
        "books": f"{data['user_books']}",
        "persons_find": []
    })




### example  ###

# new_person = {
#     "name": "Митя",
#     "last_name": "Самцов",
#     "year": 1989,
#     "sex": "мужчина",
#     "city": "Самцов",
#     "girls": [
#     {
#         "user_id": "1",
#         "user": "Sveta",
#         "age": 30
#     },
#     {
#             "user_id": "2",
#             "user": "Tania",
#             "age": 33
#     }],
# }
#
# print(insert_document(series_collection, new_person))


def find_document(collection, elements, multiple=False):
    """ Function to retrieve single or multiple documents from a provided
    Collection using a dictionary containing a document's elements.
    """
    if multiple:
        results = collection.find(elements)
        return [r for r in results]
    else:
        return collection.find_one(elements)

## example  ###

# result_find = find_document(series_collection, {"id_vk": 558826})
# print(result_find)
# result_need = result_find["girls"]
# print(result_need[0])



def update_document(collection, query_elements, new_values):
    """ Function to update a single document in a collection.
    """
    collection.update_one(query_elements, {'$set': new_values})

### example  ###

# result_update = update_document(series_collection, {'name': 'Юля'}, {'year': '1989'})


def delete_document(collection, query):
    """ Function to delete a single document from a collection.
    """
    collection.delete_one(query)

### example  ###

# delete_document(series_collection, {'name': 'Петя'})




###### ДОБАВЛЕНИЕ СЛОВАРЯ В НАШ СПИСОК NESTED, ДОБАВЛЕНИЕ НОВОЙ ДЕВУШКИ ########
#
# series_collection.update_one(
#     {"name": "Митя"},
#     {"$addToSet": {"girls": {
#             "user_id": "3",
#             "user": "Elena",
#             "age": 41
#
#     }}}, upsert=True)





###### ИЗМЕНЕНИЕ ДАННЫХ ВЛОЖЕННОЙ ДЕВУШКИ, НАПРИМЕР ВОЗРАСТА ########

# series_collection.update_one(
#     {"name": "Митя", "girls.user_id": "2"},
#     {"$set": {"girls.$.age": 50}}, upsert=True)


# Пример поиска по списку, вывод данных по девушкам.
# result_find = find_document(series_collection, {"name": "Митя"})
# result_need = result_find["girls"]
#
# for item in result_need:
#     print(item)



