# -*- coding: utf-8 -*-
from django.shortcuts import render_to_response, redirect, render, get_object_or_404
from django.http import Http404
from django.http import HttpResponse
from kinger.models import Agency,School,Role,Access,DocumentReceiver,StarFigure,School,Teacher,Role
from oa.forms import AgencyForm
from django.contrib import messages
from django.contrib.auth.models import User
from userena.contrib.umessages.models import Message, MessageRecipient, MessageContact
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth.decorators import login_required, permission_required
from kinger.helpers import ajax_ok,ajax_error
from oa.helpers import unread_count

@login_required
def index(request,template_name="oa/index.html"):  
    """oa首页"""
    try:
        messages = MessageRecipient.objects.filter(user=request.user,\
                    deleted_at__isnull=True,message__is_send=True).order_by('-id','read_at')
        documents = DocumentReceiver.objects.filter(is_send=True,user=request.user).order_by('is_read','-ctime')
    except:
        messages = None
        documents = None
    ctx = {'message_list':messages,'documents':documents}
    return render(request, template_name, ctx)

def view(request):  
    return HttpResponse("这是集团详情页面")

def delete(request):  
    return HttpResponse("删除集团")

def create(request,template_name="oa/agency_create.html"):

    if request.method == 'POST':
        form = AgencyForm(request.POST)
        if form.is_valid():
            agency = form.save(commit=False)
            agency.creator = request.user
            agency.save()
            if agency.id:
                obj, created = School.objects.get_or_create(name=agency.name,\
                    type=100,creator=agency.creator,description=agency.description,agency=agency)
                messages.success(request, u'已成功创建集团 %s ' % agency.name)
                return redirect("oa_agency_create")
    else:
        form = AgencyForm()
    ctx = {'form':form}
    return render(request, template_name, ctx)

@staff_member_required
def create_agency_user(request):
    """生成集团用户及集团"""
    school = School()
    school.creator_id = 1
    school.parent_id = 0
    school.save()
   
    prefix = 'u'
    latest = User.objects.latest('id')
    username = "%s%d" % (prefix, latest.id + 1)
    if User.objects.filter(username = username).count():
        username += '_'+str(random.randint(1,999))
    password = 123456
    user = User.objects.create_user(username, '', password)
    data = {'username':username,'password':password}
    teacher = Teacher()
    teacher.user_id = user.id
    teacher.creator_id = 1
    teacher.school_id = school.id
    teacher.save()
    
    role,created = Role.objects.get_or_create(school_id=0,name='集团管理员')
#    role = Role()
#    role.school_id = school.id
#    role.name = "集团管理员"
#    role.save()
    access_list = [a for a in Access.objects.all()]
    role.accesses = access_list
    
    roles = Role.objects.filter(pk=role.id)
    user.roles = roles
    
    return HttpResponse('username:' + str(username) + ',' + 'password:' + str(password))

def unread_list(request):
    user = request.user
    if request.user.is_authenticated():
        con = unread_count(request)
        return ajax_ok('成功',con)
    else:
        return ajax_error('失败','')
