# -*- coding: utf-8 -*-
from django.shortcuts import render_to_response, redirect, render, get_object_or_404
from django.db.models import Q
from django.contrib.auth.models import User
from django.http import Http404
from django.http import HttpResponse
from kinger.models import Role,Access,Teacher
from oa.forms import RoleForm
from django.contrib import messages
from django.core.urlresolvers import reverse
from django.utils.translation import ugettext as _
from kinger.helpers import ajax_error,ajax_ok
from oa.decorators import Has_permission
from oa import helpers
try:
    import simplejson as json
except ImportError:
    import json

@Has_permission('manage_role')
def index(request,template_name="oa/role_list.html"):
    """角色列表"""
    schools = helpers.get_schools(request.user)
    q = request.GET.get("q", "")
    s = int(request.GET.get("s", 0))
    roles = Role.objects.filter(school__in=schools)
    if s:
        roles = roles.filter(school_id=s)
    if q:
        roles = roles.filter(name__contains=q)
    ctx = {'roles':roles,'query':q,'schools':schools,'s':s}
    return render(request, template_name, ctx)

@Has_permission('manage_role')
def create_role(request,template_name="oa/role_form.html"):
    """创建角色"""
    school = helpers.get_schools(request.user)[0]
    ctx = {}
    agency_par_accesses = Access.objects.filter(parent__pk=0,level=0).exclude(pk=5)
    agency_sub_accesses = Access.objects.filter(level=0).exclude(parent__pk=0).exclude(parent__pk=5)

    if request.method == 'POST':
        form = RoleForm(request.POST)
        if form.is_valid():
            access_pks = request.POST.getlist('user')
            role = form.save(commit=False)
            role.school = school
            role.save()
            
            access_list = [a for a in Access.objects.filter(pk__in=access_pks)]
            if access_list:
                role.accesses = access_list

            messages.success(request, u"角色 %s 已成功创建" % role.name)
            return redirect("oa_permission_role_list")
    else:
        form = RoleForm()
        
    ctx.update({'agency_par_accesses':agency_par_accesses,'agency_sub_accesses':agency_sub_accesses,'form':form})
    return render(request, template_name, ctx)

@Has_permission('manage_role')
def update_role(request,role_id,template_name="oa/role_form.html"):
    """更新角色"""
    ctx = {}
    schools = helpers.get_schools(request.user)
    role = get_object_or_404(Role, id=role_id,school__in=schools)
    agency_pks = [r.id for r in role.accesses.filter(level=0)]
    school_pks = [r.id for r in role.accesses.filter(level=1)]
    agency_par_accesses = Access.objects.filter(parent__pk=0,level=0).exclude(pk=5)
    school_par_accesses = Access.objects.filter(parent__pk=0,level=1)
    agency_sub_accesses = Access.objects.filter(level=0).exclude(parent__pk=0).exclude(parent__pk=5)
    school_sub_accesses = Access.objects.filter(level=1).exclude(parent__pk=0)

    if request.method == 'POST':
        form = RoleForm(request.POST,instance=role)
        if form.is_valid():
            access_pks = request.POST.getlist('user')
            form.save()
            
            access_list = [a for a in Access.objects.filter(pk__in=access_pks)]
            if access_list:
                role.accesses = access_list
                
            messages.success(request, u"角色 %s 已成功创建" % role.name)
            return redirect("oa_permission_role_list")
    else:
        form = RoleForm(instance=role)
        
    ctx.update({'agency_par_accesses':agency_par_accesses,'school_par_accesses':school_par_accesses,\
                'agency_sub_accesses':agency_sub_accesses,'school_sub_accesses':school_sub_accesses,\
                'form':form,'agency_pks':agency_pks,'school_pks':school_pks,'role':role})
    return render(request, template_name, ctx)

@Has_permission('manage_role')
def delete_role(request):
    """删除角色"""
    schools = helpers.get_schools(request.user)
    if request.method == 'POST':
        role_pks = request.POST.getlist('roles')
        roles = Role.objects.filter(pk__in=role_pks,school__in=schools,type=0)
        roles.delete()
    return redirect("oa_permission_role_list")

@Has_permission('manage_role')
def add_role(request,user_id):
    """指派用户角色"""
    user = get_object_or_404(User, id=user_id)
    if request.method == 'POST':
        role_pks = request.POST.getlist('role_list')
        roles = Role.objects.filter(pk__in=role_pks)
        user.roles = roles
        messages.success(request, u"指派角色成功")
#        try:
#            schools = helpers.get_schools(request.user)
#            helpers.set_schools_admin(schools,user,roles)
#        except:
#            pass
        
    return redirect("oa_permission_designate_role")

def get_role_accesses(request):
    """获取角色的权限列表"""
    role_id = request.POST.get('role_id',0)
    if not role_id:
        return HttpResponse()

    access_list = []
    role = get_object_or_404(Role, id=role_id)
    agency_list = [{'id':r.id,'name':r.name} for r in role.accesses.filter(level=0)]
    school_list = [{'id':r.id,'name':r.name} for r in role.accesses.filter(level=1)]
    access_list.append({'agency_list':agency_list,'school_list':school_list})
    return HttpResponse(json.dumps(access_list))

@Has_permission('manage_role_set')
def designate_role(request,template_name="oa/designate_role.html"):
    """指派角色列表"""
    s = int(request.GET.get("s", 0))
    t = int(request.GET.get("t", -1))
    n = request.GET.get("n", "")
    m = request.GET.get("m", "")
    
    qs = Q(school_id=s) if s else Q()
    qt = Q(postjob__status=t) if t == 0 or t == 1 else Q()
    qn = Q(name__contains=n) if n else Q()
    qm = Q(user__username__contains=m) if m else Q()
    q = qs & qt & qn & qm

    schools = helpers.get_schools(request.user)
    school = schools[0]
    roles = Role.objects.filter(school=school)
    teachers = Teacher.objects.filter(school__in=schools).filter(q)
    states = ((0, _('在职')),(1, _('离职')),)

    ctx = {'roles':roles}
    ctx.update({"teachers": teachers,"schools":schools,"s":s,"t":t,"n":n,"states":states,'m':m})
    return render(request, template_name, ctx)

def role_detail(request, template_name="oa/role_detail.html"):
    """ 角色详情 """
    rid = request.POST.get('role_id')
    if not rid:
        return ajax_error('失败')
    rid = int(rid)
    try:
        role = Role.objects.get(pk=rid)
    except Exception, e:
        return helpers.ajax_error('失败')
    
    ctx = {}
    agency_roles = role.accesses.filter(level=0)
    agency_par = Access.objects.filter(parent__pk=0,level=0)
    agency_par_list = []
    for p in agency_par:
        agency_sub = agency_roles.filter(parent=p)
        if agency_sub.count():
            agency_par_list.append({'parent':p.name,'sub_roles':agency_sub})   
    
    data = render(request, template_name,{'agency':agency_par_list,'role':role})
    con=data.content
    return ajax_ok('成功',con)

def user_role(request, template_name="oa/user_role.html"):
    """ 分配用户角色 """

    uid = request.POST.get('user_id')
    if not uid:
        return ajax_error('失败')
    uid = int(uid)
    try:
        user = User.objects.get(pk=uid)
    except Exception, e:
        return ajax_error('失败')
    
    user_roles = [r for r in user.roles.all()]
    user_role_pks = ','.join([str(r.id) for r in user_roles])
    
    schools = helpers.get_schools(request.user)
    q = request.POST.get("q", "")
    s = int(request.POST.get("s", 0))
    roles = Role.objects.filter(school__in=schools)
    if s:
        roles = roles.filter(school_id=s)
    if q:
        roles = roles.filter(name__contains=q)
        
    ctx = {'roles':roles,'query':q,'schools':schools,'s':s,\
           'user':user,'user_roles':user_roles,'user_role_pks':user_role_pks}
    
    data = render(request,template_name,ctx)
    con=data.content
    return ajax_ok('成功',con)

@Has_permission('manage_authorize')
def set_authorize(request, template_name="oa/teacher_set_authorize.html"):
    """ 全员家长群发控制 """
    
    s = int(request.GET.get("s", 0))
    t = int(request.GET.get("t", -1))
    n = request.GET.get("n", "")
    
    
    qs = Q(school_id=s) if s else Q()
    qt = Q(is_authorize=t) if t == 0 or t == 1 else Q()
    qn = Q(name__contains=n) if n else Q()
    
    q = qs & qt & qn
    
    schools = helpers.get_schools(request.user)
    teachers = Teacher.objects.filter(school__in=schools).filter(q)
    states = ((0, _('未授权')),(1, _('已授权')),)
    ctx = {"teachers": teachers,"schools":schools,"s":s,"t":t,"n":n,"states":states}
    return render(request, template_name,ctx)

@Has_permission('manage_authorize')
def change_authorize(request):
    """更改用户全员家长群发控制授权状态"""
    tid = int(request.POST.get('tid'))
    t = Teacher.objects.get(id=tid)
    s = t.is_authorize
    if s == 0:
        t.is_authorize = 1
        t.save()
    if s == 1:
        t.is_authorize = 0
        t.save()
    data = json.dumps({'status':t.is_authorize})
    return HttpResponse(data)