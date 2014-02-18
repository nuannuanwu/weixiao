# -*- coding: utf-8 -*-

from django.conf import settings
from django.shortcuts import redirect, render, get_object_or_404
from django.core.exceptions import ObjectDoesNotExist

from kinger.models import Cookbook,CookbookRead,TileCategory,Sms,RelevantStaff,NewTileCategory,\
        Tile,Group,School,Activity,Student,GroupTeacher,Teacher,Sms
from django.db.models import Q
from api.helpers import query_range_filter,get_agency_teacher_by_group
from userena.contrib.umessages.models import Message, MessageRecipient, MessageContact
from django.views.decorators.csrf import csrf_exempt
from django.contrib.admin.views.decorators import staff_member_required

from aq.views.default import get_unread_mentor_count as unread_mentor
from waiter.views.default import get_unread_waiter_count as unread_waiter

from kinger import helpers
from django.http import Http404
from django.http import HttpResponse

from django.core.urlresolvers import reverse
from django.contrib.sites.models import Site

from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from django.db import connection
import re
import urllib,urllib2
import os, tempfile, zipfile  
from django.http import HttpResponse  
from django.core.servers.basehttp import FileWrapper  
from StringIO import StringIO  
from zipfile import ZipFile
from django.utils.http import urlquote
from django.utils.encoding import smart_str, smart_unicode

import datetime,time
from decimal import Decimal as D
try:
    import simplejson as json
except ImportError:
    import json

try:
    from sae.taskqueue import Task, TaskQueue
except:
    pass
    
import sys
reload(sys)
sys.setdefaultencoding('utf8') 

SITE_INFO = Site.objects.get_current()
 
@staff_member_required
def tile_change_form(request): 
    is_tips = request.POST.get('is_tips','0')
    
    category_list = []
    parent_category = TileCategory.objects.filter(parent_id=0,is_tips=is_tips).all()
    for p in parent_category:
        sub_category = TileCategory.objects.filter(parent_id=p.id,is_tips=is_tips).all()
        category_list.append({'id':p.id,'name':p.name,'parent_id':p.parent_id})
        for s in sub_category:
            category_list.append({'id':s.id,'name':s.name,'parent_id':s.parent_id})
     
    return HttpResponse(json.dumps(category_list))

@staff_member_required
def rev_tile_change(request): 
    is_tips = int(request.POST.get('is_tips','0'))
    category_list = []

    parent_category = NewTileCategory.objects.filter(parent_id=0,is_tips=is_tips,id__gte=1000).order_by('id')
    for p in parent_category:
        sub_category_first = NewTileCategory.objects.filter(parent_id=p.id).all()
        category_list.append({'id':p.id,'name':p.name,'parent_id':p.parent_id,'type':0})
        for f in sub_category_first:
            sub_category_second = NewTileCategory.objects.filter(parent_id=f.id).all()
            category_list.append({'id':f.id,'name':f.name,'parent_id':f.parent_id,'type':1})
            for s in sub_category_second:
                sub_category_third = NewTileCategory.objects.filter(parent_id=s.id).all()
                category_list.append({'id':s.id,'name':s.name,'parent_id':s.parent_id,'type':2})
                for t in sub_category_third:
                    category_list.append({'id':t.id,'name':t.name,'parent_id':t.parent_id,'type':3})
    return HttpResponse(json.dumps(category_list))

@staff_member_required
def cookbook_info(request,cid,template_name="admin/includes/cookbook_info.html"):
    """食谱访数据问统计"""

    cookbook = Cookbook.objects.get(id=cid)
    users = [s.user for s in cookbook.get_student()]
    user_num = len(users)
    cookbookreads = []
    read_num,send_num = 0,0
    
    cookbookreads = CookbookRead.objects.filter(cookbook=cookbook,date=cookbook.date)
    if cookbookreads:
        read_num = cookbookreads.filter(is_read=True).count()
        send_num = cookbookreads.filter(is_send=True).count()
    
    ctx = {"cookbook":cookbook,"user_num":user_num,"cookbookreads":cookbookreads,"read_num":read_num,"send_num":send_num}
    return render(request, template_name, ctx)

@staff_member_required
def not_logged_in_sms(request,template_name="admin/includes/not_logged_in_sms.html"):
    """已发送的未登录短信列表"""

    msgs = Sms.objects.filter(type_id=98,is_send=True)
    ctx = {"msgs":msgs}
    return render(request, template_name, ctx)


#发送未读导师及客服提醒
def send_staff_unread(request): 
    unread_mentors = unread_mentor()
    unread_waiters = unread_waiter()
    if not unread_mentors and not unread_mentors:
        return HttpResponse('')
    
    staffs = RelevantStaff.objects.exclude(send_mentor=False,send_waiter=False)
    
    for s in staffs:
        #发送短信,已有队列
        if s.send_mentor and unread_mentors and s.mobile:
            msg = "<" + SITE_INFO.name + ">导师留言后台有" + str(unread_mentors) + "条新客户留言. 请及时登录回复. 登录地址: " + SITE_INFO.domain + reverse('aq')
            helpers.send_staff_mobile(s.mobile,msg)
        if s.send_waiter and unread_waiters and s.mobile:
            msg = "<" + SITE_INFO.name + ">客服后台有" + str(unread_waiters) + "条新客服留言. 请及时登录回复. 登录地址: " + SITE_INFO.domain + reverse('waiter')
            helpers.send_staff_mobile(s.mobile,msg)
    
    for s in staffs:
        #发送邮件队列
        data = {"staff_id":s.id,"unread_mentors":unread_mentors,"unread_waiters":unread_waiters}
        payload = urllib.urlencode(data)
        #执行转换
        try:
            queue = TaskQueue('notice2staff')
            queue.add(Task("/backend/taskqueue/notice2staff",payload))
        except:
            st = helpers.StaffTrans()
            st.kinger_notice_to_staff(s.id,unread_mentors,unread_waiters)
  
    return HttpResponse('')


#@staff_member_required
def school_tiles_info(request,template_name="admin/includes/school_tiles_info.html"): 
    school_id = request.GET.get('sid')
    groups = Group.objects.filter(school_id=school_id,is_delete=False).exclude(type=3)
    tile_count = activity_count = record_count = message_count = 0
    tile_list = []
    activity_list = []
    record_list = []
    message_list = []
    sms_list = []
    par_sms_list = []
    for g in groups:
        tiles = Tile.objects.filter(group__id=g.id).exclude(new_type_id=4).order_by("-ctime","-id")
        tile_list.append({'id':g.id,'name':g.name,'num':tiles.count()})
        tile_count += tiles.count()
        
        activitys = Activity.objects.filter(group__id=g.id)
        activity_list.append({'id':g.id,'name':g.name,'num':activitys.count()})
        activity_count += activitys.count()
        
        users = [s.user for s in Student.objects.filter(group_id=g.id)]
        records = Tile.objects.filter(user__in=users,type_id__in=[4,5,6,7,8,101,102])
        record_list.append({'id':g.id,'name':g.name,'num':records.count()})
        record_count += records.count()
        
        teachers_pre = [t for t in g.teachers.all()]
        teachers_ext = [gt.teacher for gt in GroupTeacher.objects.filter(group=g)]
        teacher_age = get_agency_teacher_by_group(g)
        teachers = teachers_pre + teachers_ext + teacher_age
        teachers = list(set(teachers))
        users = [t.user for t in teachers]
        messages = Message.objects.filter(sender__in=users)
        message_list.append({'id':g.id,'name':g.name,'num':messages.count()})
        message_count += messages.count()
        
    t_users = [tu.user for tu in Teacher.objects.filter(school_id=school_id,is_delete=False)]
    smses = Sms.objects.filter(sender__in=t_users)
    from django.db.models import Count
    t_user_pks = [sms['sender'] for sms in smses.values('sender').annotate(num=Count('sender'))]
    for u in t_user_pks:
        try:
            user = User.objects.get(id=u)
        except:
            user = None
        total = 0
        total = Sms.objects.filter(sender_id=u).count()
        num = 0
        num = Sms.objects.filter(sender_id=u,is_send=True).count()
        sms_list.append({'id':u,'num':num,'total':total,'user':user})   
    print sms_list,'ssssssssssssssss'
    
    s_users = [st.user for st in Student.objects.filter(school_id=school_id,is_delete=False)]
    smses = Sms.objects.filter(sender__in=s_users)
    from django.db.models import Count
    s_user_pks = [sms['sender'] for sms in smses.values('sender').annotate(num=Count('sender'))]
    for u in s_user_pks:
        try:
            user = User.objects.get(id=u)
        except:
            user = None
        total = 0
        total = Sms.objects.filter(sender_id=u).count()
        num = 0
        num = Sms.objects.filter(sender_id=u,is_send=True).count()
        par_sms_list.append({'id':u,'num':num,'total':total,'user':user})   
    
    ctx = {'tile_count':tile_count,'activity_count':activity_count, 'record_count':record_count,\
            'message_count':message_count,'tile_list':tile_list,'activity_list':activity_list,\
            'record_list':record_list,'message_list':message_list,'sms_list':sms_list,'par_sms_list':par_sms_list}
#    return HttpResponse(ctx)
    return render(request, template_name, ctx)



@staff_member_required
def special_group_for_school(request): 
    schools = School.objects.filter(parent_id__gt=0,is_delete=False)
    count = 0
    for s in schools:
        group,created = Group.objects.get_or_create(name="全园班级",school_id=s.id,type=3,creator=s.creator,grade_id=0)
        if created:
            count += 1
    return HttpResponse("total add: " + str(count))

def get_group_messages(request):
    from api.helpers import query_range_filter,get_agency_teacher_by_group
    from userena.contrib.umessages.models import Message, MessageRecipient, MessageContact
    gid = request.GET.get('gid')
    group = Group.objects.get(id=gid)
    teachers_pre = [t for t in group.teachers.all()]
    teachers_ext = [g.teacher for g in GroupTeacher.objects.filter(group=group)]
    teacher_age = get_agency_teacher_by_group(group)
    teachers = teachers_pre + teachers_ext + teacher_age
    teachers = list(set(teachers))
    users = [t.user for t in teachers]
    messgges = Message.objects.filter(sender__in=users)
    return HttpResponse(str(group.name) +": " + str(messgges.count()))

def get_user_messages(request,template_name="admin/includes/get_user_messages.html"):
    from api.helpers import query_range_filter,get_agency_teacher_by_group
    from userena.contrib.umessages.models import Message, MessageRecipient, MessageContact
    uid = request.GET.get('uid','0')
    
    smses = Sms.objects.filter(sender__id=uid)
    ctx = {'smses':smses}
    return render(request, template_name, ctx)
    
def get_tile_image(request):
    gid = request.GET.get('gid')
    group = Group.objects.get(id=gid)
    tiles = Tile.objects.filter(group=group)
    total = tiles.count()
    url_list = []
    per = 400
    download_url = reverse('admin_groupimg_download',kwargs={'gid':group.id})
    parts = total / per + 1
    html = "<div><p>" + group.school.name + ":" + group.name + "</p><p>图片总数：" + str(total) + "</p>"
    if parts == 1:
        html += "<p><a href='" + download_url + "'>打包下载</a></p>&nbsp;&nbsp;"
    else:
        p_list = sorted(list(range(parts)),reverse=True)
        print p_list,'ppppppp'
        for p in p_list:
            url = download_url + "?part=" + str(p)
            start = p * per + 1
            end = p * per + per if p * per + per < total else total
            html += "<div><p><a href='" + url + "'>打包下载[" + str(start) + "-" + str(end) + "]</a></p>"
    html += "</div>"
    return HttpResponse(html)

def download_zipfile(request,gid):  
    """打包下载公文附件""" 
    group = Group.objects.get(id=gid)
    tiles = Tile.objects.filter(group=group)
    total = tiles.count()
    files = [t.img for t in tiles]
    p = int(request.GET.get('part',0))
    start = p * 50 + 1
    end = p * 50 + 50 if p * 50 + 50 < total else total
    files = files[start:end]

    in_memory = StringIO()  
    zip = ZipFile(in_memory, "a")  
    for f in files: 
        try:
            f_name = str(f).split('/')[-1]
            opener1 = urllib2.build_opener()
            page1 = opener1.open(f.url)
            zip.writestr(f_name,page1.read()) 
        except:
            pass

    for file in zip.filelist:  
        file.create_system = 0      
          
    zip.close()  
    
    filename = group.name + '.zip'
    if "MSIE" in request.META['HTTP_USER_AGENT']:
        filename=urlquote(filename)
    else:
        filename=smart_str(filename)
  
    response = HttpResponse(mimetype="application/zip")  
    response["Content-Disposition"] = 'attachment; filename=%s' % filename
      
    in_memory.seek(0)      
    response.write(in_memory.read())
      
    return response  
