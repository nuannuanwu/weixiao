# -*- coding: utf-8 -*-

from piston.handler import BaseHandler
from api.helpers import rc

from kinger.models import Teacher, Group
from api.helpers import query_range_filter
from django.core.exceptions import ObjectDoesNotExist


class TeacherHandler(BaseHandler):
    model = Teacher
    fields = ("id", "school_id", "name", "appellation", "description", "ctime", \
     ("user", ()))

    @classmethod
    def school_id(cls, model, request):
        return model.school.id

    def read(self, request):
        """
        获取某个老师的信息

        ``GET`` 未公开接口

        :param id:
            某个教师的教师 id
        """
        teacher_id = request.GET.get("id")
        try:
            teacher = Teacher.objects.get(pk=teacher_id) 
        except Teacher.DoesNotExist:
            return rc.NOT_HERE

        return teacher


class TeacherCategoryHandler(TeacherHandler):
    allowed_methods = ("GET",)

    def by_class(self, request):
        """
        获得某个班级的老师列表

        :param class_id:
            老师所在班级的 id
        """
        class_id = request.GET.get("class_id")
        if not class_id:
            return rc.BAD_REQUEST

        try:
            teachers = Group.objects.get(pk=class_id).teachers.all()
        except ObjectDoesNotExist, e:
            return rc.not_here(e)

        return query_range_filter(request.GET, teachers, "teachers")

    def read(self, request, category=None):
        func = getattr(self, category)
        if not func and not callable(func):
            return rc.FORBIDDEN
        return func(request)
