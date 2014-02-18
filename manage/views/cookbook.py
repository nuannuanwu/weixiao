# -*- coding: utf-8 -*-
from django.shortcuts import redirect, render
from kinger.models import Group, School, Teacher,Cookbook, CookbookSet
from django.contrib import messages

from manage.decorators import school_admin_required
import calendar
import datetime
from kinger import helpers
import copy
from django.core.urlresolvers import reverse

@school_admin_required
def index(request, template_name="cookbook/index.html"):
    """
    食谱首页
    """
    # 初始化数据
    user = request.user
    schools = user.manageSchools.all()

    if schools.count() > 0:
        school = schools[0]
    else:
        messages.error(request,'你没有可管理的学校')
        return redirect('manage')

    groups = school.group_set.all()
    cur_date = datetime.date.today()

    cookbook_type = 'school' # 食谱类型，默认是学校的


    # 取得参数
    date_param = request.GET.get('date')
    school_param = request.GET.get('school')
    group_param = request.GET.get('group')


    # 日期初始化，空日期代表当前月份
    if date_param:
        try:
            the_date = datetime.datetime.strptime(date_param, "%Y-%m")
        except ValueError:
            the_date = cur_date
    else:
        the_date = cur_date

    #  只有学校为空，班级不为空，才是班级类型，其它都是学校
    if not school_param and group_param:
        cookbook_type = 'group'


    days = calendar.monthrange(the_date.year,the_date.month)[1]

    #当前日期
    cur_month_date = cur_date.strftime("%Y-%m")

    #上下日期
    prev_month = helpers.move_month(the_date, "-")
    next_month = helpers.move_month(the_date, "+")

    school_cookbook = Cookbook.objects.filter(school=school,date__year=the_date.year,date__month=the_date.month)

    month_cal = calendar.monthcalendar(the_date.year, the_date.month)

    items = Cookbook.objects.get_items()
    cookbook_set = CookbookSet.objects.get_set(school=school)

    cookbook_data = {       
        'cur_month_date':cur_month_date,
        'prev_month':prev_month,
        'next_month':next_month,
        'month_cal':month_cal,
        'type':'school',
        'date':{
            'year':the_date.year,
            'month':the_date.month
        },
        'group':{
            'id':0,
            'name':''
        },
        'groups':groups,
        'set':cookbook_set,
        'cookbook':[]      
    }    

    cur_day_con_demo = {
        'day':1,
        'is_pub':False,
        'con':{
            'breakfast':{
                'con':'',
                'comefrom':'school'
            },
            'light_breakfast':{
                'con':'',
                'comefrom':'school'
            },
            'lunch':{
                'con':'',
                'comefrom':'school'
            },
            'light_lunch':{
                'con':'',
                'comefrom':'school'
            },
            'dinner':{
                'con':'',
                'comefrom':'school'
            },
            'light_dinner':{
                'con':'',
                'comefrom':'school'
            },
        },
        'items':[]
    }

    if cookbook_type == 'school':
        cookbook_data['type'] = 'school'

        # 取得学校食谱
        for d in range(1,days+1):
            cur_day_con = copy.deepcopy(cur_day_con_demo)
            cur_day_con['day'] = d

            school_cookbook_day = None

            for s in school_cookbook:
                if s.date.day == d:
                    school_cookbook_day = s
                    break                                    
            
            school_pub = True if school_cookbook_day else False

            # 发布过,默认为，从未发布过
            if school_pub:
                cur_day_con['is_pub'] = True               

                for item in items: 
                    school_con = getattr(school_cookbook_day, item) if school_pub else ''              

                    cur_day_con['con'][item]['con'] = school_con
                    cur_day_con['con'][item]['comefrom'] = 'school' 

                    # 加入显示项
                    if cur_day_con['con'][item]['con'] !='' and cookbook_set[item]['is_show']:
                        cur_day_con['items'].append(cookbook_set[item]['name'])

            cookbook_data['cookbook'].append(cur_day_con)

    elif cookbook_type == 'group':
        cookbook_data['type'] = 'group'

        group_pk = int(group_param)
        group = Group.objects.get(pk=group_pk)
        group_cookbook = Cookbook.objects.filter(group=group,date__year=the_date.year,date__month=the_date.month)

        cookbook_data['group']['id'] = group.pk
        cookbook_data['group']['name'] = group.name

        for d in range(1,days+1):
            cur_day_con = copy.deepcopy(cur_day_con_demo)
            cur_day_con['day'] = d

            school_cookbook_day = None
            group_cookbook_day = None

            for s in school_cookbook:
                if s.date.day == d:
                    school_cookbook_day = s
                    break

            for g in group_cookbook:
                if g.date.day == d:
                    group_cookbook_day = g
                    break

            school_pub = True if school_cookbook_day else False
            group_pub = True if group_cookbook_day else False

            

            # 发布过,默认为，从未发布过
            if school_pub or group_pub:
                
                cur_day_con['is_pub'] = True               

                for item in items:                 

                    group_con = getattr(group_cookbook_day, item) if group_pub else ''
                    school_con = getattr(school_cookbook_day, item) if school_pub else ''               

                    # 读取班级
                    if group_con != '':
                        cur_day_con['con'][item]['con'] = group_con
                        cur_day_con['con'][item]['comefrom'] = 'group'

                    # 读取学校
                    else:
                        cur_day_con['con'][item]['con'] = school_con
                        cur_day_con['con'][item]['comefrom'] = 'school' 

                    # 加入显示项
                    if cur_day_con['con'][item]['con'] !='' and cookbook_set[item]['is_show']:
                        cur_day_con['items'].append(cookbook_set[item]['name'])

            cookbook_data['cookbook'].append(cur_day_con)

    ctx = cookbook_data

    return render(request, template_name, ctx)

@school_admin_required
def save_cookbook_set(request,):
    """
    用于保存学校的食谱设置
    """
    # 取得参数
    try:            
        user = request.user
        schools = user.manageSchools.all()

        if schools.count() > 0:
            school = schools[0]
        else:
            messages.error(request,'你没有可管理的学校')
            return redirect('manage')

        breakfast = True if request.POST.get('breakfast') else False
        light_breakfast = True if request.POST.get('light_breakfast') else False
        lunch = True if request.POST.get('lunch') else False
        light_lunch = True if request.POST.get('light_lunch') else False
        dinner = True if request.POST.get('dinner') else False
        light_dinner = True if request.POST.get('light_dinner') else False
     
        school_set = CookbookSet.objects.filter(school=school)

        if school_set.count() > 0:
            school_set = school_set[0]
            school_set.breakfast = breakfast
            school_set.light_breakfast = light_breakfast
            school_set.lunch = lunch
            school_set.light_lunch = light_lunch
            school_set.dinner = dinner
            school_set.light_dinner = light_dinner
            
        else:
            school_set = CookbookSet(school=school,breakfast=breakfast,light_breakfast=light_breakfast,lunch=lunch,light_lunch=light_lunch,dinner=dinner,light_dinner=light_dinner)

        school_set.save()
        messages.success(request,'设置成功')
    except:
        messages.success(request,'设置失败')       
    
    return redirect(request.META['HTTP_REFERER'])

@school_admin_required
def save_cookbook(request,):
    """
    保存某天，班或学校食谱
    """
    # 取得参数
    # 初始化数据
    user = request.user
    schools = user.manageSchools.all()

    if schools.count() > 0:
        school = schools[0]
    else:
        messages.error(request,'你没有可管理的学校')
        return redirect('manage')

    cookbook_type = 'school' # 食谱类型，默认是学校的

    items = Cookbook.objects.get_items()
    come_items = {}
    show_list = {}

    # 取得参数
    date_param = request.POST.get('date')
    school_param = request.POST.get('school')
    group_param = request.POST.get('group')    
    action_type = request.POST.get('ty')
    
    the_date = datetime.datetime.strptime(date_param, "%Y-%m-%d")    

    #  只有学校为空，班级不为空，才是班级类型，其它都是学校
    if not school_param and group_param:
        cookbook_type = 'group'


    is_empty = 0
    for i in items:
        come_items[i] = request.POST.get(i)
        is_empty = is_empty + 1 if come_items[i] else is_empty
    if not is_empty and action_type != 'clear':
        return helpers.ajax_error('请添加食谱内容',type='')

    # print dinner
    school_cookbook = Cookbook.objects.filter(school=school,date=the_date)
   
    if cookbook_type == 'school':       
        
        if school_cookbook.count() > 0:  
            school_cookbook = school_cookbook[0]

            for i in items:
                setattr(school_cookbook,i,come_items[i])

            school_cookbook.save()
        else:
            school_cookbook = Cookbook(creator=user,school=school,date=the_date,breakfast=come_items['breakfast'],light_breakfast=come_items['light_breakfast'], lunch=come_items['lunch'], light_lunch=come_items['light_lunch'], dinner=come_items['dinner'], light_dinner=come_items['light_dinner'])  
            school_cookbook.save()

        for i in items:            
            school_item = getattr(school_cookbook, i)

            show_list[i] = True if school_item != '' else False            

    elif cookbook_type == 'group':
        group_pk = int(group_param)

        group_cookbook = Cookbook.objects.filter(group=group_pk,date=the_date)
        
        school_pub = True if school_cookbook.count() > 0 else False
        group_pub = True if group_cookbook.count() > 0 else False

        # 保存继承，若来自学校内容，则保存为空(代表继承)
        if school_pub:
            school_cookbook_items = school_cookbook[0]
            for i in items:
                if getattr(school_cookbook_items, i) == come_items[i]:
                    come_items[i] = ''

        # 需要继承保存判断
        if group_pub:
            group_cookbook = group_cookbook[0]
            for i in items:
                setattr(group_cookbook,i,come_items[i])
            group_cookbook.save()

        else:
            group = Group.objects.get(pk=group_pk)
            group_cookbook = Cookbook(creator=user,group=group,date=the_date,breakfast=come_items['breakfast'],light_breakfast=come_items['light_breakfast'], lunch=come_items['lunch'], light_lunch=come_items['light_lunch'], dinner=come_items['dinner'], light_dinner=come_items['light_dinner'])
            group_cookbook.save()

        # 返回 是否为空选项，用于前端显示

        for i in items:
            group_item = getattr(group_cookbook, i)
            school_item = getattr(school_cookbook[0], i) if school_pub else ''

            if group_item != '':
                show_list[i] = True
            elif school_item !='':
                show_list[i] = True
            else:
                show_list[i] = False

    cookbook_set_items = CookbookSet.objects.get_set(school=school)

    for i in items:
        if not cookbook_set_items[i]['is_show']:
            del show_list[i]

    return helpers.ajax_ok('成功',con=show_list)

@school_admin_required
def get_cookbook_date(request,):
    """
    获得某天食谱
    """
    try:
        #初始化数据

        user = request.user
        schools = user.manageSchools.all()

        if schools.count() > 0:
            school = schools[0]
        else:
            messages.error(request,'你没有可管理的学校')
            return redirect('manage')

        cur_date = datetime.date.today()
        cookbook_day = None

        cookbook_type = 'school' # 食谱类型，默认是学校的

        # 取得参数
        date_param = request.GET.get('date')
        school_param = request.GET.get('school')
        group_param = request.GET.get('group')


        # 日期初始化，空日期代表当前月份
        if date_param:
            try:
                the_date = datetime.datetime.strptime(date_param, "%Y-%m-%d")
            except ValueError:
                the_date = cur_date
        else:
            the_date = cur_date

        #  只有学校为空，班级不为空，才是班级类型，其它都是学校
        if not school_param and group_param:
            cookbook_type = 'group'


        if cookbook_type == 'school':
            cookbook_day = Cookbook.objects.get_cookbook_date(school=school,date=the_date)
        else:
            group_param = int(group_param)
            group = Group.objects.get(pk=group_param)
            cookbook_day = Cookbook.objects.get_cookbook_date(school=school,group=group,date=the_date)
        return helpers.ajax_ok('成功',con=cookbook_day)
    except:
        return helpers.ajax_error('失败')


        