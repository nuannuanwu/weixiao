# -*- coding: utf-8 -*-

from piston.handler import BaseHandler
from api.helpers import rc, DispatchMixin
from django.core.exceptions import ObjectDoesNotExist
from kinger.models import Mentor
from api.helpers import query_range_filter
from api.helpers import media_path

class MentorHandler(DispatchMixin, BaseHandler):
    model = Mentor
    fields = ("id", "name", "appellation", "description", "ctime", \
     ("user", ()))
    allowed_methods = ("GET", )

    def read(self, request):
        """
        获取某个老师的信息

        ``GET`` 未公开接口

        :param id:
            某个教师的教师 id
        """
        mentor_id = request.GET.get("id")
        try:
            mentor = Mentor.objects.get(pk=mentor_id) 
        except Mentor.DoesNotExist:
            return rc.NOT_HERE

        return mentor