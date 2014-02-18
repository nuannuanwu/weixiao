# -*- coding: utf-8 -*-
from django.shortcuts import render_to_response, redirect, render, get_object_or_404
from django.http import Http404
from django.http import HttpResponse
from kinger.models import Agency,School,Department
from oa.forms import AgencyForm,DepartmentForm
from django.contrib import messages
from django.core.urlresolvers import reverse
from oa.decorators import Has_permission,agency_admin_required
from oa import helpers

@Has_permission('manage_department')
def index(request,template_name="oa/department_list.html"):
    """部门列表"""
    schools = helpers.get_schools(request.user)
    school_id = request.GET.get("sid",'')
    if school_id:
        school = get_object_or_404(School, pk=school_id)
        departments = school.departments.all()
    else:
        school = None
        departments = Department.objects.filter(school__in=schools)
    ctx = {'schools':schools,'school':school,'departments':departments,'sid':school_id}
    return render(request, template_name, ctx)

def view(request):  
    return HttpResponse("这是集团详情页面")

@Has_permission('manage_department')
def delete(request,department_id):
    """删除部门"""
    school_id = request.GET.get("sid",'')
    schools = helpers.get_schools(request.user)
    department = get_object_or_404(Department,pk=department_id,school__in=schools)
    department.delete()
    messages.success(request, u'部门 %s 已删除' % department.name)
    redirect_url = reverse('oa_department_list') + "?sid=" + str(school_id)
    return redirect(redirect_url)

@Has_permission('manage_department')
def create(request,template_name="oa/department_form.html"):
    """创建部门"""
    ctx = {}
    school_id = request.GET.get("sid",0)
    
    if request.method == 'POST':
        school_id = int(request.POST.get("school",0))
        form = DepartmentForm(request.POST,user=request.user)
        
        if request.is_ajax():
            return helpers.ajax_validate_form(form)

        if form.is_valid():
            department = form.save(commit=False)
            department.creator = request.user
            department.save()
            ctx.update({"school":department.school})
            if department.id:
                messages.success(request, u'已成功创建部门 %s ' % department.name)
                redirect_url = reverse('oa_department_list') + "?sid=" + str(department.school.id)
                return redirect(redirect_url)
    else:
        form = DepartmentForm(user=request.user)
    try:
        school = get_object_or_404(School,id=school_id)
    except:
        school = None
    
    schools = helpers.get_schools(request.user)
    ctx.update({"school":school,"schools":schools})
    ctx.update({'form':form})
    return render(request, template_name, ctx)

@Has_permission('manage_department')
def update(request, department_id, template_name="oa/department_form.html"):
    """更新部门"""
    schools = helpers.get_schools(request.user)
    department = get_object_or_404(Department,pk=department_id,school__in=schools)
    school = department.school

    if request.method == 'POST':
        form = DepartmentForm(request.POST, instance=department, user=request.user)
        
        if request.is_ajax():
            return helpers.ajax_validate_form(form)
        
        if form.is_valid():
            department = form.save(commit=False)
            department.save()
            messages.success(request, u"已成功更新部门： %s " % department.name)
            redirect_url = reverse('oa_department_list') + "?sid=" + str(department.school.id)
            return redirect(redirect_url)
    else:
        form = DepartmentForm(instance=department,user=request.user)
    ctx = {"form": form, "department": department,"school":school,"schools":schools}
    return render(request, template_name, ctx)


