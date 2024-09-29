from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
from AAB import Vars, LOG

mongo_client = MongoClient(Vars["database_url"], server_api=ServerApi('1'))
database = mongo_client.get_database('AAB')
last_added = database.get_collection('last_added')
new_db = database.get_collection('new_db')
remain = database.get_collection('remain')
worker = database.get_collection('worker')
files = database.get_collection('files')


def get_last_hash():
    data = last_added.find_one({'_id': 1})
    return data['hash'] if data else None


def add_hash(hash_value):
    if get_last_hash() is None:
        last_added.insert_one({"_id": 1, 'hash': hash_value})
    else:
        last_added.update_one({'_id': 1}, {"$set": {'hash': hash_value}}, upsert=True)


def is_new_db():
    data = new_db.find_one({'_id': 1})
    if not data:
        new_db.insert_one({'_id': 1})
        return True
    return False


def add_remain_anime(remaining: list):
    remain_data = remain.find_one({'_id': 1})
    if remain_data is None:
        remain.insert_one({'_id': 1, 'list': remaining})
    else:
        main_list = remain_data['list']
        main_list.extend(remaining)
        remain.update_one({'_id': 1}, {'$set': {'list': main_list}}, upsert=True)


def get_remain_anime() -> list:
    doc = remain.find_one({'_id': 1})
    return doc['list'] if doc else []


def update_remain_anime(list_of_anime: list):
    remain.update_one({"_id": 1}, {"$set": {'list': list_of_anime}}, upsert=True)


def is_working() -> bool:
    doc = worker.find_one({'_id': 1})
    if doc is None:
        worker.insert_one({'_id': 1, 'working': False})
        return False
    return doc['working']


def update_worker(param: bool):
    worker.update_one({'_id': 1}, {"$set": {'working': param}}, upsert=True)


def add_file(name: str, hash_value: str, message_id: int):
    files.insert_one({"name": name, 'hash': hash_value, "message_id": message_id})


def get_file_by_hash(hash_value: str) -> [None, dict]:
    return files.find_one({"hash": hash_value})


def rev_and_del(lst: list) -> list:
    if lst:
        lst.reverse()
        lst.pop()
        lst.reverse()
    return lst


def remove_anime_from_remain():
    data = get_remain_anime()

    if data and 'quality' in data[0] and len(data[0]['quality']) >= 1:
        new_list = rev_and_del(data)
        update_remain_anime(new_list)
    else:
        if data:
            main_dict = data[0]
            try:
                new_data = rev_and_del(data)
                new_data.reverse()
                new_data.append({
                    'name': main_dict['name'],
                    'magnet': rev_and_del(main_dict['magnet']),
                    'hash': rev_and_del(main_dict['hash']),
                    'quality': rev_and_del(main_dict['quality']),
                    'title': rev_and_del(main_dict['title'])
                })
                new_data.reverse()
                update_remain_anime(new_data)
            except Exception as e:
                LOG.error(e)
