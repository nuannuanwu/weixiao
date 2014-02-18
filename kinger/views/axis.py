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
Cookbook,CookbookType,Access_log,Comment_relation,Activity,TileVisitor,DailyRecordVisitor,CookbookRead,Tile,TinymceImage
from django.db.models import Q
from django.contrib.contenttypes.models import ContentType
import calendar,datetime,time
from django.http import Http404,HttpResponse
from kinger import helpers
from django.contrib.auth.models import User
from django.core.cache import cache
from kinger.settings import STATIC_URL,CTX_CONFIG
from django.core.paginator import Paginator
from django.core.urlresolvers import reverse
from kinger.forms import MobileForm, PwdResetForm, PwdMobileForm,TileBabyForm
from kinger.profiles.models import Profile
from notifications import notify
from django.contrib.auth import views as auth_views
from django.contrib.sites.models import get_current_site
from django.db import connection
from django.http import Http404
from django.contrib.auth import REDIRECT_FIELD_NAME
from django.contrib.sites.models import Site
from kinger.views.revision import get_baby_tile_date,get_active_date,get_cookbook_date,get_q_user,get_daily_category_tiles,\
        get_daily_cook_books,add_tile_visitor,set_user_access,get_daily_category,is_vip,get_group_date,\
        get_daily_activitie_tiles,cook_book_item,is_empty_active,check_user_cookbook_by_date
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

@login_required
def time_axis(request, template_name="kinger/tile_axis.html"):
    return render(request, template_name)

@login_required
def get_daily_baby_tiles(request,template_name = "kinger/revision/baby_axis_extra_container.html"):
    date = request.POST.get('date')
    page = int(request.POST.get('num',1))
    is_all = False
    category = NewTileCategory.objects.all()
    category = category.filter(is_tips=0)   
    category = NewTileCategory.objects.filter(is_tips=0)     
    today_tiles = Tile.objects.get_tiles_baby(request.user).filter(new_category__in=category,start_time__startswith=date)\
        .exclude(new_category__parent_id=1130).exclude(new_category_id=9).order_by("-microsecond") 
    
    start = (page - 1) * 20 + 8
    end = page * 20 + 8
    tiles = today_tiles[start:end]
    if end >= today_tiles.count():
        is_all = True
    data = render(request, template_name,{'tiles':tiles,'page':page+1,'is_all':is_all,'tile_date':date})
    con=data.content
    
    return ajax_ok('成功',con)

@login_required
def tile_view_pre(request, tile_id, template_name="kinger/revision/axis_tile_view_pre.html"):
    user = request.user
    data = json.dumps({'status':"error"})
    ty = request.GET.get('ty')
    cid = request.GET.get('cid')
    if ty == 'theme' and tile_id == '0':
        if cid != '0':
            tiles = Tile.objects.filter(new_category_id=cid)[:1]
        else:
            tiles = Tile.objects.filter(new_category_id__gt=2400,new_category_id__lte=2412)[:1]
        if tiles.count():
            tile = tiles[0]
        else:
            return HttpResponse(data)
    else:
        try:
            tile = Tile.objects.get(pk=tile_id)
        except:
            return HttpResponse(data)
    
    is_last_page = True
    if tile.n_comments > 0:
        comments = Comment.objects.for_model(tile).select_related('user')\
            .order_by("-submit_date").filter(is_public=True).filter(is_removed=False)
        if comments.count() > 5:
            comments = comments[0:5]
            is_last_page = False 
    else:
        comments = None
        
    ctx = {}
    ctx.update({"tile": tile,"comments": comments,"is_last_page":is_last_page})
    data = render(request, template_name,ctx)
    con=data.content
    return ajax_ok('成功',con)
    
@login_required
def tile_view(request, tile_id, template_name="kinger/revision/axis_tile_view.html"):
    """ 瓦片详情页， 会显示与该瓦片相关的今日记录, 根据分类过滤"""
    user = request.user
    if not user.is_authenticated():
        data = json.dumps({'status':"error"})
        return HttpResponse(data)
    tile = get_object_or_404(Tile, pk=tile_id)
    tile.view_count += 1
    tile.save()
    helpers.add_daily_record_visitor(user,tile)
    set_user_access(user)
    
    channel = request.GET.get("channel")
    type = request.GET.get("ty","")
    month = request.GET.get("month","")
    tpage = int(request.GET.get("tpage",1))

    if channel == "edu":
        tiles = Tile.objects.get_tiles_edu(user)
    elif channel == "life":
        tiles = Tile.objects.get_tiles_life(user)
    else:
        tiles = Tile.objects.get_tiles_baby(user).exclude(new_category_id=9)      
        # 禁止访问其它用户的记录
        if tile.creator != user:
            try:
                tiles.get(pk=tile_id)
            except ObjectDoesNotExist:
                if not tile.is_public:
                    return render(request, "403.html")
    
    tiles = tiles.exclude(new_category_id__in=range(1130,1138)).order_by("-microsecond")
    recommends = Tile.objects.get_tiles_edu(user).order_by("-microsecond")[0:100]
    recommend_tiles = [recommends[i] for i in random.sample(range(100),4)]
    today = tile.start_time
    today_tiles = Tile.objects.get_tiles_date(date=today, tiles=tiles)
    daily_category = get_daily_category()
    if daily_category:
        today_tiles = today_tiles.exclude(new_category__parent=daily_category)
    today_tiles = today_tiles.order_by("-microsecond")
    
    try:
        next_day = Tile.objects.get_tiles_date_grater(date=today, tiles=tiles.filter(microsecond__gt=tile.microsecond)).exclude(id=tile.id).order_by("microsecond")
        next_day = next_day.exclude(new_category__parent=daily_category)[0] if daily_category else next_day[0]   
    except:
        next_day = None
    try:
        yesterday = Tile.objects.get_tiles_date_less(date=today, tiles=tiles.filter(microsecond__lt=tile.microsecond)).exclude(id=tile.id).order_by("-microsecond")
        yesterday = yesterday.exclude(new_category__parent=daily_category)[0] if daily_category else yesterday[0]       
    except:
        yesterday = None
     
    is_last_page = True 
    if tile.n_comments > 0:
        comments = Comment.objects.for_model(tile).select_related('user')\
            .order_by("-submit_date").filter(is_public=True).filter(is_removed=False)
        if comments.count() > 5:
            comments = comments[0:5]
            is_last_page = False 
    else:
        comments = None
        
    ctx = {}

    emo_config = helpers.emo_config()
    tile_all = [t for t in tiles]
    try:
        tile_order = tile_all.index(tile)
    except:
        tile_order = 0
    print tile_order,'ttttttttttttttttttt'
#    if tpage == (tile_order / 10) + 1:
#        order = (tile_order + 1) % 10
#    else:
    order = (tile_order) % 10
    print order,'oooooooooooooooooooooooooo'
    if tpage == 1:
        tpage = (tile_order / 10) + 1
    start = (tpage - 1) * 10
    end = tpage * 10
    is_last_tpage = True if end >= len(tile_all) else False
    tiles = tile_all[start:end]
    
    is_ajax = True if request.method == 'POST' else False
    ctx.update({"tile": tile, "cur_tile": tile, "today_tiles": today_tiles, "ty":type, "comments": comments,\
        "yesterday": yesterday, "next_day": next_day,"month": month,"channel": channel,"tpage":tpage,\
         "tiles": tiles,"emo_config":emo_config,"order":order,'is_last_tpage':is_last_tpage,\
         "is_last_page":is_last_page,"recommend_tiles":recommend_tiles,'is_ajax':is_ajax})

    if is_ajax:
        data = render(request, template_name,ctx)
        con=data.content
        return ajax_ok('成功',con)
    else:
        template_name = "kinger/revision/tile_view.html"
        return render(request, template_name,ctx)

@login_required
def theme_view(request,template_name="kinger/revision/axis_theme_view.html"):
    """ 主题详情页"""
    tile_id = request.GET.get('tid')
    ty = request.GET.get('ty')
    if ty == 'theme':
        themes = Tile.objects.filter(new_category_id__gt=2400,new_category_id__lte=2412)[:1]
        tile_id = themes[0].id if themes.count() else 0
    cid = request.GET.get('cid')
    if tile_id:
        tile = get_object_or_404(Tile, pk=tile_id)
    else:
        try:
            tiles_all = Tile.objects.filter(new_category__id__startswith='24').exclude(new_category__id=2400)
            if cid:
                tiles_all = tiles_all.filter(new_category__id=cid)
            tile = tiles_all[0]
        except:
            data = {'status':False,'msg':"暂无主题内容"}
            return HttpResponse(json.dumps(data))
    user = request.user
    tile.view_count += 1
    tile.save()
    helpers.add_daily_record_visitor(user,tile)
    set_user_access(user)
    
    channel = request.GET.get("channel")
    type = request.GET.get("ty","")
    month = request.GET.get("month","")
    tpage = int(request.GET.get("tpage",1))
    
    tiles = Tile.objects.filter(new_category_id__gt=2400,new_category_id__lte=2412)
    month_tiles = tiles.filter(new_category=tile.new_category)[0:3]
    month_tiles_pks = [m.id for m in month_tiles]
    year_tiles = tiles.order_by('-n_comments')[0:4]
    

    today = tile.start_time
    today_tiles = Tile.objects.get_tiles_date(date=today, tiles=tiles).order_by("-microsecond")
    
    try:
        next_day = Tile.objects.get_tiles_date_grater(date=today, tiles=tiles.filter(microsecond__gt=tile.microsecond,id__in=month_tiles_pks)).exclude(id=tile.id).order_by("microsecond")
        next_day = next_day[0]   
    except:
        next_day = None
    try:
        yesterday = Tile.objects.get_tiles_date_less(date=today, tiles=tiles.filter(microsecond__lt=tile.microsecond,id__in=month_tiles_pks)).exclude(id=tile.id).order_by("-microsecond")
        yesterday = yesterday[0]       
    except:
        yesterday = None
    
    is_last_page = True 
    if tile.n_comments > 0:
        comments = Comment.objects.for_model(tile).select_related('user')\
            .order_by("-submit_date").filter(is_public=True).filter(is_removed=False)
        if comments.count() > 5:
            comments = comments[0:5]
            is_last_page = False 
    else:
        comments = None
        
    ctx = {}
    emo_config = helpers.emo_config()
    tile_all = [t for t in tiles]
    tile_order = tile_all.index(tile)
#    if tpage == (tile_order / 10) + 1:
#        order = (tile_order + 1) % 10
#    else:
#        order = None
    if tpage == 1:
        tpage = (tile_order / 10) + 1
    start = (tpage - 1) * 10
    end = tpage * 10
    is_last_tpage = True if end >= len(tile_all) else False
    tiles = tile_all[start:end]
    
    is_ajax = True if request.method == 'POST' else False
    ctx.update({"tile": tile, "cur_tile": tile, "today_tiles": today_tiles, "ty":type, "comments": comments,"year_tiles":year_tiles,\
        "yesterday": yesterday, "next_day": next_day,"month": month,"channel": channel,"tpage":tpage,'month_tiles':month_tiles,\
         "tiles": tiles,"emo_config":emo_config,'is_last_tpage':is_last_tpage,"is_last_page":is_last_page,'is_ajax':is_ajax})
    if is_ajax:
        data = render(request, template_name,ctx)
        con=data.content
        return ajax_ok('成功',con)
    else:
        template_name = "kinger/revision/axis_theme_view_page.html"
        return render(request, template_name,ctx)
    

def tile_page(request, tile_id, template_name="kinger/revision/axis_tile_page.html"):
    """ 瓦片详情页,底部分页"""
    tile = get_object_or_404(Tile, pk=tile_id)
    user = request.user
    channel = request.GET.get("channel")
    tpage = int(request.GET.get("tpage",1))
    is_ajax = request.GET.get("is_ajax",False)
    is_ajax = True if is_ajax == "True" else False

    if channel == "edu":
        tiles = Tile.objects.get_tiles_edu(user)
    elif channel == "life":
        tiles = Tile.objects.get_tiles_life(user)
    else:
        tiles = Tile.objects.get_tiles_baby(user).exclude(new_category_id=9)      
        # 禁止访问其它用户的记录
        if tile.creator != user:
            try:
                tiles.get(pk=tile_id)
            except ObjectDoesNotExist:
                if not tile.is_public:
                    return render(request, "403.html")
    
    tiles = tiles.exclude(new_category__parent_id=1130).order_by("-microsecond")
    ctx = {}
    tile_all = [t for t in tiles]
    tile_order = tile_all.index(tile)
#    if tpage == (tile_order / 10) + 1:
#        order = (tile_order + 1) % 10
#    else:
#        order = None
    order = (tile_order) % 10
#    if tpage == 1:
#        tpage = (tile_order / 10) + 1
    start = (tpage - 1) * 10
    end = tpage * 10
    is_last_tpage = True if end >= len(tile_all) else False
    tiles = tile_all[start:end]
    print tpage,'tttttttttttttttt'
    
    ctx.update({"tpage":tpage,"tiles": tiles,"order":order,"tile":tile,"is_last_tpage":is_last_tpage,"channel":channel,"is_ajax":is_ajax})
    data = render(request, template_name,ctx)
    con=data.content
    return ajax_ok('成功',con)

def more_comment(request, tile_id,template_name="kinger/revision/includes/comments_show.html"):
    """ 加载更多评论 """
    tile = get_object_or_404(Tile, pk=tile_id)
    cpage = int(request.GET.get("cpage",1))
    
    is_last_page = True 
    if tile.n_comments > 0:
        comments = Comment.objects.for_model(tile).select_related('user')\
            .order_by("-submit_date").filter(is_public=True).filter(is_removed=False)
    else:
        comments = None

    start = (cpage - 1) * 10 + 5
#    start = 0
    end = cpage * 10 + 5
    
    if end < comments.count():
        is_last_page = False 

    comments = comments[start:end]
    data = render(request, template_name,{"tile": tile,'comments':comments,"cpage":cpage,"is_last_page":is_last_page})
    con=data.content
    return ajax_ok('成功',con)

@login_required
def daily_record(request, template_name="kinger/revision/axis_daily_record.html"):
    """日常记录详情页 """
    if not is_vip(request.user):  
        return render(request, "403.html")
    date = request.POST.get('date')
    type = int(request.POST.get('ty','0'))
    tiles = Tile.objects.get_tiles_baby(request.user)
    category = NewTileCategory.objects.filter(is_tips=0, parent__pk=1130)
    date = datetime.datetime.strptime(date,"%Y-%m-%d")
    dates = get_group_date(request)
    group_date = [d for d in dates if d[0].date() <= date.date()]
    
    content_type = ContentType.objects.get_for_model(Tile)
    new_visitor = DailyRecordVisitor()
    new_visitor.visitor = request.user
    new_visitor.target_content_type = content_type
    new_visitor.save() 
    
    effective_date = [str(x[0].date()) for x in dates]
    current_date = datetime.datetime.now().date()
    effective_date.append(str(current_date))
    
    page = int(request.POST.get("page", '1'))
    start = (page - 1) * 5
    end = page * 5 
    is_last_page = False 
    if end >= len(group_date):
        is_last_page = True 
    
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
        if daily_record:
            record_dict['data'] = daily_record
            record_list.append(record_dict)

    ctx = {"channel":"baby", "record_list":record_list,"group_date":group_date,\
           'effective_date':effective_date,'type':type,'page':page,'date':date,'is_last_page':is_last_page}
    data = render(request, template_name,ctx)
    con=data.content
    return ajax_ok('成功',con)

@login_required
def daily_activity(request, template_name="kinger/revision/axis_daily_activity.html"):
    """日常活动详情页"""
    date = request.POST.get('date','')
    id = request.POST.get('id',0)
    user = request.user
    if not is_vip(request.user):  
        return render(request, "403.html")
    
    try:
        group = user.student.group
        q = Q(group=group) | Q(user=user)
    except:
        q = Q(user=user)
    actives = Activity.objects.filter(q)
    
    if id:
        active_id = id
    else:
        date_active = actives.filter(start_time__startswith=date)
        active_id = date_active[0].id if date_active else 0
        
    if active_id == 0:
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
        
        helpers.add_daily_record_visitor(user,active)#添加访问记录
    
    current_date = datetime.datetime.strptime(date,"%Y-%m-%d") if date else datetime.datetime.now()
    today = active.start_time if active else current_date
    effective_date = [str(x.start_time.date()) for x in actives]
    
    effective_date.append(str(current_date))
 
    try:
        active_list = actives.filter(microsecond__gt=active.microsecond).exclude(id=active.id) if active else actives
        next_day = active_list.filter(start_time__gte=today).order_by("microsecond")[0]
    except:
        next_day = None
    try:
        active_list = actives.filter(microsecond__lt=active.microsecond).exclude(id=active.id) if active else actives
        yesterday = active_list.filter(start_time__lte=today).order_by("-microsecond")[0]
    except:
        yesterday = None
        
    today_active = get_daily_activitie_tiles(user)
    if not next_day and not today_active and active:
        next_day = {"id":0}
    
    today = today.date()    
    ctx = {}
    ctx.update({"tile": active, "effective_date":effective_date,"yesterday": yesterday,\
                "next_day": next_day,"mentors":mentors,"ty":"events","today":today,"current_date":current_date})
    data = render(request, template_name,ctx)
    con=data.content
    return ajax_ok('成功',con)

@login_required
def daily_cookbook(request, template_name="kinger/revision/axis_cookbook.html"):
    """明日食谱详情页"""
    
    date = request.POST.get('date','')
    id = request.POST.get('id',0)
    
    user = request.user
    if not is_vip(user):  
        return render(request, "403.html")
    try:
        group = user.student.group
    except:
        return render(request, "404.html")
    school = group.school
    q = Q(group=group) | Q(school=school)
    
    if not id:
        tommory = datetime.datetime.strptime(date,"%Y-%m-%d") + datetime.timedelta(days = 1)
        q_date = Q(date__startswith=tommory.date())
        cookbooks = Cookbook.objects.filter(q & q_date).order_by('group','-date')
        id = cookbooks[0].id if cookbooks else None
    
    tommorrow = datetime.datetime.now() + datetime.timedelta(days = 1)
    
    current_day = (datetime.datetime.strptime(date,"%Y-%m-%d") + datetime.timedelta(days = 1)).date() if date else tommorrow.date()
    if not id:
        cookbook =None
        today = current_day
    else:
        cookbook = get_object_or_404(Cookbook, pk=id)
        today = cookbook.date
    today_book = cookbook

    mentors = Mentor.objects.all() 
    q = Q(group=group) | Q(school=school)       
    cookbooks = Cookbook.objects.filter(q).exclude(breakfast='',light_breakfast='',
                lunch='',light_lunch='',dinner='',light_dinner='').order_by('-date')
    #禁止访问其他用户数据
    if today_book:
        try:
            cookbooks.get(pk=id)
        except ObjectDoesNotExist:
            return render(request, "403.html")
    
        helpers.mark_cookbook_as_read(request,today_book)#标记当前用户食谱数据为已读
        helpers.add_daily_record_visitor(user,today_book)#增加用户访问记录
        
    effective_date = [str(x.date + datetime.timedelta(days = -1) ) for x in cookbooks if check_user_cookbook_by_date(user,x.date)]
    current_date = current_day
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
    
    book_item = cook_book_item(today_book)
    book_item_pre = cook_book_item(lastday_book)
    book_item_next = cook_book_item(nextday_book)
    
    if not nextday_book and not current_book and today_book:
        nextday_book = {"id":0}

    today = today + datetime.timedelta(days = -1)
    ctx = {}
    ctx.update({"effective_date":effective_date,"book_item":book_item,"cookbooks": cookbooks,\
                 "today_book": today_book,"tommorrow":tommorrow, "yesterday": lastday_book,\
                  "next_day": nextday_book,"mentors":mentors, "ty":"cookbook","today":today,\
                  "current_date":current_date,'book_item_pre':book_item_pre,'book_item_next':book_item_next})
    data = render(request, template_name,ctx)
    con=data.content
    return ajax_ok('成功',con)

@login_required
def create_baby_tile(request, template_name="kinger/revision/create_baby_tile.html"):
    print request.FILES
    form = TileBabyForm(request.POST,request.FILES)
    print form.errors,'errors------------------------------'
    if form.is_valid():
        ty = request.POST.get("ty",'')
        desc = request.POST.get("description",'')
        try:
            description = urllib.unquote(desc)
        except:
            description = desc
        tile = form.save(commit=False)
        tile.creator = request.user
        tile.user = request.user
        tile.new_category_id = 1200
        tile.is_tips = 0
        print ty,'ty--------------------------------------'
        if ty == "flash":
#            pid = request.POST.get("tile_pid")
            file_path = request.POST.get("file_path")
            extension = request.POST.get("extension")
            file_id = request.POST.get("fid")
            print file_path,extension,'ppppppppppppppppppppppppppppppppppp'
            tile.save()
            date = str(datetime.datetime.strftime(datetime.datetime.now(),"%Y%m%d"))
            salt, hash = generate_sha1(tile.id)
            file_name = 'tile/' + date + '/' + hash[:22] + '.' + extension
#            tile_img = TinymceImage.objects.get(id=pid)
            tile.img = file_name
            print tile.id,'yyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyy'
            try:
                URL('http://' + SITE_INFO.domain + reverse('cron_make_large_img')).post_async(filename=file_name,file_path=file_path,tileid=tile.id)
            except Exception, e:
                print e,'eeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeee'
                try:
                    fr = open(file_path,"rb")
                    content = fr.read()
                    fr.close()
                    if os.path.isfile(file_path):
                        os.remove(file_path)
                    AliyunStorage(). _put_file(file_name, content)
                except:
                    pass
                
            try:
                temp = TemporaryFiles.objects.get(fileid=file_id)
                os.remove(temp.path)
                temp.delete()
            except:
                pass
        else:
            tile.description = urllib.unquote(str(tile.description))
        tile.save()
        if ty == "word_type":
            messages.success(request, _("发布成功"))
            return redirect('kinger_rev_time_axis')
        data = json.dumps({'status':1,'desc':"ok"})
        return HttpResponse(data)
    
    data = json.dumps({'status':0,'desc':"error"})
    return HttpResponse(data)
#    else:
#        form = TileBabyForm()
#    ctx = {"form":form}
#    
#    data = render(request, template_name,ctx)
#    con=data.content
#    return ajax_ok('成功',con)
##    return render(request, template_name,ctx)

@login_required
def delete_tile(request, tile_id):
    try:
        tile = get_object_or_404(Tile, pk=tile_id)
        tile.delete()
        messages.success(request, _("删除成功"))
    except:
        messages.error(request, _("删除失败"))
    return redirect('kinger_rev_time_axis')
    
def get_tile_n_comments(request):
    tid = request.POST.get("tid")
    try:
        tile = Tile.objects.get(id=tid)
        comments = Comment.objects.for_model(tile).select_related('user').filter(is_public=True).filter(is_removed=False)
        data = json.dumps({'num':comments.count()})
        return HttpResponse(data)
    except:
        data = json.dumps({'num':0})
        return HttpResponse(data)
    
def edit_tile_description(request):
    tid = request.POST.get("tid")
    desc = request.POST.get("desc","")
    try:
        tile = Tile.objects.get(id=tid)
        tile.description = desc
        tile.save()
        data = json.dumps({'status':True,'desc':desc})
        return HttpResponse(data)
    except:
        data = json.dumps({'status':False,'desc':desc})
        return HttpResponse(data)
    
    
