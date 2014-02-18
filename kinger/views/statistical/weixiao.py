# -*- coding: utf-8 -*-
from django.conf import settings
from django.utils.translation import ugettext as _
from django.shortcuts import redirect, render, get_object_or_404
from django.core.exceptions import ObjectDoesNotExist
from kinger.helpers import get_redir_url,media_path,unread_count,ajax_ok
from django.dispatch import receiver
from django.contrib import messages
from django.contrib.comments import Comment
from django.contrib.comments.views.moderation import perform_delete
from django.contrib.comments.signals import comment_was_posted
from django.contrib import comments
from django.contrib.auth.decorators import login_required, permission_required
from kinger.models import Tile, TileTag, TileType, Student,Sms, VerifySms,NewTileCategory,Mentor,TemporaryFiles,\
Cookbook,CookbookType,Access_log,Comment_relation,Activity,TileVisitor,DailyRecordVisitor,CookbookRead,Tile,TinymceImage,\
Group,Teacher,Student,GroupTeacher,School
from django.db.models import Q
from django.contrib.contenttypes.models import ContentType
import calendar,datetime,time
from django.http import Http404,HttpResponse
from kinger import helpers
from django.contrib.auth.models import User
from django.core.cache import cache
from kinger.settings import STATIC_URL,CTX_CONFIG,FILE_PATH
from django.core.paginator import Paginator
from django.core.urlresolvers import reverse
from kinger.profiles.models import Profile
from django.contrib.sites.models import get_current_site
from django.db import connection
from django.http import Http404
from django.contrib.auth import REDIRECT_FIELD_NAME
from django.contrib.sites.models import Site
from sms.models import SmsSend,SmsReplay
from userena.contrib.umessages.models import Message, MessageRecipient, MessageContact
from oa.decorators import statistical_perm
#from api.helpers import get_agency_teacher_by_group
try:
    import simplejson as json
except ImportError:
    import json

import random,urllib
from django.db.models import Max
from celery.task.http import URL
from userena.utils import generate_sha1
import os
from oss_extra.storage import AliyunStorage
import logging
logger = logging.getLogger(__name__)
SITE_INFO = Site.objects.get_current()


def index(request, template_name="statistical/index.html"):
    return render(request, template_name)
    
@statistical_perm
def group_teacher(request, template_name="statistical/group_teacher.html"):
    school_id = request.GET.get('school_id')
    schools = School.objects.filter(is_delete=False).exclude(parent_id=0)
    ctx = {'schools':schools}
    if school_id:
        school = get_object_or_404(School,id=school_id)
        group_id = request.GET.get('group_id')
        stime = request.GET.get('stime','')
        etime = request.GET.get('etime','')
        if group_id:
            group = get_object_or_404(Group,id=group_id)
            group_pks = [group,]
        else:
            group = None
            groups = Group.objects.filter(school_id=school_id,is_delete=False).exclude(type=3)
            group_pks = [g for g in groups]
            
        teachers_pre = [t for t in Teacher.objects.filter(group__in=group_pks)]
        teachers_ext = [gt.teacher for gt in GroupTeacher.objects.filter(group_id__in=group_pks)]
    #    teacher_age = get_agency_teacher_by_group(group)
        teachers = teachers_pre + teachers_ext
        teachers = list(set(teachers))
        st = datetime.datetime.strptime(stime,"%Y-%m-%d") if stime else None
        et = datetime.datetime.strptime(etime,"%Y-%m-%d") if etime else None
        data = [get_teacher_data(t.id,st,et) for t in teachers]
        ctx.update({'data':data,'school':school,'group':group,'stime':stime,'etime':etime})
    return render(request, template_name,ctx)

@statistical_perm
def school_group(request, template_name="statistical/school_group.html"):
    school_id = request.GET.get('school_id')
    schools = School.objects.filter(is_delete=False).exclude(parent_id=0)
    ctx = {'schools':schools}
    if school_id:
        stime = request.GET.get('stime','')
        etime = request.GET.get('etime','')
        school = get_object_or_404(School,id=school_id)
        groups = Group.objects.filter(school_id=school_id,is_delete=False).exclude(type=3)
        st = datetime.datetime.strptime(stime,"%Y-%m-%d") if stime else None
        et = datetime.datetime.strptime(etime,"%Y-%m-%d") if etime else None
        data = [get_class_data(g.id,st,et) for g in groups]
        ctx.update({'data':data,'school':school,'stime':stime,'etime':etime})
    return render(request, template_name,ctx)

@statistical_perm
def school_student(request, template_name="statistical/school_student.html"):
    school_id = request.GET.get('school_id')
    schools = School.objects.filter(is_delete=False).exclude(parent_id=0)
    ctx = {'schools':schools}
    if school_id:
        school = get_object_or_404(School,id=school_id)
        group_id = request.GET.get('group_id')
        stime = request.GET.get('stime','')
        etime = request.GET.get('etime','')
        if group_id:
            group = get_object_or_404(Group,id=group_id)
            group_pks = [group.id,]
        else:
            group = None
            groups = Group.objects.filter(school_id=school_id,is_delete=False).exclude(type=3)
            group_pks = [g.id for g in groups]
        st = datetime.datetime.strptime(stime,"%Y-%m-%d") if stime else None
        et = datetime.datetime.strptime(etime,"%Y-%m-%d") if etime else None
        data = [get_student_data(s.id,st,et) for s in Student.objects.filter(group_id__in=group_pks)]
        ctx.update({'data':data,'school':school,'group':group,'stime':stime,'etime':etime})
    return render(request, template_name,ctx)

def get_teacher_data(tid,st,et):
    teacher = get_object_or_404(Teacher,id=tid)
    user = teacher.user
    tiles = Tile.objects.filter(creator=user)
    activies = Activity.objects.filter(creator=user)
    smses = SmsSend.objects.filter(sender=user)
    messages = MessageRecipient.objects.filter(message__sender=user)
    if st:
        messages = messages.filter(message__sent_at__gte=st)
        tiles = tiles.filter(start_time__gte=st)
        activies = activies.filter(start_time__gte=st)
        smses = smses.filter(send_date__gte=st)
    if et:
        messages = messages.filter(message__sent_at__lt=et)
        tiles = tiles.filter(start_time__lt=et)
        activies = activies.filter(start_time__lt=et)
        smses = smses.filter(send_date__lt=et)
        
    tile_num = tiles.exclude(new_category__parent_id=1130).exclude(category_id=9).count()
    active_num = activies.count()
    record_num = tiles.filter(new_category__parent_id=1130).count()
    sms = SmsSend.objects.filter(sender=user).count()
    msg = messages.filter(message__sender=user).count()
    ctx = {'teacher':teacher,'tile_num':tile_num,'active_num':active_num,'record_num':record_num,\
           'sms':sms,'msg':msg}
    return ctx
    
def get_class_data(gid,st,et):
    group = get_object_or_404(Group,id=gid)
    teachers_pre = [t for t in group.teachers.all()]
    teachers_ext = [gt.teacher for gt in GroupTeacher.objects.filter(group=group)]
#    teacher_age = get_agency_teacher_by_group(group)
    teachers = teachers_pre + teachers_ext
    teachers = list(set(teachers))
    tile_num = 0
    active_num = 0
    record_num = 0
    sms = 0
    msg = 0
    for te in teachers:
        d = get_teacher_data(te.id,st,et)
        tile_num += d['tile_num']
        active_num += d['active_num']
        record_num += d['record_num']
        sms += d['sms']
        msg += d['msg']
    ctx = {'group':group,'tile_num':tile_num,'active_num':active_num,'record_num':record_num,\
           'sms':sms,'msg':msg}
    return ctx

def get_student_data(sid,st=None,et=None):
    student = get_object_or_404(Student,id=sid)
    user = student.user
    tile_content_type = ContentType.objects.get_by_natural_key("kinger", "tile")
    acc_logs = Access_log.objects.filter(user=user,type=2)
    comments = Comment.objects.filter(user=user,content_type=tile_content_type)
    daily_vistors = DailyRecordVisitor.objects.filter(visitor=user)
    sms_replaies = SmsReplay.objects.filter(sender=user)
    messages = MessageRecipient.objects.filter(message__sender=user)
    tiles = Tile.objects.filter(creator=user)
    if st:
        acc_logs = acc_logs.filter(send_time__gte=st)
        comments = comments.filter(submit_date__gte=st)
        daily_vistors = daily_vistors.filter(visit_time__gte=st)
        sms_replaies = sms_replaies.filter(target__deal_date__gte=st)
        messages = messages.filter(message__sent_at__gte=st)
        tiles = tiles.filter(start_time__gte=st)
    if et:
        acc_logs = acc_logs.filter(send_time__lt=et)
        comments = comments.filter(submit_date__lt=et)
        daily_vistors = daily_vistors.filter(visit_time__lt=et)
        sms_replaies = sms_replaies.filter(target__deal_date__lt=et)
        messages = messages.filter(message__sent_at__lt=et)
        tiles = tiles.filter(start_time__lt=et)
        
    web_num = acc_logs.exclude(url__startswith='/api').count()
    api_num = acc_logs.filter(url__startswith='/api').count()
    img_num = DailyRecordVisitor.objects.tile_img_count(user,stime=st,etime=et,type='img')
    word_num = DailyRecordVisitor.objects.tile_img_count(user,stime=st,etime=et,type='word')
    record_num = DailyRecordVisitor.objects.tile_img_count(user,stime=st,etime=et,type='record')
    
    word_comments = 0
    img_comments = 0
    for c in comments:
        try:
            if c.content_object.new_type_id in [1,2]:
                img_comments += 1
            if c.content_object.new_type_id == 4:
                word_comments += 1
        except:
            pass

    content_type = ContentType.objects.get_for_model(Activity)
    active_num = daily_vistors.filter(target_content_type=content_type).count()
    sms = sms_replaies.count()
    msg = messages.count()
    imgs = tiles.filter(new_type_id=1).count()
    words = tiles.filter(new_type_id=4).count()
    ctx = {'student':student,'web_num':web_num,'active_num':active_num,'record_num':record_num,\
           'sms':sms,'msg':msg,'api_num':api_num,'img_num':img_num,'word_comments':word_comments,\
           'img_comments':img_comments,'word_num':word_num,'img_num':img_num,'imgs':imgs,'words':words}
    return ctx
    
@statistical_perm
def student_tile_visit(request, template_name="statistical/tile_visit.html"):
    school_id = request.GET.get('school_id')
    schools = School.objects.filter(is_delete=False).exclude(parent_id=0)
    ctx = {'schools':schools}
    if school_id:
        school = get_object_or_404(School,id=school_id)
        group_id = request.GET.get('group_id')
        stime = request.GET.get('stime','')
        etime = request.GET.get('etime','')
        if group_id:
            group = get_object_or_404(Group,id=group_id)
            group_pks = [group.id,]
        else:
            group = None
            groups = Group.objects.filter(school_id=school_id,is_delete=False).exclude(type=3)
            group_pks = [g.id for g in groups]
        st = datetime.datetime.strptime(stime,"%Y-%m-%d") if stime else None
        et = datetime.datetime.strptime(etime,"%Y-%m-%d") if etime else None
        users = [s.user for s in Student.objects.filter(group_id__in=group_pks)]
        data = tile_visit_data(users,st,et) 
        ctx.update({'data':data,'school':school,'group':group,'stime':stime,'etime':etime})
    return render(request, template_name,ctx)

def tile_visit_data(users,st=None,et=None):
    tile_content_type = ContentType.objects.get_by_natural_key("kinger", "tile")
    daily_vistors = DailyRecordVisitor.objects.filter(visitor__in=users).order_by('visit_time')
    if st:
        daily_vistors = daily_vistors.filter(visit_time__gte=st)
    if et:
        daily_vistors = daily_vistors.filter(visit_time__lt=et)
    
    records = []
    for t in daily_vistors:
        try:
            tile = t.target
            records.append({'time':t.visit_time,'uname':t.visitor.username,'group':t.visitor.student.group,\
                            'tid':tile.id,'tips':tile.is_tips,'cat':tile.new_category.name}) 
        except:
            pass
    return records

def page_request_time(request):
    import subprocess
    import sys
    import datetime
    result = '<div>'
    f = request.GET.get('f','edu_index.txt')
    ps = request.GET.get('ps','')
    site = request.GET.get('site','test.weixiao178.com/')
    file_path = FILE_PATH + '/stal/' + f
#    rs = open(file_path,'a+')
#    rs.write(str(datetime.datetime.now()) + ps)
    for x in range(0,10):
        p = subprocess.Popen("time curl -s -o test.html " + site, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        for line in p.stdout.readlines():
#            rs.write(line)
            result += '<p>' + line.split('user')[0].split('sys')[0] + '</p>'
    result += '</div>'
#    rs.close()
    return HttpResponse('<div>' + str(datetime.datetime.now()) + ps + '</div>' + result)
