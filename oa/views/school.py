# -*- coding: utf-8 -*-
from django.shortcuts import render_to_response, redirect, render, get_object_or_404
from django.http import Http404
from django.http import HttpResponse
from kinger.models import Agency,School,Department,Group,Teacher,Student
from oa.forms import SchoolForm
from django.contrib import messages
import xlwt, xlrd
from oa import helpers
from django.utils.translation import ugettext as _
from oa.decorators import Has_permission

@Has_permission('manage_school')
def index(request,template_name="oa/school_list.html"):
    """学园管理列表页"""
    schools = helpers.get_schools(request.user)
    school_pks = [s.id for s in schools]
    query = request.GET.get("q",'')
    if query:
        schools = School.objects.filter(name__contains=query,pk__in=school_pks)
    ctx = {'schools':schools,"query":query}
    return render(request, template_name, ctx)

@Has_permission('manage_school')
def delete(request,school_id):  
    """删除学园"""
    school_pks = [s.id for s in helpers.get_schools(request.user)]
    school = get_object_or_404(School,pk=school_id,pk__in=school_pks)
    school.delete()
    messages.success(request, u'学园 %s 已删除' % school.name)
    return redirect("oa_school_list")

@Has_permission('manage_school')
def create(request,template_name="oa/school_form.html"):
    """创建学园"""
    ctx = {}
    schools = helpers.get_schools(request.user)
    try:
        agency = schools[0].parent
    except:
        agency = schools[0]
    if request.method == 'POST':
        form = SchoolForm(request.POST)
        
        if request.is_ajax():
            return helpers.ajax_validate_form(form)
        
        if form.is_valid():
            school = form.save(commit=False)
            school.creator = request.user
            school.parent = agency
#             admins = [u for u in agency.admins.all()]
            school.save()
            if school.id:
#                 school.admins = admins
                messages.success(request, u'已成功创建学园 %s ' % school.name)
            return redirect("oa_school_list")
    else:
        form = SchoolForm()
    ctx.update({'form':form})
    return render(request, template_name, ctx)

@Has_permission('manage_school')
def update(request, school_id, template_name="oa/school_form.html"):
    """更新学园"""
    school_pks = [s.id for s in helpers.get_schools(request.user)]
    school = get_object_or_404(School,pk=school_id,pk__in=school_pks)
#     school = get_object_or_404(School, pk=school_id)
    if request.method == 'POST':
        form = SchoolForm(request.POST, instance=school)
        
        if request.is_ajax():
            return helpers.ajax_validate_form(form)
        
        if form.is_valid():
            form.save()
            messages.success(request, u"已成功更新学园： %s " % school.name)

            return redirect("oa_school_list")
    else:
        form = SchoolForm(instance=school)

    ctx = {"form": form, "school": school}
    return render(request, template_name, ctx)

@Has_permission('manage_school')
def update(request, school_id, template_name="oa/school_form.html"):
    """更新学园"""
    school_pks = [s.id for s in helpers.get_schools(request.user)]
    school = get_object_or_404(School,pk=school_id,pk__in=school_pks)
#     school = get_object_or_404(School, pk=school_id)
    if request.method == 'POST':
        form = SchoolForm(request.POST, instance=school)
        
        if request.is_ajax():
            return helpers.ajax_validate_form(form)
        
        if form.is_valid():
            form.save()
            messages.success(request, u"已成功更新学园： %s " % school.name)

            return redirect("oa_school_list")
    else:
        form = SchoolForm(instance=school)

    ctx = {"form": form, "school": school}
    return render(request, template_name, ctx)

@Has_permission('manage_school')
def export_member(request,school_id):
    school = School.objects.get(pk=school_id)
    ty = request.GET.get("ty",'teacher')
    
    if ty == "teacher":
        teachers = Teacher.objects.filter(school=school)
        teachers = teachers.filter(is_delete=False)
        response = HttpResponse(mimetype="application/ms-excel")
        response['Content-Disposition'] = 'attachment; filename=teachers.xls'
    
        wb = xlwt.Workbook()
        ws = wb.add_sheet(_("Teacher List"))
    
        for idx, col in enumerate([ _("Name"),_("Username"), _("Mobile")]):
            ws.write(0, idx, col)
        row = 0
        for s in teachers:
            row += 1 
            col = 0
            name = helpers.get_name(s.user)
            for c in [name,s.user.username,s.user.profile.mobile]:   
                ws.write(row,col,c)
                col += 1
        wb.save(response)
        return response
    else:
        students = Student.objects.filter(school=school,is_delete=False)
        response = HttpResponse(mimetype="application/ms-excel")
        response['Content-Disposition'] = 'attachment; filename=teachers.xls'
    
        wb = xlwt.Workbook()
        ws = wb.add_sheet(_("Teacher List"))
    
        for idx, col in enumerate([ _("Name"),_("Username"), _("Mobile"), _('school class')]):
            ws.write(0, idx, col)
        row = 0
        for s in students:
            col = 0
            name = helpers.get_name(s.user)
            try:
                student_info = [name,s.user.username,s.user.profile.mobile,s.group.name]
                row += 1 
                for c in student_info:   
                    ws.write(row,col,c)
                    col += 1
            except:
                pass
        wb.save(response)
        return response


