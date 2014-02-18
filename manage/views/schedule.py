# -*- coding: utf-8 -*-
from django.http import HttpResponse, HttpResponseNotFound
from django.shortcuts import render_to_response, redirect, render, get_object_or_404
#from api.helpers import rc
from kinger import helpers
from django.conf import settings
from manage.forms import ScheduleForm
from django.contrib import messages
from kinger.models import Group,Schedule,Teacher
from manage.decorators import school_teacher_required
from django.core.urlresolvers import resolve, reverse
from manage.helpers import is_teacher,is_student
from django.utils.encoding import smart_str, smart_unicode
from django.utils.http import urlquote
from django.contrib.auth.decorators import login_required

@login_required
def student_index(request, template_name="schedule/student_index.html"):
    user = request.user
    schedules = Schedule.objects.all()
    try:
        group = user.student.group
    except:
        return render(request, "403.html")
    schedules = schedules.filter(group=group)
    ctx = {"schedules":schedules,"group":group}
    return render(request, template_name, ctx)

@school_teacher_required
def teacher_index(request, template_name="schedule/teacher_index.html"):
    user = request.user
    groups = user.teacher.groups.all()
    
    schedules = Schedule.objects.all()
    group_id = request.GET.get("class_id","")
    if group_id:
        schedules = schedules.filter(user=user,group_id=group_id)
    else:
        group_id = groups[0].id
        schedules = schedules.filter(user=user,group_id=group_id)
    group = Group.objects.get(pk=group_id)
    ctx = {"schedules":schedules,"group":group,"groups":groups}
    return render(request, template_name, ctx)

@school_teacher_required
def create(request,template_name="schedule/add_form.html"):

    ctx = {}
    group_id = request.GET.get("class_id","")
    if request.method == 'POST':
        form = ScheduleForm(request.POST,request.FILES)
        if form.is_valid():
            schedule = form.save(commit=False)
            schedule.save()
            ctx.update({"group":schedule.group})
            messages.success(request, u'课表 %s 上传成功' % schedule.name)
    else:
        group = get_object_or_404(Group, pk=group_id)
        form = ScheduleForm()
        ctx.update({"group":group})

    ctx.update({'form':form})
    return render(request, template_name, ctx)

@school_teacher_required
def delete(request, schedule_id):
    """ 删除课表 """

    schedule = get_object_or_404(Schedule,pk=schedule_id)
    schedule.delete()
    messages.success(request, u'课表 %s 已删除' % schedule.name)
    return redirect("manage_schedule_teacher")

@login_required    
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
    

