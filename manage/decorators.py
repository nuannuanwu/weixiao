# -*- coding: utf-8 -*-
from functools import wraps
from django.contrib import messages
from django.utils.translation import ugettext as _
from django.contrib.admin.forms import AdminAuthenticationForm
from django.contrib.auth.views import login
from django.contrib.auth import REDIRECT_FIELD_NAME
from kinger.models import Teacher
from django.contrib.auth.views import redirect_to_login
import hotshot
import os
import time
import kinger.settings as settings
import tempfile
try:
    PROFILE_LOG_BASE = settings.PROFILE_LOG_BASE
except:
    PROFILE_LOG_BASE = tempfile.gettempdir()


def school_admin_required(view_func):
    """
        检查是否具有学校管理员
    """
    @wraps(view_func)
    def check_perms(request, *args, **kwargs):
        user = request.user
        path = request.build_absolute_uri()
        if user.has_perm('kinger.can_manage_school'):       
            return view_func(request, *args, **kwargs)
        elif user.is_authenticated():
            messages.error(request, '你不是学校管理员，无权访问。请用学校管理员帐号登录。')           
            return redirect_to_login(path)
        else:
            messages.info(request, '访问学校管理后台，请用学校管理员账号登录')  
            return redirect_to_login(path)
    return check_perms

# def school_admin_required(view_func):
#     """
#     Decorator for views that checks that the user is logged in and is a staff
#     member, displaying the login page if necessary.
#     """
#     @wraps(view_func)
#     def _checklogin(request, *args, **kwargs):
#         user = request.user
#         if user.has_perm("kinger.can_manage_school"):
#             # The user is valid. Continue to the admin page.
#             return view_func(request, *args, **kwargs)

#         assert hasattr(request, 'session'), "The Django admin requires session middleware to be installed. Edit your MIDDLEWARE_CLASSES setting to insert 'django.contrib.sessions.middleware.SessionMiddleware'."
#         defaults = {
#             'template_name': 'admin/login.html',
#             'authentication_form': AdminAuthenticationForm,
#             'extra_context': {
#                 'title': _('Log in'),
#                 'app_path': request.get_full_path(),
#                 REDIRECT_FIELD_NAME: request.get_full_path(),
#             },
#         }
#         return login(request, **defaults)
#     return _checklogin

def school_teacher_required(view_func):
    """
        检查是否为老师用户
    """
    @wraps(view_func)
    def check_perms(request, *args, **kwargs):
        user = request.user
        path = request.build_absolute_uri()
        if is_teacher(user):       
            return view_func(request, *args, **kwargs)
        elif user.is_authenticated():
            messages.error(request, '你不是老师用户，无权访问。请用老师账号登录。')           
            return redirect_to_login(path)
        else:
            #messages.info(request, '')  
            return redirect_to_login(path)
    return check_perms


def is_teacher(user):
    """是否为老师用户"""
    try:
        d = isinstance(user.teacher,Teacher)
        if d:
            return True
        else:
            return False
    except Exception:
        return False


def profile(log_file):
    """Profile some callable.

    This decorator uses the hotshot profiler to profile some callable (like
    a view function or method) and dumps the profile data somewhere sensible
    for later processing and examination.

    It takes one argument, the profile log name. If it's a relative path, it
    places it under the PROFILE_LOG_BASE. It also inserts a time stamp into the 
    file name, such that 'my_view.prof' become 'my_view-20100211T170321.prof', 
    where the time stamp is in UTC. This makes it easy to run and compare 
    multiple trials.     
    """

    if not os.path.isabs(log_file):
        log_file = os.path.join(PROFILE_LOG_BASE, log_file)

    def _outer(f):
        def _inner(*args, **kwargs):
            # Add a timestamp to the profile output when the callable
            # is actually called.
            (base, ext) = os.path.splitext(log_file)
            base = base + "-" + time.strftime("%Y%m%dT%H%M%S", time.gmtime())
            final_log_file = base + ext

            prof = hotshot.Profile(final_log_file)
            try:
                ret = prof.runcall(f, *args, **kwargs)
            finally:
                prof.close()
            return ret

        return _inner
    return _outer