# -*- coding: utf-8 -*-

from piston.handler import BaseHandler
from api.helpers import rc, DispatchMixin
from django.core.exceptions import ObjectDoesNotExist
from kinger.models import Group
from api.helpers import query_range_filter
from api.helpers import media_path

class GroupHandler(DispatchMixin, BaseHandler):
    model = Group
    fields = ("id", "name", "ctime", "school_id", "logo", "description", "announcement")
    allowed_methods = ("GET", )

    @classmethod
    def logo(cls, model, request):
        try:
            url = model.logo
            url = media_path(url,"normal")
            return url
        except Exception:
            return ""

    @DispatchMixin.get_required
    def list(self, request):
        """
        获取登录用户所在的班级列表

        ``GET`` `account/profile/class_list <http://192.168.1.222:8080/v1/account/profile/class_list>`_

        """
        try:
            queryset = request.user.teacher.groups.all()
            return query_range_filter(request.GET, queryset, "classes")
        except ObjectDoesNotExist:
            pass

        try:
            group = request.user.student.group
            queryset = Group.objects.filter(id=group.id).all()
            return query_range_filter(request.GET, queryset, "classes")
        except ObjectDoesNotExist:
            pass

        return rc.NOT_FOUND