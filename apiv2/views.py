# -*- coding: utf-8 -*-

"""
| api 接口所有的 handler 声明.
| 每个 ``handler`` 相当于 ``django`` 一个 ``view``
"""

from apiv2.handlers.tile import *
from apiv2.handlers.comment import *
from apiv2.handlers.student import *
from apiv2.handlers.teacher import *
from apiv2.handlers.user import *
from apiv2.handlers.message import *
from apiv2.handlers.group import *
from apiv2.handlers.event import *
from apiv2.handlers.mentor import *
from apiv2.handlers.active import *
from apiv2.handlers.cookbook import *
from apiv2.handlers import ApiNotFoundHandler

from apiv2.authentication import PistonOAuth2
# from piston.resource import Resource
from apiv2.resource import KingerResource
from piston.authentication import HttpBasicAuthentication, DjangoAuthentication, MultiAuthentication


class ApiAuth(object):
    """
     api 接口所有的认证方式.
    """
    oauth2 = PistonOAuth2(json=True)
    base = HttpBasicAuthentication()
    dj = DjangoAuthentication()
    
    # 同时支持多种认证方式，按顺序认证.
    dj_oauth = MultiAuthentication((oauth2, dj))


def _r(handler, auth=ApiAuth.dj_oauth):
    return KingerResource(handler=handler, authentication=auth)


def _web_r(handler):
    """
    给 web 端调用的接口
    """
    re = KingerResource(handler, ApiAuth.dj)
    # 对提交进行 ``csrf`` 保护(防止跨域提交).
    re.csrf_exempt = False
    return re

users = _r(UserHandler)
accounts = _r(AccountHandler)

actives = _r(ActiveHandler)
actives_actions = _r(ActiveActionHandler)

cookbooks = _r(CookbookHandler)

tiles = _r(TileHandler)
tiles_actions = _r(TileActionHandler)
tiles_likeable = _r(TileLikeableHandler)
tiles_category = _r(TileCategoryHandler)

tiles_categorys = _r(CategoryHandler)

tiles_types = _r(TileTypesHandler)
tiles_tags = _r(TileTagsHandler)
tiles_create_tags = _r(TileCtagHandler)

tiles_event = _r(EventSettingHandler)

comments = _r(CommentHandler)
comments_templater = _r(CommentTemplaterHandler)
comments_templater_types = _r(CommentTemplaterTypeHandler)

students = _r(StudentHandler)
students_category = _r(StudentCategoryHandler)

teachers = _r(TeacherHandler)
teachers_category = _r(TeacherCategoryHandler)

groups = _r(GroupHandler)
mentors = _r(MentorHandler)

messages = _r(MessageHandler)
message_contacts = _r(MessageContactHandler)
messages_actions = _r(MessageActionHandler)
messages_test = _r(MessageTestHandler)
mesage_to_class = _r(MessageToClassHandler)

event_setting = _r(EventSettingHandler)
api_not_found = _r(ApiNotFoundHandler)
devices = _r(DeviceHandler)


web_comments = _web_r(CommentHandler)
web_tiles_likeable = _web_r(TileLikeableHandler)
