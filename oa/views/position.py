# -*- coding: utf-8 -*-
from django.shortcuts import render_to_response, redirect, render, get_object_or_404
from django.http import Http404
from django.http import HttpResponse
from kinger.models import Agency,School,Department,Position
from oa.forms import AgencyForm,DepartmentForm,PositionForm
from django.contrib import messages
from django.core.urlresolvers import reverse
from oa import helpers
from oa.decorators import Has_permission

@Has_permission('manage_position')
def index(request,template_name="oa/position_list.html"):
    """职务管理列表"""
    schools = helpers.get_schools(request.user)
    school_id = request.GET.get("sid",'')
    if school_id:
        school = get_object_or_404(School, pk=school_id)
        positions = school.positions.all()
    else:
        school = None
        positions = Position.objects.filter(school__in=schools)
    
    ctx = {'schools':schools,'school':school,'positions':positions}
    return render(request, template_name, ctx)

@Has_permission('manage_position')
def delete(request,position_id):  
    """删除职务"""
    schools = helpers.get_schools(request.user)
    position = get_object_or_404(Position,pk=position_id,school__in=schools)
    position.delete()
    messages.success(request, u'职务 %s 已删除' % position.name)
    redirect_url = reverse('oa_position_list') + "?sid=" + str(position.school.id)
    return redirect(redirect_url)

@Has_permission('manage_position')
def create(request,template_name="oa/position_form.html"):
    """创建职务"""
    ctx = {}
    school_id = request.GET.get("sid",0)
    if request.method == 'POST':
        form = PositionForm(request.POST)
        school_id = int(request.POST.get('school'))
        
        if request.is_ajax():
            return helpers.ajax_validate_form(form)
        
        if form.is_valid():
            position = form.save(commit=False)
            position.creator = request.user
            position.save()
            ctx.update({"school":position.school})
            if position.id:
                messages.success(request, u'已成功创建职务 %s ' % position.name)
#                 redirect_url = reverse('oa_position_list') + "?sid=" + str(position.school.id)
                return redirect('oa_position_list')
    else:
        form = PositionForm()
    try:
        school = get_object_or_404(School,id=school_id)
    except:
        school = None
    schools = helpers.get_schools(request.user)
    ctx.update({"school":school,"schools":schools})
    ctx.update({'form':form})
    return render(request, template_name, ctx)

@Has_permission('manage_position')
def update(request, position_id, template_name="oa/position_form.html"):
    """更新职务"""
    schools = helpers.get_schools(request.user)
    position = get_object_or_404(Position,pk=position_id,school__in=schools)
    school = position.school

    if request.method == 'POST':
        form = PositionForm(request.POST, instance=position)
        
        if request.is_ajax():
            return helpers.ajax_validate_form(form)
        
        if form.is_valid():
            position = form.save(commit=False)
            position.save()
            messages.success(request, u"已成功更新职务： %s " % position.name)
            redirect_url = reverse('oa_position_list') + "?sid=" + str(position.school.id)
            return redirect(redirect_url)
    else:
        form = PositionForm(instance=position)
    ctx = {"form": form, "position": position,"school":school,"schools":schools}
    return render(request, template_name, ctx)


