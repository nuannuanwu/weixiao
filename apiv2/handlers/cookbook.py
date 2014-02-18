# -*- coding: utf-8 -*-

from piston.handler import BaseHandler
from api.helpers import rc, DispatchMixin
from django.db.models import Q
from django.db import IntegrityError
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.comments import Comment
from kinger.models import Cookbook,Group
from kinger import helpers
from django.contrib.auth.models import User

from django.contrib.contenttypes.models import ContentType
from likeable.models import Like
from api.helpers import query_range_filter

import api.handlers.user
from api.helpers import media_path,media_attr
import datetime
try:
    import simplejson as json
except ImportError:
    import json


class CookbookHandler(DispatchMixin, BaseHandler):
    model = Cookbook
    fields = ("id", "breakfast", "cookbook", "light_breakfast","lunch","light_lunch", "dinner", "light_dinner", "date","school","group")
    
    allowed_methods = ("GET", )

    def read(self, request):
        """
        获取某个食谱的详情

        ``GET`` 

        param id:某个食谱的 id
        param date:日期
        param class_id:班级id
        """
        params = request.GET
        id = params.get("id")
        date = params.get("date")
        class_id = params.get("class_id")
        if id:
            try:
                cookbook = Cookbook.objects.get(pk=id)
                helpers.mark_cookbook_as_read(request,cookbook)
                return cookbook
            except Cookbook.DoesNotExist:
                return rc.NOT_HERE
            
        if not date and not class_id:
            return rc.bad_request( "date or class_id is requierd")
        
        try:
            group = Group.objects.get(pk=class_id)
        except Group.DoesNotExist:
            return rc.not_here("froup object is not exist")
        
        #date = datetime.datetime.strptime(date,"%Y-%m-%d")
        cookbooks = Cookbook.objects.filter(date=date,group=group)

        if cookbooks:
            cookbook = cookbooks[0]
            helpers.mark_cookbook_as_read(request,cookbook)
        else:
            cookbook = ''
        return cookbook
    