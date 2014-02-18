# -*- coding: utf-8 -*-
from django.shortcuts import render_to_response, redirect, render, get_object_or_404
from django.http import Http404
from django.http import HttpResponse
from kinger.models import School,WorkGroup,Teacher,Department,PostJob,Position,Communicate,Group,GroupGrade
from oa.forms import ClassForm,WorkGroupForm
from oa.helpers import set_class_teacher,set_guide_teacher,get_schools,get_school_with_workgroup
from django.contrib import messages
from django.core.urlresolvers import reverse
from django.contrib.auth.models import User
from kinger.helpers import ajax_error,ajax_ok
from oa.decorators import Has_permission
from django.db.models import Q
try:
    import simplejson as json
except ImportError:
    import json

@Has_permission('manage_global_group')
def index(request,template_name="oa/workgroup_list.html"):
    school = get_schools(request.user)[0]
    workgroups = school.workgroup_set.all()
    workgroups = workgroups.filter(type=0)
    ctx = {'workgroups':workgroups,'ty':False}
    return render(request, template_name, ctx)

@Has_permission('manage_personal_group')
def personal(request,template_name="oa/workgroup_list.html"):
    school = get_schools(request.user)[0]
    workgroups = school.workgroup_set.all()
    workgroups = workgroups.filter(type=1)
    workgroups = workgroups.filter(user=request.user)
    ctx = {'workgroups':workgroups,'ty':True}
    return render(request, template_name, ctx)

@Has_permission('manage_global_group')
def create(request,template_name="oa/workgroup_form.html"):
    ctx = {}
    school = get_schools(request.user)[0]
    teachers = Teacher.objects.filter(school=school)
    
    if request.method == 'POST':
        form = WorkGroupForm(request.POST)
        if form.is_valid():
            workgroup = form.save(commit=False)
            workgroup.school = school
            workgroup.type = 0
            workgroup.save()
            
            member_pks = request.POST.getlist('to')
            members = [t for t in User.objects.filter(pk__in=member_pks)]
            workgroup.members = members
            messages.success(request, u'已成功创建 %s ' % workgroup.name)
            return redirect('oa_workgroup_list')
    else:
        form = WorkGroupForm()
    
    schools = get_school_with_workgroup(request.user)
    ctx.update({'form':form,'teachers':teachers,'ty':0,'schools':schools})
    return render(request, template_name, ctx)

@Has_permission('manage_personal_group')
def personal_create(request,template_name="oa/workgroup_form.html"):
    ctx = {}
    school = get_schools(request.user)[0]
    teachers = Teacher.objects.filter(school=school)
    
    if request.method == 'POST':
        form = WorkGroupForm(request.POST)
        if form.is_valid():
            workgroup = form.save(commit=False)
            workgroup.school = school
            workgroup.type = 1
            workgroup.user = request.user
            workgroup.save()
            
            member_pks = request.POST.getlist('to')
            members = [t for t in User.objects.filter(pk__in=member_pks)]
            workgroup.members = members
            messages.success(request, u'已成功创建 %s ' % workgroup.name)
            return redirect('oa_workgroup_personal')
    else:
        form = WorkGroupForm()
    
    schools = get_school_with_workgroup(request.user)
    ctx.update({'form':form,'teachers':teachers,'ty':1,'schools':schools})
    return render(request, template_name, ctx)

@Has_permission('manage_global_group')
def update(request, workgroup_id, template_name="oa/workgroup_form.html"):
    ctx = {}
    school = get_schools(request.user)[0]
    teachers = Teacher.objects.filter(school=school)
    workgroup = get_object_or_404(WorkGroup,pk=workgroup_id)
    ty = workgroup.type
    member_pks = [m.id for m in workgroup.members.all()]
    
    if request.method == 'POST':
        form = WorkGroupForm(request.POST,instance=workgroup)
        if form.is_valid():
            workgroup = form.save(commit=False)
            workgroup.save()
            
            member_pks = request.POST.getlist('to')
            print member_pks,'mmmmmmmmmmmmm'
            members = [t for t in User.objects.filter(pk__in=member_pks)]
            workgroup.members = members
            messages.success(request, u'已成功更新 %s ' % workgroup.name)
            return redirect('oa_workgroup_list')
    else:
        form = WorkGroupForm(instance=workgroup)
        
    schools = get_school_with_workgroup(request.user)
    ctx.update({'form':form,'teachers':teachers,'member_pks':member_pks,'workgroup':workgroup,'ty':0,'schools':schools})
    return render(request, template_name, ctx)

@Has_permission('manage_personal_group')
def personal_update(request, workgroup_id, template_name="oa/workgroup_form.html"):
    ctx = {}
    school = get_schools(request.user)[0]
    teachers = Teacher.objects.filter(school=school)
    workgroup = get_object_or_404(WorkGroup,pk=workgroup_id)
    member_pks = [m.id for m in workgroup.members.all()]
    
    if request.method == 'POST':
        form = WorkGroupForm(request.POST,instance=workgroup)
        if form.is_valid():
            workgroup = form.save(commit=False)
            workgroup.save()
            
            member_pks = request.POST.getlist('to')
            members = [t for t in User.objects.filter(pk__in=member_pks)]
            workgroup.members = members
            messages.success(request, u'已成功更新 %s ' % workgroup.name)
            return redirect('oa_workgroup_personal')
    else:
        form = WorkGroupForm(instance=workgroup)
    
    schools = get_school_with_workgroup(request.user)
    ctx.update({'form':form,'teachers':teachers,'member_pks':member_pks,'workgroup':workgroup,'ty':1,'schools':schools})
    return render(request, template_name, ctx)

@Has_permission('manage_global_group')
def delete(request):
    if request.method == 'POST':
        workgroup_pks = request.POST.getlist('workgroups')
        workgroups = WorkGroup.objects.filter(pk__in=workgroup_pks)
        workgroups.delete()
        messages.success(request, u'删除成功')
    return redirect("oa_workgroup_list")

@Has_permission('manage_personal_group')
def personal_delete(request):
    if request.method == 'POST':
        workgroup_pks = request.POST.getlist('workgroups')
        workgroups = WorkGroup.objects.filter(pk__in=workgroup_pks)
        workgroups.delete()
        messages.success(request, u'删除成功')
    return redirect("oa_workgroup_personal")

def set_workgroup(request, template_name="oa/workgroup_set.html"):
    """ 设置组成员 """
    wid = int(request.POST.get('workgroup_id',0))
    
    ty = int(request.POST.get('ty',0))
    data = request.POST.get('data','')
    user_pks = [int(u) for u in data.split(",") if u]
    
    schools = get_school_with_workgroup(request.user)
    member_pks = []
    if wid and wid !=0:
        workgroup = get_object_or_404(WorkGroup, pk=wid)
        member_pks = [u.id for u in workgroup.members.all()]
    
    user_pks = user_pks + member_pks
    
    member_list = [u for u in User.objects.filter(pk__in=user_pks)]
    
    school_id = request.POST.get('s','')
    if school_id:
        school = get_object_or_404(School, pk=school_id)
    else:
        school = get_schools(request.user)[0]
    
    if school.parent_id == 0:
        q = Q(school__in=schools)
    else:
        q = Q(school=school)
    teachers = Teacher.objects.filter(q)
    group_lists = Group.objects.filter(q)
    group_list = []
    group_grades = GroupGrade.objects.all()
    for grade in group_grades:
        t_list = []
        grade_groups = group_lists.filter(grade=grade)
        for g in grade_groups:
            #老师按照班级分组
            group_teachers = [s.user for s in Teacher.objects.filter(group=g)]
            if group_teachers:
                t_list.append({'id':g.id,'name':g.name,'members':group_teachers})
        if t_list:
            group_list.append({'id':grade.id,'name':grade.name,'groups':t_list})
    
    depatrment_list = []
    departments = Department.objects.filter(q)
    for d in departments:
        members = [p.teacher.user for p in PostJob.objects.filter(department=d)]
        if members:
            depatrment_list.append({'id':d.id,'name':d.name,'members':members})
    
    positions = Position.objects.filter(q)
    position_list = []
    for p in positions:
        members = [po.teacher.user for po in PostJob.objects.filter(position=p)]
        if members:
            position_list.append({'id':p.id,'name':p.name,'members':members})
    
    word_list = []
    words = [chr(i) for i in range(65,91)]
    for w in words:
        members = [t.user for t in teachers.filter(pinyin__istartswith=w)]
        if members:
            word_list.append({'id':w,'name':w,'members':members})
        
    
    data = render(request, template_name,{'member_list':member_list,'teachers':teachers,'depatrment_list':depatrment_list,\
                                          'position_list':position_list,'word_list':word_list,'school':school,\
                                          'group_list':group_list,'schools':schools,'user_pks':user_pks})
    con=data.content
    return ajax_ok('成功',con)

@Has_permission('manage_communicate')
def communicate(request, template_name="oa/communicate_form.html"):
    ctx = {}
    school = get_schools(request.user)[0]
    schools = get_schools(request.user)[1:]
    school_pk_list = [l.school_id for l in Communicate.objects.filter(parent=school)]
 
    if request.method == 'POST':
        school_pks = request.POST.getlist('schools')
        school_list = [sch for sch in School.objects.filter(pk__in=school_pks)]
        Communicate.objects.filter(parent=school).delete()
        for s in school_list:
            c = Communicate()
            c.school = s
            c.parent = school
            c.save()
            messages.success(request, u'保存成功')
#        ctx.update({'schools':schools,'school_pk_list':school_pk_list,'success':True})
        return redirect('oa_communicate')
    ctx.update({'schools':schools,'school_pk_list':school_pk_list})
    return render(request, template_name, ctx)
