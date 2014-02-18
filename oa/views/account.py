# -*- coding: utf-8 -*-
from django.shortcuts import redirect, render, get_object_or_404
from kinger.models import Teacher, School, Group, PostJob,Sms,Role
from django.contrib.auth.models import User
from oa.forms import TeacherUserForm,UserProfileForm,PostJobForm
from django.core.context_processors import csrf
from django.contrib import messages
from django.db.models import Q
from django.utils.translation import ugettext as _
from django.core.exceptions import ObjectDoesNotExist, MultipleObjectsReturned
from django.http import HttpResponse
from django.views.decorators.http import require_POST, require_GET
import xlwt, xlrd
from django.http import HttpResponse
from oa import helpers
import datetime
from kinger.settings import SEND_ACCOUNT_TIMEDELTA
from django.core.exceptions import ObjectDoesNotExist, MultipleObjectsReturned
from manage.forms import TeacherForm
from django.contrib.auth.forms import PasswordChangeForm,SetPasswordForm
from userena import signals as userena_signals
from django.core.urlresolvers import reverse
from oa.decorators import Has_permission
from django.contrib import auth
from django.contrib.auth.views import logout
from oa.forms import PasswordForm
try:
    import simplejson as json
except ImportError:
    import json
    

@Has_permission('manage_personal_message')
def account_setting(request, template_name="oa/account_setting.html"):
    """个人设置"""
    if request.method == 'POST':
        password = request.user.password
        form1 = TeacherUserForm(request.POST,instance=request.user)
        form2 = UserProfileForm(request.POST, request.FILES,instance=request.user.get_profile())
        
        if form1.is_valid() and form2.is_valid():
            u = form1.save(commit=False)
            u.password = password
            u.save()
            profile = form2.save(commit=False)
            realname = request.POST['realname']
            profile.realname = realname
            profile.save()
            if helpers.is_teacher(request.user):
                teacher = request.user.teacher
                teacher.name = profile.realname
                teacher.save()
            if helpers.is_student(request.user):
                student = request.user.student
                student.name = profile.realname
                student.save()
            
            messages.success(request, _('Your profile has been updated.'))
            return redirect("oa_account_setting")
    else:
        form1 = TeacherUserForm(instance=request.user)
        form2 = UserProfileForm(instance=request.user.get_profile())
    
    
    try:
        postjob = request.user.teacher.postjob
    except:
        postjob = None
    ctx = {'form1': form1,'form2': form2,'postjob':postjob}
    ctx.update(csrf(request))
    return render(request, template_name, ctx)

@Has_permission('manage_personal_message')
def password_change(request,user_id,template_name='oa/password_form.html'):
    """修改密码"""
    pass_form=PasswordForm
    user = get_object_or_404(User,id=user_id)
    form = pass_form(user=user)
    success = False
    if request.method == "POST":
        form = pass_form(user=user, data=request.POST)
        if form.is_valid():
            form.save()
            # Send a signal that the password has changed
            userena_signals.password_complete.send(sender=None,user=user)
            success = True
            return render(request, template_name, {'form':form,'success':success})
            
    ctx = {'form':form,'profile':user.get_profile(),'success':success}

    return render(request, template_name, ctx)

@Has_permission('manage_personal_message')
def password_set(request,user_id,template_name='oa/set_password_form.html'):
    """重置密码"""
    pass_form=SetPasswordForm
    user = get_object_or_404(User,id=user_id)
    form = pass_form(user=user)
    success = False
    if request.method == "POST":
        form = pass_form(user=user, data=request.POST)
        if form.is_valid():
            form.save()
            # Send a signal that the password has changed
            userena_signals.password_complete.send(sender=None,user=user)
            success = True
            return render(request, template_name, {'form':form,'success':success})
            
    ctx = {'form':form,'profile':user.get_profile(),'success':success}

    return render(request, template_name, ctx)

def oa_logout(request):
    """登出账号"""
    if request.user.is_authenticated:
        logout(request)
        messages.success(request, _('You have been signed out.'))
        return redirect("kinger_edu_index")
    else:
        return redirect(request.get_full_path())


