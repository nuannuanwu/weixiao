# -*- coding: utf-8 -*-

from piston.handler import BaseHandler
from api.helpers import rc
# from django.db.models import Q

from kinger.models import Student,Group,GroupTeacher
# from django.contrib.auth.models import User
from api.helpers import query_range_filter,media_path
from django.core.exceptions import ObjectDoesNotExist

class GroupHandler(BaseHandler):
    model = Group
    fields = ("id", "school_id", "class_id", "name", "description", "ctime", ("user", ()))
    allowed_methods = ("GET", )

    @classmethod
    def class_id(cls, model, request):
        return model.id
    
#    def user(cls, model, request):
#        return model
    
#    @classmethod
#    def avatar(cls, model, request):
#        try:
#            url = model.logo
#            url = media_path(url, "avatar")
#            return url
#        except Exception:
#            return ""
#    
#    @classmethod
#    def avatar_large(cls, model, request):
#        try:
#            url = model.logo
#            url = media_path(url, "avatar_large")
#            return url
#        except Exception:
#            return ""
        
    def read(self, request):
        class_id = request.GET.get("class_id")
#        if not class_id:
#            return rc.BAD_REQUEST
#        
        
#        queryset = Group.objects.filter(school__pk=group.school_id).exclude(type=3)
        try:
            group = Group.objects.get(pk=class_id)
            group_wx_pks = [gv.id for gv in Group.objects.filter(school__pk=group.school_id)]
            group_oa_pks = [go.group_id for go in GroupTeacher.objects.filter(teacher=request.user.teacher)]
            group_pks = group_wx_pks + group_oa_pks
            queryset = Group.objects.filter(pk__in=group_pks).all().exclude(type=3)
        except:
            queryset = Group.objects.filter(id=class_id)

        return queryset
        

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
        
        from oa.helpers import user_access_list
        user = request.user
        code_list = [c.code for c in user_access_list(user)]
        school_level = True if "manage_school_tile" in code_list else False

        if school_level:
            try:
                group = Group.objects.get(pk=class_id)
#                queryset = Group.objects.filter(school__pk=group.school_id).exclude(type=3)
                queryset = GroupHandler().read(request)
                print queryset,'qqqqqqqqqqqqqqqqqqqqqq'
            except ObjectDoesNotExist, e:
                return rc.not_here(e)
            return query_range_filter(request.GET, queryset, "students")
        
        else:
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
