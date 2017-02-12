#!/usr/bin/env python

"""Tests for the Flask Heroku template."""

import unittest
from app import app
from pymongo import MongoClient
from pymongo.errors import ConnectionFailure
from splatter import SplatService

test_database_name = 'splatpal_test'

class TestApp(unittest.TestCase):

    # setup the service on class init
    @classmethod
    def setUpClass(cls):
        cls.splat_service = cls._create_test_service()
        cls.splat_service.db_client.drop_database(test_database_name)

    @classmethod
    def _create_test_service(cls):
        mongodb_uri = 'mongodb://localhost:27017/' + test_database_name
        database = MongoClient(mongodb_uri)
        try:
            database.admin.command('ismaster')
        except ConnectionFailure:
            print("Unable to connect to Mongo client at URI: %s", mongodb_uri)
            quit()
        return SplatService(database)

    def setUp(self):
        self.app = app.test_client()
        self.app.splat_service = self.splat_service

    def test_home_page_works(self):
        rv = self.app.get('/')
        self.assertTrue(rv.data)
        self.assertEqual(rv.status_code, 200)

    def test_about_page_works(self):
        rv = self.app.get('/about/')
        self.assertTrue(rv.data)
        self.assertEqual(rv.status_code, 200)

    def test_default_redirecting(self):
        rv = self.app.get('/about')
        self.assertEqual(rv.status_code, 301)

    def test_404_page(self):
        rv = self.app.get('/i-am-not-found/')
        self.assertEqual(rv.status_code, 404)

    def test_static_text_file_request(self):
        rv = self.app.get('/robots.txt')
        self.assertTrue(rv.data)
        self.assertEqual(rv.status_code, 200)
        rv.close()

    def test_create_and_find_api_key(self):
        api_key_name = 'testApiKey'
        doc_id = self.splat_service.create_api_key(api_key_name)
        self.assertIsNotNone(doc_id)

        all_keys = self.splat_service.find_all_api_keys()
        self.assertIsNotNone(all_keys)

        api_key = self.splat_service.find_api_key(doc_id=doc_id)
        self.assertEqual(api_key['name'], api_key_name)
        self.assertIsNotNone(api_key['key'])

        same_api_key = self.splat_service.find_api_key(name=api_key_name)
        self.assertEqual(api_key, same_api_key)

        different_key_id = self.splat_service.create_api_key("OtherKeyName")
        different_key = self.splat_service.find_api_key(different_key_id)
        self.assertNotEqual(same_api_key, different_key)

        found_by_name = self.splat_service.find_api_key(name=different_key['name'])
        self.assertEqual(found_by_name, different_key)

        found_by_doc_id_and_name = self.splat_service.find_api_key(doc_id=different_key['_id'], name=different_key['name'])
        self.assertEqual(found_by_doc_id_and_name, different_key)

    def test_delete_api_key(self):
        api_key_name = 'testApiKey'
        doc_id = self.splat_service.create_api_key(api_key_name)
        api_key = self.splat_service.find_api_key(doc_id=doc_id)
        self.assertIsNotNone(api_key)

        deleted = self.splat_service.delete_api_key(doc_id=doc_id)
        self.assertEqual(deleted, api_key)
        self.assertIsNone(self.splat_service.find_api_key(doc_id=doc_id))

    def test_create_api_key_with_provided_key(self):
        api_key_name = 'testApiKey'
        provided_key = 'IAmAnEmoji'
        doc_id = self.splat_service.create_api_key(api_key_name, key=provided_key)

        api_key = self.splat_service.find_api_key(doc_id=doc_id)
        self.assertEqual(api_key['key'], provided_key)

    def test_update_api_key(self):
        original_key_name = 'originalName'
        original_key_value = 'originalKeyValue'
        doc_id = self.splat_service.create_api_key(original_key_name, key=original_key_value)
        api_key = self.splat_service.find_api_key(doc_id=doc_id)
        self.assertEqual(api_key['name'], original_key_name)
        self.assertEqual(api_key['key'], original_key_value)

        updated_name = 'updatedName'
        self.splat_service.update_api_key(doc_id, key=api_key['key'], name=updated_name)
        api_key = self.splat_service.find_api_key(doc_id)
        self.assertEqual(api_key['name'], updated_name)
        self.assertEqual(api_key['key'], original_key_value)

        updated_key = 'updatedKeyValue'
        self.splat_service.update_api_key(doc_id, key=updated_key, name=api_key['name'])
        api_key = self.splat_service.find_api_key(doc_id)
        self.assertEqual(api_key['key'], updated_key)
        self.assertEqual(api_key['name'], updated_name)


if __name__ == '__main__':
    unittest.main()
