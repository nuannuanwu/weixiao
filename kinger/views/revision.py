# -*- coding: utf-8 -*-
#from django.http import HttpResponse
from django.conf import settings
from django.utils.translation import ugettext as _
from django.shortcuts import redirect, render, get_object_or_404
from django.core.exceptions import ObjectDoesNotExist
from kinger.helpers import get_redir_url,media_path,unread_count,get_month_theme,add_daily_record_visitor
# from django.shortcuts import render_to_response,render
# from django.template import RequestContext
from django.dispatch import receiver
from django.contrib import messages
from django.contrib.comments import Comment
from django.contrib.comments.views.moderation import perform_delete
from django.contrib.comments.signals import comment_was_posted
from django.contrib import comments
from django.contrib.auth.decorators import login_required, permission_required
from kinger.helpers import get_redir_url,media_path,unread_count,ajax_ok,get_channel,get_month_theme

from kinger.models import Tile, TileTag, TileType, Student,Sms, VerifySms,NewTileCategory,Mentor,\
Cookbook,CookbookType,Access_log,Comment_relation,Activity,TileVisitor,DailyRecordVisitor,\
CookbookRead,Tile,TileRecommend,WebSite,Album,Photo,Part,Link,Teacher,Student,CookbookSet
from django.db.models import Q
from django.contrib.contenttypes.models import ContentType
from kinger import helpers
import calendar
import datetime
import time
from django.http import Http404
from django.http import HttpResponse

from kinger import helpers
from django.contrib.auth.models import User
from django.core.cache import cache
from kinger.settings import STATIC_URL,CTX_CONFIG
from django.core.paginator import Paginator
from django.core.urlresolvers import reverse
from kinger.forms import MobileForm, PwdResetForm, PwdMobileForm
from kinger.profiles.models import Profile
from notifications import notify
from django.contrib.auth import views as auth_views
from django.contrib.sites.models import get_current_site
from django.db import connection
from django.http import Http404
from django.contrib.auth import REDIRECT_FIELD_NAME
from django.contrib.sites.models import Site
try:
    import simplejson as json
except ImportError:
    import json
from oa.helpers import get_parent_domain
from django.contrib.auth import authenticate, login, logout, REDIRECT_FIELD_NAME
from userena.forms import (SignupForm, SignupFormOnlyEmail, AuthenticationForm,
                           ChangeEmailForm, EditProfileForm)
from manage.decorators import profile
import random
from django.db.models import Max

import logging
logger = logging.getLogger(__name__)

@login_required
def time_axis(request, template_name="kinger/revision/baby_axis.html"):
    user = request.user
    category = NewTileCategory.objects.filter(is_tips=0)
    tile_category = [c.id for c in category.exclude(parent_id=1130).exclude(id=9)] 
    record_category = category.filter(parent_id=1130)
    record_category_pks = [r.id for r in record_category] 
    
    tiles = Tile.objects.get_tiles_baby(request.user).filter(new_category_id__in=tile_category).order_by("-microsecond")
    records = Tile.objects.get_tiles_baby(request.user).filter(new_category_id__in=record_category_pks)
    actives = Activity.objects.filter(get_q_user(request.user))
    cookbook_date = get_cookbook_date(request.user)
    date_coo = [dc[0] + datetime.timedelta(days=-1) for dc in cookbook_date if check_user_cookbook_by_date(user,dc[0])]
    date_coo = sorted(list(set(date_coo)),reverse=True)
    date_sel = request.GET.get('date')
    page = int(request.GET.get("page",'1'))
    date_sel = date_sel if date_sel else str(datetime.datetime.now().date())
    day_count = 0
    d_data = []
    for i in range(3):
        if day_count > 3:break
        st,et = get_day_micro_begin2end(date_sel)
        day = None
        day_list = []
        ts = tiles.filter(microsecond__lte=et)[:1]
        day_tile = ts[0].start_time.date() if ts.count() else day
        if day_tile:
            day_list.append(day_tile)
        rs = records.filter(microsecond__lte=et)[:1]
        day_record = rs[0].start_time.date() if rs.count() else day
        if day_record:
            day_list.append(day_record)
        cs = actives.filter(microsecond__lte=et)[:1]
        day_acctive = cs[0].start_time.date() if cs.count() else day
        if day_acctive:
            day_list.append(day_acctive)
        c_day = datetime.datetime.strptime(date_sel,"%Y-%m-%d").date()
        date_coo = [d for d in date_coo if not d > c_day]
        day_cookbook = date_coo[0] if len(date_coo) else day
        if day_cookbook:
            day_list.append(day_cookbook)
            
        day = max(day_list) if len(day_list) else None
       
        if not ts.count() and not rs.count() and not cs.count() and not len(date_coo):
#            d_data = []
            break
        else:
            date_sel = str(day + datetime.timedelta(days=-1))
            start_date = datetime.datetime(day.year, day.month, day.day)
            s_time = time.mktime(start_date.timetuple())
            end_date = datetime.datetime(day.year, day.month, day.day,23,59,59)
            e_time = time.mktime(end_date.timetuple())
            d_tiles = tiles.filter(microsecond__gte=s_time,microsecond__lte=e_time)
            d_records = get_daily_category_tiles(records, record_category, day)  
            d_cookbooks = get_daily_cook_books(request.user,datetime.datetime.fromordinal(day.toordinal()))
    
            d_actives = actives.filter(start_time__startswith=day)
            d_data.append({'tiles':d_tiles,'date':day,'records':d_records,'cookbooks':d_cookbooks,'actives':d_actives})
    print page,'date_sel--------------------------'
    if request.is_ajax():
        template_name = "kinger/revision/baby_axis_container.html"
        return render(request, template_name, {'data':d_data,'date_sel':date_sel,'page':page})
    
    ctx={'data':d_data,'is_date':True,'channel':'baby','date_sel':date_sel,'page':page}
    return render(request, template_name, ctx)

#@login_required
#def time_axis(request, template_name="kinger/revision/baby_axis.html"):
#    date_tiles = [dt[0].date() for dt in get_baby_tile_date(request.user)]
#    date_act = [da[0].date() for da in get_active_date(request.user)]
#    cookbook_date = get_cookbook_date(request.user)
#    user = request.user
#    if cookbook_date:
#        date_coo = [dc[0] + datetime.timedelta(days=-1) for dc in cookbook_date if check_user_cookbook_by_date(user,dc[0])]
#        print date_coo,'date_coo--------------------------'
#        dates = date_tiles + date_act + date_coo
#    else:
#        dates = date_tiles + date_act
#        
#    dates = sorted(list(set(dates)),reverse=True)
#    effective_date = [str(x) for x in dates]
#    current_date = datetime.datetime.now().date()
#    effective_date.append(str(current_date))
#    
#    date_sel = request.GET.get('date')
#    if date_sel:
#        date_sel = datetime.datetime.strptime(date_sel,"%Y-%m-%d").date()
#        dates = [d for d in dates if not d > date_sel]
#    category = NewTileCategory.objects.filter(is_tips=0)     
#    tiles = Tile.objects.get_tiles_baby(request.user).filter(new_category__in=category)\
#        .exclude(new_category__parent_id=1130).exclude(category_id=9).order_by("-microsecond")
#    records = Tile.objects.get_tiles_baby(request.user).filter(new_category__parent_id=1130)
#    actives = Activity.objects.filter(get_q_user(request.user))
#
#    d_data = []
#    page = int(request.GET.get("page",'1'))
#    start = (page - 1) * 3
#    end = page * 3
#    page_date = dates[start:end]
#    for d in page_date:
#        start_date = datetime.datetime(d.year, d.month, d.day)
#        s_time = time.mktime(start_date.timetuple())
#        end_date = datetime.datetime(d.year, d.month, d.day,23,59,59)
#        e_time = time.mktime(end_date.timetuple())
#        d_tiles = tiles.filter(microsecond__gte=s_time,microsecond__lte=e_time)
#        d_records = get_daily_category_tiles(records, category, d)  
#        d_cookbooks = get_daily_cook_books(request.user,datetime.datetime.fromordinal(d.toordinal()))
#
#        d_actives = actives.filter(start_time__startswith=d)
#        d_data.append({'tiles':d_tiles,'date':d,'records':d_records,'cookbooks':d_cookbooks,'actives':d_actives})
#    
#    if request.is_ajax():
#        template_name = "kinger/revision/baby_axis_container.html"
#        return render(request, template_name, {'data':d_data,'page':page})
#    
#    ctx={'data':d_data,'dates':dates,'is_date':True,'channel':'baby','page':page,'effective_date':effective_date}
#    return render(request, template_name, ctx)

#@profile("edu_index.prof")
def edu_index(request, template_name = "kinger/revision/edu_index.html"):
    """"""
    site = helpers.get_domain_redirct(request)
    #站点域名
    if site:
        template_name="oa/site/index.html"
        ctx = index_for_site(request,site)
        return render(request, template_name,ctx)
    #微校域名
    else:
        if request.is_ajax():
            template_name = "kinger/revision/edu_index_container.html"
        ctx = index_for_weixiao(request)
        return render(request, template_name, ctx)


def life_edu(request, template_name = "kinger/revision/edu_index.html"):
    """"""
    user = request.user
    category = NewTileCategory.objects.all()
    content_type = ContentType.objects.get_for_model(Tile)
    
    if request.user.is_authenticated():
        #用户登录日志
        log = Access_log()
        log.type = 2
        log.user = user
        log.url = request.get_full_path()
        log.save()
                                                                           
        category = category.filter(is_tips=2) 
        tiles = Tile.objects.get_tiles_life(user)
    else:
        tiles = Tile.objects.get_life_tiles_all_unlogin()
    ctx = {}
    
    cid = request.GET.get('cid',3000)
    ty = request.GET.get('ty','')
    if ty == "pic":
        q = Q(new_type_id__in=[1,4])
    elif ty == "video":
        q = Q(new_type_id=2)
    else:
        q = Q()
    cat_obj = get_object_or_404(NewTileCategory, pk=cid)
    cat_list_pks = helpers.category_sub_and_par(cat_obj)
    tiles = tiles.filter(new_category_id__in=cat_list_pks).filter(q).order_by("-microsecond")
#    recommend_tiles = [t for t in tiles.order_by("-n_comments")[0:10]]
    recommend_tiles = [rt.tile for rt in TileRecommend.objects.all()[0:10]]
    local_url = reverse('kinger_life_edu_index')
    
    ctx.update({"tiles": tiles, "content_type": content_type,"category":category,"ty":ty,\
                "recommend_tiles":recommend_tiles,"channel":"life","cid":cid,"show_type":True,"local_url":local_url})
    if request.is_ajax():
        page = int(request.GET.get("page",'1'))
        start = (page - 1) * 15
        end = page * 15
        tiles = tiles[start:end]
        ctx['tiles'] = tiles
        template_name = "kinger/revision/edu_index_container.html"
        return render(request, template_name, ctx)
    return render(request, template_name, ctx)

@login_required
def baby_index(request, template_name = "kinger/revision/baby_index.html"):
    """"""
    date_tiles = [dt[0].date() for dt in get_baby_tile_date(request.user)]
    date_act = [da[0].date() for da in get_active_date(request.user)]
    cookbook_date = get_cookbook_date(request.user)
    if cookbook_date:
        date_coo = [dc[0] + datetime.timedelta(days=-1) for dc in get_cookbook_date(request.user)]
        dates = date_tiles + date_act + date_coo
    else:
        dates = date_tiles + date_act
        
    dates = sorted(list(set(dates)),reverse=True)
    effective_date = [str(x) for x in dates]
    current_date = datetime.datetime.now().date()
    effective_date.append(str(current_date))
    
    channel_ctx = {}
    user = request.user
    category = NewTileCategory.objects.all()
    content_type = ContentType.objects.get_for_model(Tile)
    tiles = []
    
    #用户登录日志
    log = Access_log()
    log.type = 2
    log.user = user
    log.url = request.get_full_path()
    log.save()
    
    current_time = datetime.datetime.now()  
    category = category.filter(is_tips=0)    
    tiles = Tile.objects.get_tiles_baby(user).filter(new_category__in=category).exclude(new_category__parent_id=1130).exclude(new_category_id=9)
    record_tiles = Tile.objects.get_tiles_baby(user).filter(new_category__parent_id=1130)
    today_daily_tiles = get_daily_category_tiles(record_tiles, category, current_time)
   
    latest_active = get_daily_activitie_tiles(user)
    latest_cookbook = get_daily_cook_books(user,current_time)
    is_read = 1 if CookbookRead.objects.filter(user=user,cookbook=latest_cookbook,is_read=True) else 0
    book_item = cook_book_item(latest_cookbook)
    channel_ctx = {"book_item":book_item, "current_time":current_time,"today_daily_tiles":today_daily_tiles,\
                   "latest_active":latest_active,"latest_cookbook":latest_cookbook,"is_read":is_read,"channel":"baby"}

    ctx = {}
    cid = request.GET.get('cid',1000)
    cat_obj = get_object_or_404(NewTileCategory, pk=cid)
    cat_list_pks = helpers.category_sub_and_par(cat_obj)
    tiles = tiles.filter(new_category_id__in=cat_list_pks)
    top = request.GET.get('top')
    if top:
        tiles = tiles.filter(microsecond__lte=top)
    else:
        try:
            top = tiles[0].microsecond
        except:
            top = ''
    
    ctx.update({"tiles": tiles, "content_type": content_type,"category":category,"effective_date":effective_date,"top":top,"cid":cid})
    ctx.update(channel_ctx)
    if request.is_ajax():
        page = int(request.GET.get("page",'1'))
        start = (page - 1) * 15
        end = page * 15
        tiles = tiles[start:end]
        ctx['tiles'] = tiles
        print tiles,'tiles---------------------------------'
        template_name = "kinger/revision/baby_index_container.html"
        return render(request, template_name, ctx)
    return render(request, template_name, ctx)

@login_required
def daily_record(request, template_name="kinger/revision/daily_record.html"):
    """日常记录详情页 """
    if not is_vip(request.user):  
        return render(request, "403.html")
    current_time = datetime.datetime.now() 
    tiles = Tile.objects.get_tiles_baby(request.user)
    category = NewTileCategory.objects.filter(is_tips=0, parent__pk=1130)
    group_date = get_group_date(request)
    page = int(request.GET.get("page", '1'))
    start = (page - 1) * 5
    end = page * 5 
    
    is_first = {"year":0,"month":0}
    record_list = []
    for day in group_date[start:end]:
        record_dict = {}
        record_dict['day'] = day[0]
        record_dict['is_first'] = False
        #判断当年当月的首条记录
        if is_first['year'] != day[0].year or is_first['month'] != day[0].month:
            record_dict['is_first'] = True
            is_first['year'] = day[0].year
            is_first['month'] = day[0].month 

        daily_record = get_daily_category_tiles(tiles, category, day[0])
        record_dict['data'] = daily_record
        record_list.append(record_dict)
    
    ctx = {"channel":"baby", "record_list":record_list,"group_date":group_date}
    return render(request, template_name, ctx)


def get_group_date(request):
    """获得日期分组数据"""
    now = datetime.datetime.now()
    sql_where = "start_time <= '" + str(now) + "' AND is_tips = 0 AND is_delete=0"
    user = request.user
    try:
        group = user.student.group
        if group:
            sql_where = sql_where + " AND (group_id = " + str(group.id) + " OR user_id = " + str(user.id) +")"
        else:
            sql_where = sql_where + " AND user_id = " + str(user.id)
    except ObjectDoesNotExist:
        sql_where = sql_where + " AND user_id = " + str(user.id)
    
    category = NewTileCategory.objects.filter(is_tips=0, parent__pk=1130).exclude(pk=9)
    category_id = [str(x.id) for x in category]
    if category_id:
        tag_id = "(" + ",".join(category_id) + ")"
        sql_where = sql_where + " AND new_category_id IN " + tag_id
    
    sql = "SELECT start_time AS days FROM`kinger_tile` WHERE " + sql_where + " GROUP BY TO_DAYS(start_time) ORDER BY start_time DESC"
    cursor = connection.cursor()
    cursor.execute(sql)
    return cursor.fetchall()


def get_daily_category_tiles(tiles, category, date):
    """返回当天的日常记录"""
    current_time = date
    today_tiles = Tile.objects.get_tiles_date(date=current_time, tiles=tiles)
    daily_category = category.filter(parent__pk=1130)
    daily_category_pks = [c.id for c in daily_category]
    today_tiles =  today_tiles.filter(new_category_id__in=daily_category_pks).order_by('-microsecond')
    daily_list = []
    for d in daily_category:
        daily_dict = {}
        daily_dict['id'] = d.id
        daily_dict['name'] = d.name
        daily_dict['tiles'] = []
        daily_dict['is_activitie'] = 0
        for t in today_tiles:
            if t.new_category_id == d.id:
                daily_dict['tiles'].append(t)
        if daily_dict['tiles']:
            daily_dict['num'] = len(daily_dict['tiles'])
            daily_dict['top'] = daily_dict['tiles'][0]  
        daily_list.append(daily_dict)
    return daily_list


@login_required
def daily_activity(request, active_id, template_name="kinger/daily_activity.html"):
    """日常活动详情页"""
    user = request.user
    if not is_vip(request.user):  
        return render(request, "403.html")
    
    if active_id == '0':
        active =None
    else:
        active = get_object_or_404(Activity, pk=active_id)
        is_empty = is_empty_active(active.description)
        if is_empty:
            return render(request, "404.html")
        
    q = get_q_user(user)
    actives = Activity.objects.filter(q)
    
    mentors = Mentor.objects.all()         
    # 禁止访问其它用户的记录
    if active:
        try:
            actives.get(pk=active_id)
        except ObjectDoesNotExist:
            return render(request, "403.html")
        
        add_daily_record_visitor(user,active)#添加访问记录
   
    today = active.start_time if active else datetime.datetime.now()
    effective_date = [str(x.start_time.date()) for x in actives]
    current_date = datetime.datetime.now().date()
    effective_date.append(str(current_date))
 
    try:
        active_list = actives.filter(microsecond__gt=active.microsecond) if active else actives
        next_day = active_list.filter(start_time__gte=today).order_by("start_time","microsecond")[0]
    except:
        next_day = None
    try:
        active_list = actives.filter(microsecond__lt=active.microsecond) if active else actives
        yesterday = active_list.filter(start_time__lte=today).order_by("-start_time","-microsecond")[0]
    except:
        yesterday = None
        
    today_active = get_daily_activitie_tiles(user)
    if not next_day and not today_active and active:
        next_day = {"id":0}
    
    today = today.date()    
    ctx = {}
    ctx.update({"tile": active, "effective_date":effective_date,"yesterday": yesterday,\
                "next_day": next_day,"mentors":mentors,"ty":"events","today":today,"current_date":current_date})
    return render(request, template_name, ctx)


def get_daily_by_date(request):
    
    date = request.GET.get('date','')
    ty = request.GET.get('ty','')
    user = request.user
    try:
        group = user.student.group
        q = Q(group=group) | Q(user=user)
    except:
        q = Q(user=user)
    actives = Activity.objects.filter(q)
    
    requested_redirect = request.GET.get('next','/')
    today = datetime.datetime.now().date()
    if not date:
        return redirect(requested_redirect)
    if ty == 'events':   
        actives = actives.filter(start_time__startswith=date)
        id = actives[0].id if actives else None
        if id:
            return redirect(reverse('kinger_daily_activity',kwargs={'active_id':id}))
        else:
            if date == str(today):
                return redirect(reverse('kinger_daily_activity',kwargs={'active_id':0}))
            else:
                return redirect(requested_redirect)
    else:
        try:
            group = user.student.group
        except:
            return render(request, "404.html")
        school = group.school
        q = Q(group=group) | Q(school=school)
        tommory = datetime.datetime.strptime(date,"%Y-%m-%d") + datetime.timedelta(days = 1)
        q_date = Q(date__startswith=tommory.date())
        cookbooks = Cookbook.objects.filter(q & q_date).order_by('-date')
        id = cookbooks[0].id if cookbooks else None
        if id:
            return redirect(reverse('kinger_daily_cookbook',kwargs={'cid':id}))
        else:
            if date == str(today):
                return redirect(reverse('kinger_daily_cookbook',kwargs={'cid':0}))
            else:
                return redirect(requested_redirect)
        

@login_required
def daily_cookbook(request, cid, template_name="kinger/daily_activity.html"):
    """明日食谱详情页"""
    tommorrow = datetime.datetime.now() + datetime.timedelta(days = 1)
    user = request.user
    if not is_vip(user):  
        return render(request, "403.html")
    if cid == '0':
        cookbook =None
        today = tommorrow.date()
    else:
        cookbook = get_object_or_404(Cookbook, pk=cid)
        today = cookbook.date
   
    today_book = cookbook
    try:
        group = user.student.group
    except:
        return render(request, "403.html")
    school = group.school
    mentors = Mentor.objects.all() 
    q = Q(group=group) | Q(school=school)       
    cookbooks = Cookbook.objects.filter(q).exclude(breakfast='',light_breakfast='',
                lunch='',light_lunch='',dinner='',light_dinner='').order_by('-date')
    #禁止访问其他用户数据
    if today_book:
        try:
            cookbooks.get(pk=cid)
        except ObjectDoesNotExist:
            return render(request, "403.html")
    
        helpers.mark_cookbook_as_read(request,today_book)#标记当前用户食谱数据为已读
        add_daily_record_visitor(user,today_book)#增加用户访问记录
        
    effective_date = [str(x.date + datetime.timedelta(days = -1) ) for x in cookbooks]
    current_date = datetime.datetime.now().date()
    effective_date.append(str(current_date))
    
    try:
        lastday_book =cookbooks.filter(date__lt=today)[0]
    except:
        lastday_book = None
        
    tommory = datetime.datetime.now() + datetime.timedelta(days = 1)
    tommory_date = tommory.date()
    try:
        nextday_book =cookbooks.filter(date__gt=today,date__lte=tommory_date).reverse()[0]
    except:
        nextday_book = None
        
    current_book = get_daily_cook_books(user,datetime.datetime.now())
    if not nextday_book and not current_book and today_book:
        nextday_book = {"id":0}
    
    book_item = cook_book_item(today_book)
    today = today + datetime.timedelta(days = -1)
    ctx = {}
    ctx.update({"effective_date":effective_date,"book_item":book_item,"cookbooks": cookbooks, "today_book": today_book,"tommorrow":tommorrow, \
                "yesterday": lastday_book, "next_day": nextday_book,"mentors":mentors, "ty":"cookbook","today":today,"current_date":current_date})
    return render(request, template_name, ctx)
    

def cook_book_item(book):
    """返回指定的食谱详系数据"""
    book_item = []
    if not book:
        return book_item
    book_type = CookbookType.objects.all()
    book_content = {"breakfast":book.breakfast,"light_breakfast":book.light_breakfast,"lunch":book.lunch, \
                    "light_lunch":book.light_lunch,"dinner":book.dinner,"light_dinner":book.light_dinner}
    
    try:
        if book.school_id:
            school = book.school
        else:
            school = book.group.school
    except:
        school = None
        
    for t in book_type:
        item = {}
        item['name'] = t.name
        item['school'] = school
        a = item['name']
        item['cname'] = t.cname
        item['img'] = t.img
        item['content'] = book_content[t.name]
        book_item.append(item)
    return book_item

def get_baby_tile_date(user):
    
    now = datetime.datetime.now()
    sql_where = "start_time <= '" + str(now) + "' AND is_tips = 0 AND is_delete=0"
#    user = request.user
    try:
        group = user.student.group
        if group:
            sql_where = sql_where + " AND (group_id = " + str(group.id) + " OR user_id = " + str(user.id) +")"
        else:
            sql_where = sql_where + " AND user_id = " + str(user.id)
    except ObjectDoesNotExist:
        sql_where = sql_where + " AND user_id = " + str(user.id)
    
    sql = "SELECT start_time AS days FROM`kinger_tile` WHERE " + sql_where + " GROUP BY TO_DAYS(start_time) ORDER BY start_time DESC"
    cursor = connection.cursor()
    cursor.execute(sql)
    return cursor.fetchall()

def get_active_date(user):
    
    now = datetime.datetime.now()
    sql_where = "start_time <= '" + str(now) + "' AND is_delete=0"
    try:
        group = user.student.group
        if group:
            sql_where = sql_where + " AND (group_id = " + str(group.id) + " OR user_id = " + str(user.id) +")"
        else:
            sql_where = sql_where + " AND user_id = " + str(user.id)
    except ObjectDoesNotExist:
        sql_where = sql_where + " AND user_id = " + str(user.id)
    
    sql = "SELECT start_time AS days FROM`kinger_activity` WHERE " + sql_where + " GROUP BY TO_DAYS(start_time) ORDER BY start_time DESC"
    cursor = connection.cursor()
    cursor.execute(sql)
    return cursor.fetchall()

def get_cookbook_date(user):
    
    now = datetime.datetime.now() + datetime.timedelta(days = 1)
    sql_where = "date <= '" + str(now.date()) + "'"
    try:
        group = user.student.group
        
        if not group:
            return []
        
        sql_where = sql_where + " AND (group_id = " + str(group.id) + " OR school_id = " + str(group.school.id) + \
            ") AND (breakfast != ''  OR light_breakfast != '' OR lunch != '' OR light_lunch != '' \
            OR dinner != '' OR light_dinner != '')"
            
#        if group:
#            sql_where = sql_where + " AND group_id = " + str(group.id) + \
#            " AND (breakfast != ''  OR light_breakfast != '' OR lunch != '' OR light_lunch != '' \
#            OR dinner != '' OR light_dinner != '')"
#        else:
#            school = group.school
#            sql_where = sql_where + " AND school_id = " + str(school.id) + \
#            " AND (breakfast != ''  OR light_breakfast != '' OR lunch != '' OR light_lunch != '' \
#            OR dinner != '' OR light_dinner != '')"
        
        sql = "SELECT date AS days FROM`kinger_cookbook` WHERE " + sql_where + " GROUP BY date ORDER BY date DESC"
        cursor = connection.cursor()
        cursor.execute(sql)
        return cursor.fetchall()
    except ObjectDoesNotExist:
        return []
    
def get_daily_activitie_tiles(user):
    """判断并返回当天是否有学习生活记录"""
    current_time = datetime.datetime.now()
    date = current_time.date()
    q = get_q_user(user)
    q = q & Q(start_time__startswith=date)       
    actives = Activity.objects.filter(q)
    if actives:
        last_active = actives[0]
    else:
        last_active = None
    return last_active


def get_daily_cook_books(user,now):
    """查询明日食谱，若没有则返回None"""
    tommorrow = now + datetime.timedelta(days = 1)
    date = tommorrow.date()
    try:
        group = user.student.group
        if group:
            tomorrow_recipes = Cookbook.objects.filter(group=group,date=date).exclude(breakfast='',light_breakfast='',
                lunch='',light_lunch='',dinner='',light_dinner='').order_by('-date')
            if not tomorrow_recipes:
                school = group.school
                tomorrow_recipes = Cookbook.objects.filter(school=school,date=date).exclude(breakfast='',light_breakfast='',
                lunch='',light_lunch='',dinner='',light_dinner='').order_by('-date')    
        else:
            tomorrow_recipes = None
    except ObjectDoesNotExist:
        tomorrow_recipes = None
    if tomorrow_recipes:
        last_book = tomorrow_recipes[0]
        return last_book
    else:
        return None

    
@login_required
def cal(request, template_name="kinger/revision/tile_board.html"):
    """
    | 以日历形式展示历史记录，按月显示.
    | 日历只展示 属于个人或者所在班级的记录, 即 *baby* 分类. 所以要清除 session

    :param month:
        当前月份.
    """
    try:
        request.session.pop('kinger_channel')
    except KeyError:
        pass
    cal = calendar
    cur_month_date = datetime.datetime.today()
    try:
        month = request.GET.get("month")
        if month:
            cur_month_date = datetime.datetime.strptime(month, "%Y-%m")
    except Exception, e:
        logger.error(e)

    prev_month = helpers.move_month(cur_month_date, "-")
    next_month = helpers.move_month(cur_month_date, "+")

    month_cal = cal.monthcalendar(cur_month_date.year, cur_month_date.month)

    category = NewTileCategory.objects.filter(is_tips=0)
    tiles = Tile.objects.get_tiles_baby(request.user).filter(new_category__in=category)
    tiles = tiles.exclude(new_category__parent_id=1130).exclude(new_category_id=9)
    tiles = tiles.filter(start_time__year=cur_month_date.year,start_time__month=cur_month_date.month)
        
    ctx = {"month_cal": month_cal, "cur_month_date": cur_month_date, "is_cal": True}
    ctx.update({"prev_month": prev_month, "next_month": next_month, 'tiles':tiles })
    return render(request, template_name, ctx)


@login_required
def view(request, tile_id, template_name="kinger/revision/tile_view.html"):
    """ 瓦片详情页， 会显示与该瓦片相关的今日记录, 根据分类过滤"""
    tile = get_object_or_404(Tile, pk=tile_id)
    user = request.user
    tile.view_count += 1
    tile.save()
    add_daily_record_visitor(user,tile)
    set_user_access(user)
    
    channel = request.session.get("kinger_channel")
    channel = request.GET.get("channel")
    type = request.GET.get("ty","")
    month = request.GET.get("month","")

    if channel == "tips":
        tiles = Tile.objects.get_tiles_edu(user)
        tiles = Tile.objects.filter(category__is_tips=True)

    elif channel == "all":
        tiles = Tile.objects.get_tiles_all_login(user)

    else:
        tiles = Tile.objects.get_tiles_baby(user)        
        # 禁止访问其它用户的记录
        if tile.creator != user:
            try:
                tiles.get(pk=tile_id)
            except ObjectDoesNotExist:
                if not tile.is_public:
                    return render(request, "403.html")

    today = tile.pub_time
    today_tiles = Tile.objects.get_tiles_date(date=today, tiles=tiles)
    daily_category = get_daily_category()
    if daily_category:
        today_tiles = today_tiles.exclude(category__parent=daily_category)
    today_tiles = today_tiles.order_by("-microsecond")
    
    try:
        next_day = Tile.objects.get_tiles_date_grater(date=today, tiles=tiles.filter(microsecond__gt=tile.microsecond)).exclude(id=tile.id).order_by("start_time","microsecond")
        next_day = next_day.exclude(category__parent=daily_category)[0] if daily_category else next_day[0]   
    except:
        next_day = None
    try:
        yesterday = Tile.objects.get_tiles_date_less(date=today, tiles=tiles.filter(microsecond__lt=tile.microsecond)).exclude(id=tile.id).order_by("-start_time","-microsecond")
        yesterday = yesterday.exclude(category__parent=daily_category)[0] if daily_category else yesterday[0]       
    except:
        yesterday = None
        
    if tile.n_comments > 0:
        comments = Comment.objects.for_model(tile).select_related('user')\
            .order_by("-submit_date").filter(is_public=True).filter(is_removed=False)
    else:
        comments = None
        
    ctx = {}
    # content_type = ContentType.objects.get_for_model(Tile)

    # 单击分页
    #tile_pk_list = [t.pk for t in today_tiles]
    #p = Paginator(today_tiles,15)

    # 有可能来自不同频道，而没有找到
    #try:
        #p_index = tile_pk_list.index(tile.pk)//15 + 1
    #except:
        #messages.error(request, '请转换到全部')
       # p_index = 1

    #today_tiles = p.page(p_index)
    emo_config = helpers.emo_config()

    ctx.update({"tile": tile, "cur_tile": tile, "today_tiles": today_tiles, "ty":type, "comments": comments, \
        "yesterday": yesterday, "next_day": next_day,"month": month,"channel": channel,"emo_config":emo_config})
    return render(request, template_name, ctx)


@login_required
#@require_POST
#@permission_required("comments.can_moderate")
def delete_comment(request, comment_id,template_name="kinger/revision/includes/comments_show.html"):
    """ 评论删除后，减少对应*瓦片*的评论数(冗余字段), 并跳转且作出提示 """
    comment = get_object_or_404(Comment, pk=comment_id, site__pk=settings.SITE_ID)
    if request.user == comment.user:
        perform_delete(request, comment)
        comment.content_object.after_del_comments()
#        messages.success(request, _("Comment deleted success"))
    else:
#        messages.error(request, _("You can't delete this comment"))
        pass
        
    tile = comment.content_object
    is_last_page = True
    if tile.n_comments > 0:
        comments = Comment.objects.for_model(tile).select_related('user')\
            .order_by("-submit_date").filter(is_public=True).filter(is_removed=False)
        if comments.count() > 5:
            is_last_page = False
    else:
        comments = None
    data = render(request, template_name,{"tile": tile,'comments':comments,"is_last_page":is_last_page})
    con=data.content
#    print con,'ccccccccccc'
    return ajax_ok('成功',con)

    # Flag the comment as deleted instead of actually deleting it.
#    return redirect(get_redir_url(request))


@receiver(comment_was_posted, sender=Comment)
def comment_messages(sender, comment, request, **kwargs):
    """ 添加评论后，增加对应*瓦片*的评论数(冗余字段), 并跳转且作出提示 """
    tile = comment.content_object
    cid = request.REQUEST.get('cid')
    try:
        comment.content_object.after_add_comments()
        tile = comment.content_object
        href = request.REQUEST.get('notify','')
        channel = get_channel(tile)
        if not href:
            href = reverse('axis_tile_view',kwargs={'tile_id': tile.id}) + "?channel=" + channel
    
        #添加一条提醒
        actions = {'title':'新消息','href':href + "#comment_div_" + str(comment.id)}
        
        if tile.creator != request.user:
            notify.send(request.user, verb='新消息', action_object=tile, recipient=tile.creator, actions=actions)
        if cid:
            comment_obj = get_object_or_404(Comment, pk=cid)
            relation = Comment_relation()
            relation.target_object = comment_obj
            relation.action_object = comment
            relation.save()
            if comment_obj.user != request.user:
                notify.send(request.user, verb='新消息', action_object=comment_obj, recipient=comment_obj.user, actions=actions)
    except:
        pass

    if request.user.is_authenticated():
        comment._set_url("http://www." + str(time.mktime(datetime.datetime.now().timetuple())) + ".com")
        comment.save()
        

import binascii
try:
    from sae_extra.apns import Apns
except:
    pass
def test(request):

    body = {'alert':'message','badge':1,'sound' : 'in.caf'}
    cert_id = 482
    device_token = '10b916771c9d0041e9abdb14051eaf745b82a6d4d79e030ebcefb7b89a4adbf8'
    apns = Apns()
    result = apns.push( cert_id , body , device_token );
    return HttpResponse(result)

def is_vip(user):
    """是否为vip用户"""
    try:
        d = isinstance(user.student,Student)
        if d:
            return True
        else:
            return False
    except Exception:
        return False

@login_required
def get_user_info(request):
    """ 鼠标移动到头像，显示用户详情信息 """
    uid = request.GET.get('uid')
    if not uid:
        return helpers.ajax_error('失败')
    uid = int(uid)
    try:
        user = User.objects.get(pk=uid)
    except Exception, e:
        return helpers.ajax_error('失败')
    
    try:       
        pro = user.get_profile()       
        about_me = pro.about_me
        user_name = pro.chinese_name_or_username()       
        image = pro.mugshot
        if not pro.can_view_profile(request.user): about_me = ''
    except Exception, e:      
        image = ''
        about_me = ''
        user_name = user.username

    url = media_path(image)    
    # 消息对话链接    
    talk_link = reverse('user_umessages_history',kwargs={'uid':user.id})
    show_talk = True if user.id != request.user.id else False
    info = {
        "about_me":about_me,
        "user_name":user_name,
        "avatar":url,
        "talk_link":talk_link,
        "show_talk":show_talk
    }
    return helpers.ajax_ok('成功',con=info)

@login_required
def vcar(request, template_name="kinger/includes/vcar.html"):
    """ 鼠标移动到头像，显示用户详情信息 """
    uid = request.GET.get('uid')
    if not uid:
        return helpers.ajax_error('失败')
    uid = int(uid)
    try:
        user = User.objects.get(pk=uid)
    except Exception, e:
        return helpers.ajax_error('失败')
    
    is_mentor = False
    try:       
        pro = user.get_profile()
        is_mentor = pro.is_mentor
        if is_mentor:
            about_me = user.mentor.description
            appellation = user.mentor.appellation
        else:
            appellation = ''
            about_me = pro.about_me
        user_name = pro.chinese_name_or_username()       
        image = pro.mugshot
        if not pro.can_view_profile(request.user): about_me = ''
    except Exception, e: 
        appellation = ''     
        image = ''
        about_me = ''
        user_name = user.username
    
    url = media_path(image, size="avatar")   
    url = url if url else STATIC_URL + CTX_CONFIG['DEFAULT_AVATAR']
    
    # 消息对话链接    
    talk_link = reverse('user_umessages_history',kwargs={'uid':user.id})
    show_talk = True if user.id != request.user.id else False
    info = {
        "uid":uid,    
        "about_me":about_me,
        "user_name":user_name,
        "avatar":url,
        "user":user,
        "is_mentor":is_mentor,
        "talk_link":talk_link,
        "show_talk":show_talk,
        "appellation":appellation
    }
    data = render(request, template_name, info)
    con=data.content
    return helpers.ajax_ok('成功',con)


def get_category_relation():
    """瓦片分类，父类所包含子类的列表"""
    cursor = connection.cursor()
    cursor.execute(
        "SELECT parent_id AS pid , GROUP_CONCAT(id) AS sid FROM `kinger_tile_category` WHERE parent_id != 0 GROUP BY parent_id "
        )
    desc = cursor.description
    rows = [dict(zip([col[0] for col in desc], row)) for row in cursor.fetchall()]
    return rows

def get_daily_category():
    """日常记录瓦片分类的父类"""
    try:
        daily_category = NewTileCategory.objects.get(pk=1130)
    except:
        daily_category = None
    return daily_category
    
def is_empty_active(desc):
    """判断日常活动内容是否为空"""
    daily = {'events':''}
    try:
        daily = json.loads(desc)
    except:
        pass
    if not daily['events']:
        return True 
    else:
        i = 0
        for d in daily['events']:
            if not d['content']:
               i += 1 
        if i == len(daily['events']):
            return True
    return False

def remove_empty_active(tiles):
    """移除日常活动为空的记录"""
    if tiles:
        empty_tile = []
        for t in tiles:
            if is_empty_active(t.description):
                empty_tile.append(t.id)
        if empty_tile:
            tiles = tiles.exclude(id__in=empty_tile)
    return tiles
         
def add_tile_visitor(user,tile):
    """增加瓦片访问者"""
    try:
        tile_visitor = TileVisitor()
        tile_visitor.visitor = user
        tile_visitor.tile = tile
        tile_visitor.save()
    except:
        pass

def set_user_access(user):
    try:
        pro = user.get_profile()
        pro.last_access = datetime.datetime.now()
        pro.save()
    except:
        pass
      
    
#from api.handlers.message import MessageHandler
def unread_list(request):
    user = request.user
    if request.user.is_authenticated():
        con = unread_count(request)
        return helpers.ajax_ok('成功',con)
    else:
        return helpers.ajax_error('失败','')

@login_required
def mark_cookbook_as_read(request):
    cid = request.POST.get('cookbook',0)
    try:
        cookbook = get_object_or_404(Cookbook, pk=cid)
    except:
        cookbook = None
    if cookbook:
        helpers.mark_cookbook_as_read(request,cookbook)
    return HttpResponse('')
        

def introduction(request, template_name="kinger/introduction.html"):
    """成长介绍"""
    return render(request, template_name)
 
def get_q_user(user):
    """返回用户及用户所在班级的查询"""
    try:
       group = user.student.group
       q = Q(group=group) | Q(user=user)
    except:
        q = Q(user=user)
    return q

def show_comment(request, id='', template_name="kinger/revision/includes/comments_show.html"):
    tile = Tile.objects.get(id=id)
    is_last_page = True
    if tile.n_comments > 0:
        comments = Comment.objects.for_model(tile).select_related('user')\
            .order_by("-submit_date").filter(is_public=True).filter(is_removed=False)
        if comments.count() > 5:
            is_last_page = False 
    else:
        comments = None
    return render(request, template_name,{"tile": tile,'comments':comments,"is_last_page":is_last_page})

def school_active(site,cty):
    """学园活动，幼儿作品"""
    albums = Album.objects.filter(site=site,category_id=cty)
    photos = Photo.objects.filter(album__in=albums,is_show=True)
    return photos

def get_parts(site,cty):
    """精彩文章，新闻动态，公告通知"""
    parts = Part.objects.filter(site=site,category_id=cty,is_show=True).exclude(type=0).order_by("-type","-ctime")
    return parts

def get_tip(site):
    parts = Part.objects.filter(site=site,category_id=11).order_by("-ctime")
    if parts.count():
        return parts[0]
    else:
        return None
    
def get_start(school,ty):
    if ty == 'teacher':
        starts = Teacher.objects.filter(school=school,user__figure__is_show=True)
    else:
        starts = Student.objects.filter(school=school,user__figure__is_show=True)
    return starts

def index_for_site(request,site):
    ctx = {'channel':'site_index'}
    if request.user.is_authenticated():
        ctx.update({'user_login':request.user})
    school = site.school
    auth_form = AuthenticationForm
    if request.method == 'POST':
        form = auth_form(request.POST)
        
        if request.is_ajax():
            return helpers.ajax_validate_error(form)
        
        if form.is_valid():
            identification, password, remember_me = (form.cleaned_data['identification'],
                                                     form.cleaned_data['password'],
                                                     form.cleaned_data['remember_me'])
            user = authenticate(identification=identification,password=password)
            try:
                profile = user.get_profile()
            except:
                p = Profile()
                p.user = user
                p.save()
            if user.is_active:
                login(request, user)

                if remember_me:
                    request.session.set_expiry(userena_settings.USERENA_REMEMBER_ME_DAYS[1] * 86400)
                else: request.session.set_expiry(0)
                messages.success(request, _('You have been signed in.'))
                # Whereto now?
                return redirect(request.get_full_path())
            else:
                return redirect(reverse('userena_disabled',
                                        kwargs={'username': user.username}))
    else:
        form = AuthenticationForm()
        
    school_actives = school_active(site,17)
    student_actives = school_active(site,18)
    articals = get_parts(site,19)
    news = get_parts(site,10)
    print news,'nnnnnnnnnnnnnn'
    announces = get_parts(site,9)
    tip = get_tip(site)
    start_teachers = get_start(site.school,'teacher')
    start_students = get_start(site.school,'student')
    tiles = Tile.objects.get_tiles_all_unlogin()[0:4]
    links = Link.objects.filter(site=site)
    parent_domain = helpers.get_parent_domain(request)
    ctx.update({'form':form,'school_actives':school_actives,'student_actives':student_actives,\
                'articals':articals,'news':news,'announces':announces,'tip':tip,'links':links,\
                'start_teachers':start_teachers,'start_students':start_students,'tiles':tiles,\
                'site':site,'parent_domain':parent_domain})
    return ctx

def index_for_weixiao(request):
    user = request.user
    category = NewTileCategory.objects.all()
#    content_type = ContentType.objects.get_for_model(Tile)
    
    if request.user.is_authenticated():
        #用户登录日志
        log = Access_log()
        log.type = 2
        log.user = user
        log.url = request.get_full_path()
        log.save()
                                                                           
        category = category.filter(is_tips=1) 
#            category_pks = [c.id for c in category]
        
        tiles = Tile.objects.get_tiles_edu(user)
    else:
        tiles = Tile.objects.get_tiles_all_unlogin()
    ctx = {}
    
    cid = request.GET.get('cid',2000)
    ty = request.GET.get('ty','')
    if ty == "pic":
        q = Q(new_type_id__in=[1,4])
    elif ty == "video":
        q = Q(new_type_id=2)
    else:
        q = Q()
    try:
        show_type = True if int(cid) in [2120,2121,2122,2200,2210,2220,2230,2240] else False
    except:
        show_type = False
    cat_obj = get_object_or_404(NewTileCategory, pk=cid)
    cat_list_pks = helpers.category_sub_and_par(cat_obj)
    tiles = tiles.filter(new_category_id__in=cat_list_pks).filter(q)
    top = request.GET.get('top')
    if top:
        tiles = tiles.filter(microsecond__lte=top)
    else:
        try:
            top = tiles[0].microsecond
        except:
            top = ''
#    recommend_tiles = tiles.order_by("-n_comments")[0:10]
    recommend_tiles = [rt.tile for rt in TileRecommend.objects.all()[0:10]]
    month_themes = get_month_theme()
    local_url = reverse('kinger_edu_index')
    ctx.update({"tiles": tiles,"category":category,"channel":"edu",'month_themes':month_themes,'top':top,\
                "recommend_tiles":recommend_tiles,"cid":cid,"show_type":show_type,"ty":ty,"local_url":local_url})
    
    print "the end --------------------------------------------"
    if request.is_ajax():
        page = int(request.GET.get("page",'1'))
        start = (page - 1) * 15
        end = page * 15
        tiles = tiles[start:end]
        ctx['tiles'] = tiles
    return ctx

def check_user_cookbook_by_date(user,date):
    try:
        group = user.student.group
        school = group.school
    except:
        return False
    
    q = Q(group=group) | Q(school=school)
    q_date = Q(date=date)
    cookbooks = Cookbook.objects.filter(q & q_date).order_by('group','-date')
    result = False
    if cookbooks.count():
        book = cookbooks[0]
        result = ckeck_cookbook_validate(book,school)
    return result

def ckeck_cookbook_validate(book,school):
    try:
        book_set = CookbookSet.objects.get(school=school)
    except:
        return False
    if book_set.breakfast and book.breakfast: return True
    if book_set.light_breakfast and book.light_breakfast: return True
    if book_set.lunch and book.lunch: return True
    if book_set.light_lunch and book.light_lunch: return True
    if book_set.dinner and book.dinner: return True
    if book_set.light_dinner and book.light_dinner: return True
    return False

def get_day_micro_begin2end(date):
    if date:
        date = datetime.datetime.strptime(date,"%Y-%m-%d")
    else:
        date = datetime.datetime.now()
    time_start = time.mktime(date.timetuple())
    end_date = datetime.datetime(date.year, date.month, date.day,23,59,59)
    time_end = time.mktime(end_date.timetuple())
    return (time_start,time_end)

@login_required
def axis_effective_date(request):
    date_tiles = [dt[0].date() for dt in get_baby_tile_date(request.user)]
    date_act = [da[0].date() for da in get_active_date(request.user)]
    cookbook_date = get_cookbook_date(request.user)
    user = request.user
    if cookbook_date:
        date_coo = [dc[0] + datetime.timedelta(days=-1) for dc in cookbook_date if check_user_cookbook_by_date(user,dc[0])]
        dates = date_tiles + date_act + date_coo
    else:
        dates = date_tiles + date_act
        
    dates = sorted(list(set(dates)),reverse=True)
    effective_date = [str(x) for x in dates]
    current_date = datetime.datetime.now().date()
    effective_date.append(str(current_date))
    data = {'status':True,'effective_date':effective_date}
    return HttpResponse(json.dumps(data))
