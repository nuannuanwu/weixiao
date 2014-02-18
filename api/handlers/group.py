# -*- coding: utf-8 -*-

from piston.handler import BaseHandler
from api.helpers import rc, DispatchMixin
from django.core.exceptions import ObjectDoesNotExist
from kinger.models import Group,GroupTeacher
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
            from oa.helpers import user_access_list
            user = request.user
            code_list = [c.code for c in user_access_list(user)]
            school_level = True if "manage_school_tile" in code_list else False
            if school_level:
                school = request.user.teacher.school
                group,created = Group.objects.get_or_create(name="全园班级",school_id=school.id,type=3,creator=school.creator,grade_id=0)
                group_pks = [group.id]
                queryset = Group.objects.filter(pk__in=group_pks).all()
            else:
                group_wx_pks = [gv.id for gv in request.user.teacher.groups.all()]
                group_oa_pks = [go.group_id for go in GroupTeacher.objects.filter(teacher=request.user.teacher)]
                group_pks = group_wx_pks + group_oa_pks
                queryset = Group.objects.filter(pk__in=group_pks).all()
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