# -*- coding: utf-8 -*-
from django.http import HttpResponse, HttpResponseNotFound
from django.shortcuts import render_to_response, redirect, render, get_object_or_404
#from api.helpers import rc
from oa import helpers
from django.conf import settings
from manage.forms import ScheduleForm
from django.contrib import messages
from kinger.models import Group,Schedule,Teacher,School,GroupTeacher
from manage.decorators import school_teacher_required
from django.core.urlresolvers import resolve, reverse
from manage.helpers import is_teacher,is_student
from django.utils.encoding import smart_str, smart_unicode
from django.utils.http import urlquote
from django.contrib.auth.decorators import login_required
from oa.decorators import Has_permission


@Has_permission('manage_shcedule')
def teacher_index(request, template_name="oa/schedule/teacher_index.html"):
    """周课表列表页"""
    user = request.user
    schools = helpers.get_schools(user)
    school_id = int(request.GET.get("sid",-1))
    group_id = int(request.GET.get("gid",-1))
    try:
        school = get_object_or_404(School, pk=school_id)
    except:
        school = None
        
    is_admin = helpers.is_school_admin(request.user)
    if is_admin:
        groups = Group.objects.filter(school_id=school_id).exclude(type=3)
    else:
        group_pks = [g.group_id for g in GroupTeacher.objects.filter(teacher=user.teacher)]
        groups = Group.objects.filter(pk__in=group_pks)

    group_count = groups.count()
    schedules = Schedule.objects.all()
    try:
        group = Group.objects.get(pk=group_id)
    except:
        group = None
        
    schedules = Schedule.objects.filter(user=user)
    if school:
        schedules = schedules.filter(group__school=school)
    if group:
        schedules = schedules.filter(group=group)
    ctx = {"schedules":schedules,"group":group,"groups":groups,\
           "schools":schools,"school":school,'group_count':group_count}
    return render(request, template_name, ctx)

@Has_permission('manage_shcedule')
def create(request,template_name="oa/schedule/add_form.html"):
    """添加周课表"""
    user = request.user
    schools = helpers.get_schools(user)
    is_admin = helpers.is_school_admin(request.user)
    if is_admin:
        school_id = schools[0].id
        groups = Group.objects.filter(school_id=school_id).exclude(type=3)
    else:
        group_pks = [g.group_id for g in GroupTeacher.objects.filter(teacher=user.teacher)]
        groups = Group.objects.filter(pk__in=group_pks)
    group_count = groups.count()
    group_id = int(request.GET.get("class_id",-1))
    ctx = {'schools':schools,'groups':groups,'group_count':group_count}

    if request.method == 'POST':
        form = ScheduleForm(request.POST,request.FILES)
        group_id = request.POST.get("group","")
        if form.is_valid():
            schedule = form.save(commit=False)
            schedule.save()
            group = schedule.group
            messages.success(request, u'课表 %s 上传成功' % schedule.name)
            return redirect(request.get_full_path() + '?class_id=' + str(group.id))
    else:
        form = ScheduleForm()
    
    ctx.update({'form':form,"group_id":group_id})
    return render(request, template_name, ctx)

@Has_permission('manage_shcedule')
def delete(request, schedule_id):
    """ 删除课表 """

    schedule = get_object_or_404(Schedule,pk=schedule_id)
    schedule.delete()
    messages.success(request, u'课表 %s 已删除' % schedule.name)
    return redirect("oa_schedule_teacher")

@Has_permission('manage_shcedule')  
def download(request, schedule_id):
    """ 下载课表 """
    
    schedule = get_object_or_404(Schedule,pk=schedule_id)
    filename = schedule.name
    if "MSIE" in request.META['HTTP_USER_AGENT']:
        filename=urlquote(filename)
    else:
        filename=smart_str(filename)
    response = HttpResponse(schedule.src, content_type='application/msword')

    response['Content-Disposition'] = 'attachment; filename=%s' % filename
    return response
    

