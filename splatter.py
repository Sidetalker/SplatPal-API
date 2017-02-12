
import uuid
from bson.objectid import ObjectId

class SplatService(object):

    def __init__(self, db_client):
        self.db_client = db_client
        self.database = db_client.get_default_database()

    def create_api_key(self, name, key=None):

        if key is None:
            key = uuid.uuid4()
            key = str(key)

        result = self.database.APIKeys.insert_one({'name': name, 'key': key})
        return str(result.inserted_id)

    def __construct_optional_query(self, dic, doc_id=None):
        query_filter = {}
        for key, value in dic.items():
            if value is not None:
                query_filter[key] = value
        if doc_id is not None:
            query_filter['_id'] = ObjectId(doc_id)
        return query_filter

    def delete_api_key(self, doc_id=None, name=None, key=None):
        query_filter = self.__construct_optional_query({'name': name, 'key': key}, doc_id)
        return self.database.APIKeys.find_one_and_delete(query_filter)

    def find_api_key(self, doc_id=None, name=None):
        query_filter = self.__construct_optional_query({'name': name}, doc_id)
        return self.database.APIKeys.find_one(query_filter)

    def has_api_key(self, key):
        return self.database.APIKeys.find_one({'key': key}) is not None

    def find_all_api_keys(self):
        return self.database.APIKeys.find()

    def update_api_key(self, doc_id, key=None, name=None):
        return self.database.APIKeys.find_one_and_update({'_id': ObjectId(doc_id)}, {'$set': {'key': key, 'name': name}})