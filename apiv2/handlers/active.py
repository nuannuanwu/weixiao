# -*- coding: utf-8 -*-

from piston.handler import BaseHandler
from api.helpers import rc, DispatchMixin
from django.db.models import Q
from django.db import IntegrityError
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.comments import Comment
from kinger.models import Activity,Group
from django.contrib.auth.models import User

from django.contrib.contenttypes.models import ContentType
from likeable.models import Like
from api.helpers import query_range_filter

import api.handlers.user
from api.helpers import media_path,media_attr
try:
    import simplejson as json
except ImportError:
    import json


class ActiveHandler(DispatchMixin, BaseHandler):
    model = Activity
    fields = ("id", "user", "group", "description", "start_time")
    allowed_methods = ("GET", )

    def read(self, request):
        """
        获取某个活动的信息

        ``GET`` 

        :param id:
            某个活动的 id
        """
        params = request.GET
        active_id = params.get("id")
        user_id = params.get("uid")
        class_id = params.get("class_id")
        if active_id:
            try:
                active = Activity.objects.get(pk=active_id)
                return active
            except Activity.DoesNotExist:
                return rc.NOT_HERE
            
        if not user_id and not class_id:
            return rc.bad_request( "user_id or class_id is requierd")
        q = Q(user__pk=user_id) if user_id else Q(group__pk=class_id)
        queryset = Activity.objects.filter(q).order_by("-start_time","-id")
        return query_range_filter(params, queryset, "actives")
    

class ActiveActionHandler(ActiveHandler):
    """管理日常活动操作"""
    allowed_methods = ("POST")
    
    def post(self, request):
        """
        发布一条内容, 针对个人或者班级.

        ``POST`` `actives/create/ <http://192.168.1.222:8080/api/v1/actives/create>`_

        :param uid:
            发布者，默认为匿名用户(uid: -1)

        :param class_id:
            瓦片所属班级，是否属于班级的内容

        :param content:
            内容描述

        """
        params = request.POST
        uid = params.get("uid", -1)
        class_id = params.get("class_id")
        content = params.get("content", "")
        
        try:
            user = User.objects.get(pk=uid)
        except User.DoesNotExist:
            return rc.not_here("user object  is not exist")

        try:
            group = Group.objects.get(pk=class_id) if class_id else None
        except Group.DoesNotExist:
            group = None

        try:
            desc = json.loads(content)
            act = desc['events']
        except:
            return rc.not_here("description object must be json has key events")
        if not act:
            desc = ''
        else:
            i = 0
            for d in act:
                if not d['content']:
                   i += 1 
            if i == len(act):
                desc = ''
                
        if not desc:
            return rc.not_here("description can not be null")
        active = Activity()
        active.user = user
        active.creator = request.user
        active.group = group
        active.description = json.dumps({"events":desc['events']})
        active.save()
        
        return active if active.id else None
    
    def modify(self, request):
        """
        修改一条内容, 针对个人或者班级.

        ``POST`` `actives/modify/ <http://192.168.1.222:8080/v1/actives/modify>`_

        :param id:
            活动id
        :param uid:
            发布者，默认为匿名用户(uid: -1)

        :param class_id:
            活动所属班级，是否属于班级的内容

        :param content:
            内容描述
        """
        params = request.POST
        id = params.get("id")
        uid = params.get("uid", "")
        class_id = params.get("class_id","")
        content = params.get("content", "")
        
        try:
            active = Activity.objects.get(pk=id)
        except Activity.DoesNotExist:
            return rc.not_here("active object is not exist")
            
        if uid:
            try:
                user = User.objects.get(pk=uid)
            except User.DoesNotExist:
                return rc.not_here("user object  is not exist")
            active.user = user

        if class_id:
            try:
                group = Group.objects.get(pk=class_id)
            except Group.DoesNotExist:
                return rc.not_here("group object  is not exist")
            active.group = group
        
        if content:
            try:
                desc = json.loads(content)
                act = desc['events']
            except:
                return rc.not_here("description object must be json include key events")
            if not act:
                desc = ''
            else:
                i = 0
                for d in act:
                    if not d['content']:
                       i += 1 
                if i == len(act):
                    desc = ''
            if not desc:
                return rc.not_here("description can not be null")
            active.description = json.dumps({"events":desc['events']})
        
        active.save()
        return active
    
    def delete(self, request):
        """
        删除一条内容

        ``POST`` `actives/destroy/ <http://192.168.1.222:8080/api/v1/actives/destroy>`_

        :param id:
            某条活动的 id
        """
        active_id = request.POST.get("id")
        try:
            Activity.objects.get(pk=active_id).delete()
        except Activity.DoesNotExist:
            return rc.NOT_HERE

        return rc.accepted({"result": True})