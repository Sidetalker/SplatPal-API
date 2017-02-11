
import uuid

class SplatService(object):

    def __init__(self, database):
        self.database = database

    def create_api_key(self, name, key=None):

        if key is None:
            key = uuid.uuid4()
            key = str(key)

        result = self.database.APIKeys.insert_one({'name': name, 'key': key})
        return str(result.inserted_id)

    def _construct_optional_query(self, dic):
        query_filter = {}
        for key, value in dic.items():
            if value is not None:
                query_filter[key] = value
        return query_filter

    def delete_api_key(self, doc_id=-1, name=None, key=None):
        query_filter = self._construct_optional_query({'_id': doc_id, 'name': name, 'key': key})
        return self.database.APIKeys.find_one_and_delete(query_filter)
