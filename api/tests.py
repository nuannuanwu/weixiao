# -*- coding: utf-8 -*-
"""
This file demonstrates writing tests using the unittest module. These will pass
when you run "manage.py test".

Replace this with more appropriate tests for your application.

本测试覆盖所有接口，但只对接口进行了基本的调用测试(看是能访问并返回正确的状态码: 200)
"""

#TODO These tests just simiplely test all the api to see as if all can be assecssed.
#Should include more logic proccess.

from django.test import TestCase
from oauth2app.models import Client as O2Client
import requests
from base64 import b64encode
try:
    import simplejson as json
except ImportError:
    import json

from kinger import settings

# TODO: use django test Client object is batter.!!!
# from django.test import Client

#SITE = "http://127.0.0.1:8000/"
#SITE = "http://192.168.1.222:8000/"
#SITE = "http://szeco.vicp.net:8000/"
#SITE = "http://weixiao178.com/"
SITE = "http://website.222.test/"


class ApiTestHelper(object):
    _instance = None
    _access_token = "" # "4d7d083d80"

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super(ApiTestHelper, cls).__new__(
                                cls, *args, **kwargs)
        return cls._instance

    def _request_token(self):
        o2client = O2Client.objects.latest("id")
        self.key = o2client.key
        self.secret = o2client.secret
        self.auth_header = "Basic %s" % b64encode(self.key + ":" + self.secret)
        self.auth_url = "oauth2/authorize/"
        self.token_url = "oauth2/access_token/"

        # payload = {"client_id": self.key, "grant_type": "password", \
        #     "username": "admin", "password": "123456"}
        # headers = {"Authorization": self.auth_header}
        # r = requests.post(SITE + self.token_url, params=payload, headers=headers)
        auth_key = b64encode(self.key + ":" + self.secret)
        payload = {"client_id": self.key, "auth_key": auth_key, \
            "grant_type": "password", "username": "admin", "password": "654321"}

        r = requests.post(SITE + self.token_url, data=payload)
        r.json = json.loads(r.content)

        print r.json['access_token']

        return r.json['access_token'] if r.status_code is 200 and r.json else None

    def get_token(self):
        if not self._access_token:
            self._access_token = self._request_token()
        return self._access_token

    def _setUp(self):
        # header = "Bearer %s" % self.get_token()
        # self.headers = {"Authorization": header}
        self.url = SITE + "api/v1/"

    def get(self, url, params={}):
        self._setUp()
        params.update({"bearer_token": self.get_token()})
        rs = requests.get(self.url + url, params=params)
        rs.json = json.loads(rs.content)
        return rs    
        # return requests.get(self.url + url, params=params, headers=self.headers)

    def post(self, url, data={}, files=None):
        self._setUp()
        data.update({"bearer_token": self.get_token()})
        rs =  requests.post(self.url + url, data=data, files=files)
        rs.json = json.loads(rs.content)
        return rs
        # return requests.post(self.url + url, data=data, files=files, headers=self.headers)


class AuthTest(TestCase):
    # fixtures = ['kinger_testdata.json', "Clients"]
    fixtures = ['oauth2_testdata.json']

    def setUp(self):
        o2client = O2Client.objects.latest("id")
        self.key = o2client.key
        self.secret = o2client.secret
        self.auth_header = "Basic %s" % b64encode(self.key + ":" + self.secret)
        self.auth_url = "oauth2/authorize/"
        self.token_url = "oauth2/access_token/"

    def _get_token(self):
        auth_key = b64encode(self.key + ":" + self.secret)
        payload = {"client_id": self.key, "auth_key": auth_key, \
            "grant_type": "password", "username": "admin", "password": "654321"}

        return requests.post(SITE + self.token_url, data=payload)

    def test_get_token(self):
        r = self._get_token()
        print r.text.encode("utf8")
        self.assertEqual(r.status_code, 200)

    def test_refresh_token(self):
        token = self._get_token()
        payload = {"client_id": self.key, "client_secret": self.secret, \
            "grant_type": "refresh_token", "refresh_token": token.json['refresh_token']}
        r = requests.post(SITE + self.token_url, data=payload)
        print r.text.encode("utf8")
        self.assertEqual(r.status_code, 200)#


class ApiTestCase(TestCase):
    # fixtures = ['kinger_testdata.json']
    fixtures = ['oauth2_testdata.json']

    def setUp(self):
        self.client = ApiTestHelper()


class AccountTest(ApiTestCase):

    def test_users_show(self):
        r = self.client.get("users/show/", {"uid": 1})
        self.assertEqual(r.status_code, 200)
        self.assertEqual(r.json['uid'], 1)

    def test_get_uid(self):
        r = self.client.get("account/get_uid/")
        self.assertEqual(r.status_code, 200)

    def test_profile_class_list(self):
        r = self.client.get("account/profile/class_list/")
        self.assertEqual(r.status_code, 200)

    def test_profile_identity(self):
        r = self.client.get("account/profile/identity/")
        self.assertEqual(r.status_code, 200)

    def test_change_password(self):
        data = {"old_password": "123456", "new_password": "654321"}
        r = self.client.post("account/change_password/", data)
        self.assertEqual(r.status_code, 202)
        self.assertEqual(r.json['result'], True)

        data = {"old_password": "654321", "new_password": "123456"}
        r = self.client.post("account/change_password/", data)
        self.assertEqual(r.status_code, 202)
        self.assertEqual(r.json['result'], True)

    def test_change_avatar(self):
        path = settings.PROJECT_ROOT + '/../api/fixtures/toky.jpg'
        files = {'avatar': ('toky.jpg', open(path, 'rb'))}
        r = self.client.post("account/change_avatar/", files=files)
        self.assertEqual(r.status_code, 200)
        self.assertEqual(r.json['uid'], 1)
    
    def timesmultiple_test_change_avatar(self):
        for i in range(100):
             self.test_change_avatar()


class TilesTest(ApiTestCase):

    def test_tiles(self):
        r = self.client.get("tiles/", {"uid": 1})
        self.assertEqual(r.status_code, 200)

    def test_tiles_show(self):
        r = self.client.get("tiles/show/", {"id": 2})
        self.assertEqual(r.status_code, 200)

    def test_tiles_tags(self):
        r = self.client.get("tiles/tags/")
        self.assertEqual(r.status_code, 200)

    def test_tiles_types(self):
        r = self.client.get("tiles/types/")
        print r.content
        self.assertEqual(r.status_code, 200)

    def test_tiles_by_babys(self):
        r = self.client.get("tiles/by_babys/", {"type_id": 1})
        self.assertEqual(r.status_code, 200)

    def test_tiles_by_tags(self):
        r = self.client.get("tiles/by_tags/", {"tag_id": 6})
        self.assertEqual(r.status_code, 200)

    def test_tiles_by_babys_with_push(self):
        r = self.client.get("tiles/by_babys_with_push/")
        self.assertEqual(r.status_code, 200)

    def test_tiles_get_event_setting(self):
        r = self.client.get("tiles/get_event_setting/", {"class_id": 11})
        self.assertEqual(r.status_code, 200)

    def _request_tiles_create(self):
        path = settings.PROJECT_ROOT + '/../api/fixtures/toky.jpg'
        files = {'img': ('toky.jpg', open(path, 'rb'))}
        data = {"type_id": 1, "title": "api tsting", "content": "post from api unittest.","tag":"mmyymmyymmyymmyy"}
        return self.client.post("tiles/create/", data, files=files)

    def test_tiles_create(self):
        r = self._request_tiles_create()
        print r.json

        self.assertEqual(r.status_code, 200)
        self.assertNotEqual(r.json["image"], "")

    def test_tiles_upload_video(self):
        path = settings.PROJECT_ROOT + '/../api/fixtures/toky.jpg'
        files = {'video': ('toky.jpg', open(path, 'rb'))}
        r = self.client.post("tiles/upload_video/", files=files)
        self.assertEqual(r.status_code, 202)
        print r.json['result']
        #self.assertEqual(r.json['result'], True)

    def test_tiles_destroy(self):
        r = self._request_tiles_create()
        self.assertEqual(r.status_code, 200)
        r = self.client.post("tiles/destroy/", {"id": r.json["id"]})
        self.assertEqual(r.status_code, 202)
        self.assertEqual(r.json['result'], True)

    def test_tiles_like(self):
        r = self.client.post("tiles/like/", {"id": 2})
        self.assertEqual(r.status_code, 200)


class CommentsTest(ApiTestCase):

    def test_comments_show(self):
        r = self.client.get("comments/show/", params={"tid": 4})
        self.assertEqual(r.status_code, 200)

    def test_comments_create(self):
        data = {"tid": 4, "content": "comments test from api"}
        r = self.client.post("comments/create/", data)
        self.assertEqual(r.status_code, 200)

    def test_web_comments_create(self):
        data = {"tid": 4, "content": "comments test from api"}
        r = self.client.post("web/comments/create/", data)
        self.assertEqual(r.status_code, 403)

    def test_comments_destroy(self):
        data = {"tid": 4, "content": "comments test from api"}
        r = self.client.post("comments/create/", data)
        if r.status_code is 200:
            r = self.client.post("comments/destroy/", {"id": r.json['id']})
            self.assertEqual(r.status_code, 202)
            self.assertEqual(r.json['result'], True)


class RolesTest(ApiTestCase):

    def test_students_by_class(self):
        r = self.client.get("students/by_class/", {"class_id": 4})
        self.assertEqual(r.status_code, 200)

    def test_teachers_by_class(self):
        r = self.client.get("teachers/by_class/", {"class_id": 4})
        self.assertEqual(r.status_code, 200)


class MessagesTest(ApiTestCase):

    def test_messages_unread_count(self):
        r = self.client.get("remind/unread_count/")
        self.assertEqual(r.status_code, 200)

    def test_messages_contacts(self):
        r = self.client.get("messages/contacts/", {"class_id": 4})
        self.assertEqual(r.status_code, 200)

    def test_messages_history(self):
        r = self.client.get("messages/history/", {"uid": 1})
        self.assertEqual(r.status_code, 200)

    def test_messages_create(self):
        data = {"uid": 1, "content": "message from api testing"}
        r = self.client.post("messages/create/", data)
        self.assertEqual(r.status_code, 200)
        self.assertEqual(r.json['from_user']['uid'], 1)
        self.assertEqual(r.json['content'], "message from api testing")

    def test_messages_create_to_class(self):
        data = {"class_id": 1, "content": "message from api testing"}
        r = self.client.post("messages/create_to_class/", data)
        self.assertEqual(r.status_code, 200)

    def test_messages_destroy(self):
        data = {"uid": 1, "content": "message from api testing"}
        r = self.client.post("messages/create/", data)
        self.assertEqual(r.status_code, 200)
        r = self.client.post("messages/destroy/", {"id": r.json['id']})
        self.assertEqual(r.status_code, 202)
        self.assertEqual(r.json['result'], True)


class DevicesTest(ApiTestCase):

    # def test_get_token(self):
    #     r = self.client.get("users/device/")
    #     self.assertEqual(r.status_code, 200)

    def test_set_token(self):
        r = self.client.post("users/set_device_token/", {"token": "ebcad75de0d42a844d98a755644e30"})
        self.assertEqual(r.status_code, 202)
        self.assertEqual(r.json['result'], True)
        
    def test_delete_token(self):
        r = self.client.post("users/set_device_token/", {"token": "ebcad75de0d42a844d98a755644e30","unset":True})
        self.assertEqual(r.status_code, 202)
        self.assertEqual(r.json['result'], True)

