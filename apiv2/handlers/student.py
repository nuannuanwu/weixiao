# -*- coding: utf-8 -*-

from piston.handler import BaseHandler
from api.helpers import rc
# from django.db.models import Q

from kinger.models import Student
# from django.contrib.auth.models import User
from api.helpers import query_range_filter
from django.core.exceptions import ObjectDoesNotExist


class StudentHandler(BaseHandler):
    model = Student
    fields = ("id", "school_id", "class_id", "sn", "name", "description", "ctime", \
     ("user", ()))

    @classmethod
    def school_id(cls, model, request):
        return model.school.id

    @classmethod
    def class_id(cls, model, request):
        try:
            return model.group.id
        except ObjectDoesNotExist:
            return ""

    def read(self, request):
        """
        获取某个学生的信息

        ``GET`` 未实现接口.

        :param id:
            某个学生的学生 id
        """
        student_id = request.GET.get("id")
        try:
            student = Student.objects.get(pk=student_id) 
        except Student.DoesNotExist:
            return rc.NOT_HERE

        return student


class StudentCategoryHandler(StudentHandler):
    allowed_methods = ("GET",)

    def by_class(self, request):
        """
        获取学生列表

        ``GET`` `students/by_class/ <http://192.168.1.222:8080/v1/students/by_class>`_

        :param class_id:
            学生所在班级 id
        """
        class_id = request.GET.get("class_id")
        if not class_id:
            return rc.BAD_REQUEST

        try:
            queryset = Student.objects.filter(group__pk=class_id)
        except ObjectDoesNotExist, e:
            return rc.not_here(e)

        return query_range_filter(request.GET, queryset, "students")

    def read(self, request, category=None):
        func = getattr(self, category)
        if not func and not callable(func):
            return rc.FORBIDDEN
        return func(request)
