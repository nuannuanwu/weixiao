# -*- coding: utf-8 -*-

from django.conf import settings
from django.shortcuts import redirect, render, get_object_or_404
from django.core.exceptions import ObjectDoesNotExist

from kinger.models import Char,Teacher, Student, School,Access_log,Tile,Activity,TileToActivity,Cookbook,\
        CookbookRead,CookbookType,EventType,Group,Access,Role,TileVisitor,DailyRecordVisitor
from django.contrib.comments import Comment
from django.db.models import Q
from django.contrib.auth.decorators import login_required
from kinger.profiles.models import Profile
from kinger import helpers
from django.contrib.contenttypes.models import ContentType

from django.http import Http404
from django.http import HttpResponse

from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from django.db import connection
import re

import datetime,time
from decimal import Decimal as D
try:
    import simplejson as json
except ImportError:
    import json

from oss_extra.storage import AliyunStorage
import urllib2
import os
import oss.oss_api
import oss.oss_util
try:
    import sae.storage
except:
    pass

def put_img_object_to_sae(sae_storage,img):
    try:
        opener1 = urllib2.build_opener()
        page1 = opener1.open(img.url)
        my_picture = page1.read()
        ob = sae.storage.Object(my_picture)
        sae_storage.put('base',img.name,ob)
        count = count + 1
        return True
    except:
        return False

def img_sae_to_sae(request):
    try:
        sae_storage = sae.storage.Client(accesskey='jyoz12zlo0', secretkey='53l04k34jz54m0xw4mjy2l4yiillzmwwxjkzli3l', prefix='jytn365')
        obj_list = [s['name'] for s in sae_storage.list("base")]
    except:
        return HttpResponse('')
    count = 0

    cbook_type = [c.img for c in CookbookType.objects.all().exclude(img='')]
    cbook_type = [val for val in cbook_type if not val.name in obj_list]
    for i in cbook_type:
        count = count + 1 if put_img_object_to_sae(sae_storage,i) else count
    
    event_type = [e.img for e in EventType.objects.all().exclude(img='')]
    event_type = [val for val in event_type if not val.name in obj_list]
    for i in event_type:
        count = count + 1 if put_img_object_to_sae(sae_storage,i) else count
    
    group_img = [g.logo for g in Group.objects.all().exclude(logo='')]
    group_img = [val for val in group_img if not val.name in obj_list]
    for i in group_img:
        count = count + 1 if put_img_object_to_sae(sae_storage,i) else count
    
    profile_img = [p.mugshot for p in Profile.objects.all().exclude(mugshot='')]
    profile_img = [val for val in profile_img if not val.name in obj_list]
    for i in profile_img:
        count = count + 1 if put_img_object_to_sae(sae_storage,i) else count
    
    tile_img = [t.img for t in Tile.objects.all().exclude(img='')]
    tile_img = [val for val in tile_img if not val.name in obj_list]
    
    for i in tile_img:
        count = count + 1 if put_img_object_to_sae(sae_storage,i) else count
    
    return HttpResponse("images_count:" + str(count))

def put_img_object_to_oss(oss_storage,img):
    try:
        opener1 = urllib2.build_opener()
        page1 = opener1.open(img.url)
        my_picture = page1.read()
        #content_type = oss.oss_util.get_content_type_by_filename(img.url)
        oss_s = AliyunStorage(location="zhuyuan-test")
        oss_s._put_file(img.name,my_picture)
        #oss_storage.put_object_from_string("zhuyuan-test",img.name,my_picture,content_type)
        return True
    except:
        return False

def is_exist_in_oss(oss_storage,img):
    try:
        obj = oss_storage.get_object("zhuyuan-test",img.name)
        if obj.status == 200:
            return True
    except:
        pass
    return False

def img_sae_to_oss(request):
    oss_storage = oss.oss_api.OssAPI(settings.OSS_HOST,settings.OSS_ACCESS_KEY_ID,settings.OSS_SECRET_ACCESS_KEY)
    obj_list = oss_storage.list_objects("zhuyuan-test")
    count = 0

    cbook_type = [c.img for c in CookbookType.objects.all().exclude(img='')]
    #cbook_type = [val for val in cbook_type if not is_exist_in_oss(oss_storage,val)]
    cbook_type = [val for val in cbook_type if not val.name in obj_list]
    for i in cbook_type:
        count = count + 1 if put_img_object_to_oss(oss_storage,i) else count
    
    
    event_type = [e.img for e in EventType.objects.all().exclude(img='')]
    #event_type = [val for val in event_type if not is_exist_in_oss(oss_storage,val)]
    event_type = [val for val in event_type if not val.name in obj_list]
    for i in event_type:
        count = count + 1 if put_img_object_to_oss(oss_storage,i) else count
   
    
    group_img = [g.logo for g in Group.objects.all().exclude(logo='')]
    #group_img = [val for val in group_img if not is_exist_in_oss(oss_storage,val)]
    group_img = [val for val in group_img if not val.name in obj_list]
    for i in group_img:
        count = count + 1 if put_img_object_to_oss(oss_storage,i) else count
   
    
    profile_img = [p.mugshot for p in Profile.objects.all().exclude(mugshot='')]
    #profile_img = [val for val in profile_img if not is_exist_in_oss(oss_storage,val)]
    profile_img = [val for val in profile_img if not val.name in obj_list]
    for i in profile_img:
        count = count + 1 if put_img_object_to_oss(oss_storage,i) else count
   
    
    tile_img = [t.img for t in Tile.objects.all().exclude(img='')]
    #tile_img = [val for val in tile_img if not is_exist_in_oss(oss_storage,val)]
    tile_img = [val for val in tile_img if not val.name in obj_list]
    for i in tile_img:
        count = count + 1 if put_img_object_to_oss(oss_storage,i) else count
    
    return HttpResponse("images_count:" + str(count))

@login_required
def pinyin_init(request):
    """
    处理之前未转成拼音数据
    """
    if not request.user.is_staff:
        return render(request, "403.html")
    teachers = Teacher.objects.filter(pinyin='')
    teacher_count = teachers.count()

    students = Student.objects.filter(pinyin='')
    students_count = students.count()

    for t in teachers:
        t.save()

    for s in students:
        s.save()

    message = "teachers_count:" + str(teacher_count) +"<br>"
    message += "students_count:" + str(students_count)

    return HttpResponse(message)
    
@login_required
def tile_microsecond_init(request):
    """"微妙级别日期初始化"""
    if not request.user.is_staff:
        return render(request, "403.html")
    tiles = Tile.objects.exclude(microsecond__gt=0.00)
    for t in tiles:
        t.save()
    message = "tiles_count:" + str(tiles.count())
    return HttpResponse(message)

@login_required
def active_data_migration(request):
    """瓦片日常活动内容数据迁移"""
    if not request.user.is_staff:
        return render(request, "403.html")
    tiles = Tile.objects.filter(is_tips=0,category_id=9,group__isnull=False)
    i = 0
    for t in tiles:
        try:
            has_migration = TileToActivity.objects.get(tile=t)
        except:
            has_migration = None
            
        if not has_migration:
            active_description = get_active_description(t.description)
            if active_description:
                active = Activity()
                active.creator = t.creator
                active.user = t.user
                active.group_id = t.group_id
                active.description = json.dumps({"events":active_description})
                active.start_time = t.start_time
                active.microsecond = t.microsecond
                active.save()
                migration = TileToActivity()
                migration.tile = t
                migration.active = active
                migration.save()
                i += 1
    message = "actives_count:" + str(i)
    return HttpResponse(message)
            

def get_active_description(desc):
    """判断日常活动内容是否为空"""
    daily = {"events":""}
    try:
        daily = json.loads(desc)
    except:
        return False
    if not daily["events"]:
        return False 
    else:
        i = 0
        for d in daily['events']:
            if not d['content']:
               i += 1 
        if i == len(daily['events']):
            return False
    return daily["events"]

@login_required
def parent_info(request,template_name="backend/parent_info.html"):
    """显示所有学校的家长信息,可根据所传的参数筛选，
        group:班级id
        school:学校id
    """
    if not request.user.is_staff:
        if request.user.username != 'yyb':
            return render(request, "403.html")
    group_id = request.GET.get("group_id",'')
    school_id = request.GET.get("school_id",'')
    
    sql_where = ''
    if group_id:
        sql_where += " AND class.id=" + group_id
    if school_id:
        sql_where += " AND school.id=" + school_id
    
    sql = "SELECT school.name AS scname,class.name AS clname, student.name AS stname, `user`.id AS uid, `user`.username, `user`.last_login,\
    `user`.date_joined FROM `kinger_school` AS school LEFT JOIN `kinger_group` AS class ON class.`school_id` = school.`id` \
    LEFT JOIN `kinger_student` AS student ON student.`group_id` = class.`id` LEFT JOIN `auth_user` AS `user` ON \
    student.`user_id` = `user`.`id` WHERE school.is_delete=0 AND class.is_delete=0 AND student.is_delete=0 " + sql_where + " ORDER BY school.id, class.id, student.id"
    
    cursor = connection.cursor()
    cursor.execute(sql)
    desc = cursor.description
    rows = [dict(zip([col[0] for col in desc], row)) for row in cursor.fetchall()]
    
    for r in rows:
        uid = r['uid']
        if r['last_login'] != r['date_joined']:
            r['last_login'] = r['last_login'].strftime('%Y-%m-%d %H:%M:%S')
        else:
            r['last_login'] = ''
        r.pop('date_joined')
        comment = Comment.objects.filter(user_id=uid).count()
        access = Access_log.objects.filter(user_id=uid)
        r['comment'] = comment
        r['login'] = access.filter(type=1).count()
        r['access'] = access.filter(type=2).count()
        try:
            r['last_access'] = access.filter(type=2)[0].send_time.strftime('%Y-%m-%d %H:%M:%S')
        except:
            r['last_access'] = ''
            
    ctx = {"info":rows}
    return render(request, template_name, ctx)

@login_required
def parent_access_info(request,uid,template_name="backend/parent_access_info.html"):
    """家长登录或访问首页历史记录"""
    if not request.user.is_staff:
        return render(request, "403.html")
    ty = request.GET.get("ty")
    access = Access_log.objects.filter(user_id=uid)
    if ty == 'login':
        access = access.filter(type=1)
    else:
        access = access.filter(type=2)
        
    ctx = {"access":access,"ty":ty}
    return render(request, template_name, ctx)

@login_required
def video_object_to_code(request):
    """视频数据格式转换"""
    if not request.user.is_staff:
        return render(request, "403.html")
    count = 0
    tiles = Tile.objects.filter(is_tips=1)
    for t in tiles:
        value = t.content
        videos = ''
        video = re.findall(r'(<video.*?</video>)',value)
        if video:
            count = count + 1
            for v in video:
                src = re.findall(r'src="(.*?)"',v)
                for s in src:
                    videos =videos +  "[[" + str(s) + "]]"
                    
                strinfo = re.compile(v)
                value = strinfo.sub(videos,value)
                t.content = value
            t.save()
    message = "tiles_count:" + str(count)
    return HttpResponse(message)

def inner_role_for_school(request):
    from oa.helpers import school_inner_role
    schools = School.objects.filter(is_delete=False)
    count = 0
    for s in schools:
        if school_inner_role(s):
            count += 1
    message = "roles_count:" + str(count)
    return HttpResponse(message)

def default_access_for_teacher(request):
    from oa.helpers import set_teacher_default_access
    teachers = Teacher.objects.filter(is_delete=False)
    count = 0
    for t in teachers:
        print t,'tttttttttttttt'
        if set_teacher_default_access(t):
            count += 1
    message = "roles_count:" + str(count)
    return HttpResponse(message)
    
def tile_visit_trans(request):
    history = TileVisitor.objects.all()
    count = 0
    content_type = ContentType.objects.get_for_model(Tile)
    for h in history:
        try:
            new,create = DailyRecordVisitor.objects.get_or_create(visitor=h.visitor,target_content_type=content_type,\
                target_object_id=h.tile_id,visit_time=h.visit_time,microsecond=h.microsecond)
            count += 1
        except:
            pass
    message = "trans_count:" + str(count)
    return HttpResponse(message)