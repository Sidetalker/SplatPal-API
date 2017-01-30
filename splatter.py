
import uuid
from pymongo import MongoClient

api_key_length = 30


class SplatterService(object):

    def __init__(self, database):
        self.database = database

    def create_api_key(self, name, key=None):

        if key is not None and len(str(key)) != api_key_length:
            raise ValueError("API key must be %s characters long")

        if key is None:
            key = uuid.uuid4()
            key = str(key)[:30]

        result = self.database.APIKeys.insert_one({'name': name, 'key': key})
        return str(result.inserted_id)

    def delete_api_key(self, doc_id=-1, name=None, key=None):
        query_filter = {'_id': doc_id}
        if name is not None:
            query_filter['name'] = name
        if key is not None:
            query_filter['key'] = key

        return self.database.APIKeys.find_one_and_delete(query_filter)
