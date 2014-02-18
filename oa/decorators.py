# -*- coding: utf-8 -*-
from functools import wraps
from django.contrib import messages
from django.utils.translation import ugettext as _
from django.contrib.admin.forms import AdminAuthenticationForm
from django.contrib.auth.views import login
from django.contrib.auth import REDIRECT_FIELD_NAME
from kinger.models import Teacher
from django.contrib.auth.views import redirect_to_login
from oa import helpers
from django.core.urlresolvers import reverse
from django.shortcuts import render_to_response, redirect, render, get_object_or_404


def school_admin_required(view_func):
    """
        检查是否具有学园管理员
    """
    @wraps(view_func)
    def check_perms(request, *args, **kwargs):
        user = request.user
        path = request.build_absolute_uri()
        if user.is_authenticated():
            try:
                schools = helpers.get_schools(request.user)
                if schools:       
                    return view_func(request, *args, **kwargs)
                else:
                    messages.error(request, '你不是集团或学园用户，无权访问。请用学园管理员账号登录。')           
                    return redirect_to_login(path) 
            except:
                messages.error(request, '你不是学园管理员，无权访问。请用学园管理员账号登录。')           
                return redirect_to_login(path)
        else:
            messages.info(request, '访问学园管理后台，请用学园管理员账号登录')  
            return redirect_to_login(path)
    return check_perms

def agency_admin_required(view_func):
    """
        检查是否具有集团管理员
    """
    @wraps(view_func)
    def check_perms(request, *args, **kwargs):
        user = request.user
        path = request.build_absolute_uri()
        return view_func(request, *args, **kwargs)
        if user.is_authenticated():
            try:
                schools = helpers.get_schools(request.user)
                print 111111
                if schools:       
                    print 2222222222
                    return view_func(request, *args, **kwargs)
                else:
                    print 33333333
                    messages.error(request, '你不是集团管理员，无权访问。请用集团管理员账号登录。')           
                    return redirect_to_login(path)
            except:
                print 4444444
                messages.error(request, '你不是集团管理员，无权访问。请用集团理员账号登录。')           
                return redirect_to_login(path)
        else:
            messages.info(request, '访问集团管理后台，请用集团管理员账号登录')  
            return redirect_to_login(path)
    return check_perms

def school_teacher_perm(view_func):
    """
        检查是否有学园职员管理权限
    """
    @wraps(view_func)
    def check_perms(request, *args, **kwargs):
        user = request.user
        path = request.build_absolute_uri()
        code_list = [c.code for c in helpers.user_access_list(user)]
        if 'school_teacher' in code_list:       
            return view_func(request, *args, **kwargs)
        elif user.is_authenticated():
            messages.error(request, '您的权限不足无法访问。')           
            return redirect_to_login(path)
        else: 
            return redirect_to_login(path)
    return check_perms

def statistical_perm(view_func):
    """
        检查是否有访问统计页面权限
    """
    @wraps(view_func)
    def statistical(request, *args, **kwargs):
        user = request.user
        path = request.build_absolute_uri()
        perm = u'访问统计页面'
        is_can =  request.user.groups.filter(name = perm).exists()
        if is_can:
            return view_func(request, *args, **kwargs)
        return redirect_to_login(path)
    return statistical

class Has_permission(object):
    def __init__(self, arg1):
        self.arg1 = arg1

    def __call__(self, f):

        def wrapped_f(request, *args, **kwargs):
#             print self.arg1,'aaaaaaaaaaaaaaaaaaaa'
            user = request.user
            path = request.build_absolute_uri()
            #用户登录
            if not user.is_authenticated():
                messages.error(request, '您尚未登录。')           
                return redirect_to_login(path)
            #老师用户
            try:
                school = helpers.get_schools(request.user)[0]
#                print school,'ssssssss'
                if not school:
                    return f(request, *args, **kwargs)
            except:
                messages.error(request, '您的权限不足无法访问。')    
                return redirect(reverse('userena_signin') + "?lack_perm=lack&next=" + str(path))   
#                return redirect_to_login(path)
            
            #权限判断
            code_list = [c.code for c in helpers.user_access_list(user)]
#            print code_list,'cccccccccc'
            if self.arg1 in code_list:  
#                print 'in'     
                return f(request, *args, **kwargs)
            elif user.is_authenticated():
#                print 'out'
                messages.error(request, '您的权限不足无法访问。')    
                return redirect(reverse('userena_signin') + "?lack_perm=lack&next=" + str(path))          
#                return redirect_to_login(path)
            else: 
                return redirect_to_login(path)       
        return wrapped_f
    
    