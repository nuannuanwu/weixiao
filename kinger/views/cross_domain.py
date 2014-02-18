# -*- coding: utf-8 -*-
from django.shortcuts import redirect, render, get_object_or_404
from django.contrib.auth.models import User
from oa.forms import TeacherUserForm,UserProfileForm,PostJobForm
from django.core.context_processors import csrf
from django.db.models import Q
from django.utils.translation import ugettext as _
from django.core.exceptions import ObjectDoesNotExist, MultipleObjectsReturned
from django.http import HttpResponse
from django.views.decorators.http import require_POST, require_GET
from django.http import HttpResponse
from oa import helpers
import datetime, time
import md5
from django.contrib.auth.forms import PasswordChangeForm
from userena import signals as userena_signals
from django.core.urlresolvers import reverse
from django.contrib import auth
try:
    import simplejson as json
except ImportError:
    import json
from django.contrib.auth.views import logout
    
def cross_domain_login(request):
    uid = request.GET.get('uid','')
    salt = request.GET.get('salt','')
    hash = request.GET.get('hash','')
    mask = '3n7j6m9s'
    m = md5.new(str(uid) + str(salt) + mask)
    new_hash = m.hexdigest()
    
    if new_hash == hash:
        user = User.objects.get(pk=uid)
        user.backend = 'django.contrib.auth.backends.ModelBackend'
        user.save()
#        user = auth.authenticate(username=u.username, password=u.password)
        is_teacher = helpers.is_teacher(user)
        is_student = helpers.is_student(user)
        if user is not None and user.is_active:
            auth.login(request, user)
    
        d = json.dumps({'is_teacher':is_teacher,'is_student':is_student,\
                        'username':helpers.get_name(user)})
#        request.GET['callback']+"("+(d)+");"
        return HttpResponse(request.GET['callback']+"("+(d)+");")
    else:
        return HttpResponse(json.dumps({}))

def cross_domain_logout(request):
    print 11111111
    uid = request.GET.get('uid','')
    salt = request.GET.get('salt','')
    hash = request.GET.get('hash','')
    mask = '0q2o4f6s'
    m = md5.new(str(uid) + str(salt) + mask)
    new_hash = m.hexdigest()

    if new_hash == hash:
        user = User.objects.get(pk=uid)
        request.user = user

    try:
        logout(request)
        status = True
    except:
        status = False
    
    d = json.dumps({'status':status})
    return HttpResponse(request.GET['callback']+"("+(d)+");")