# -*- coding: utf-8 -*-
from django.shortcuts import render_to_response, redirect, render, get_object_or_404
from django.http import Http404
from django.http import HttpResponse
from django.utils.translation import ugettext as _
from kinger.models import Agency,School,Department,Group,GroupTeacher,GroupGrade,Attachment
from oa.forms import ClassForm
from oa.helpers import set_class_teacher,set_guide_teacher,get_schools,get_content_type_by_filename
from django.utils.encoding import smart_str, smart_unicode
from django.contrib import messages
from django.core.urlresolvers import reverse
from oa.decorators import Has_permission
from kinger.helpers import ajax_error,ajax_ok
from oa import helpers
from django.core.cache import cache
import xlwt, xlrd
import datetime


@Has_permission('manage_class')
def index(request,template_name="oa/class_list.html"):
    """班级列表"""
    schools = get_schools(request.user)
    schools = [s for s in schools if not s.parent_id==0]
    school_id = request.GET.get("sid",'')
    if school_id:
        school = get_object_or_404(School, pk=school_id)
        groups = school.group_set.all()
    else:
        school = None
        groups = Group.objects.filter(school__in=schools)
    query = request.GET.get("q",'')
    if query:
        groups = groups.filter(name__contains=query)
    
    groups = groups.exclude(type=3)
    ctx = {'schools':schools,'school':school,'groups':groups,'query':query}
    return render(request, template_name, ctx)

@Has_permission('manage_class')
def delete(request,group_id):  
    """删除班级"""
    sid = request.GET.get('sid')
    schools = get_schools(request.user)
    group = get_object_or_404(Group,pk=group_id,school__in=schools)
    school = group.school
    group.delete()
    school_id = sid
    messages.success(request, u'班级 %s 已删除' % group.name)
    redirect_url = reverse('oa_class_list') + "?sid=" + str(school_id)
    return redirect(redirect_url)

@Has_permission('manage_class')
def create(request,template_name="oa/class_form.html"):
    """创建班级"""
    ctx = {}
    schools = get_schools(request.user)
    schools = [s for s in schools if not s.parent_id==0]
    
    if request.method == 'POST':
        form = ClassForm(request.POST,user=request.user)
        
        if request.is_ajax():
            return helpers.ajax_validate_form(form)
        
        if form.is_valid():
            group = form.save(commit=False)
            group.creator = request.user
            group.save()
            ctx.update({"school":group.school})
            if group.id:
                class_teacher = request.POST.getlist('class_teacher')
                set_class_teacher(group,class_teacher)
                guide_teacher = request.POST.getlist('guide_teacher')
                set_guide_teacher(group,guide_teacher)
                messages.success(request, u'已成功创建班级 %s ' % group.name)
                redirect_url = reverse('oa_class_list') + "?sid=" + str(group.school.id)
                return redirect(redirect_url)
    else:
        form = ClassForm(user=request.user)
    ctx.update({'form':form,'schools':schools})
    return render(request, template_name, ctx)

@Has_permission('manage_class')
def update(request, group_id, template_name="oa/class_form.html"):
    """更新班级"""
    ctx = {}
    schools = get_schools(request.user)
    group = get_object_or_404(Group,pk=group_id,school__in=schools)
    if request.method == 'POST':
        form = ClassForm(request.POST, instance=group, user=request.user)
        
        if request.is_ajax():
            return helpers.ajax_validate_form(form)
        
        if form.is_valid():
            group = form.save(commit=False)
            group.save()
            class_teacher = request.POST.getlist('class_teacher')
            set_class_teacher(group,class_teacher)
            guide_teacher = request.POST.getlist('guide_teacher')
            set_guide_teacher(group,guide_teacher)
            messages.success(request, u"已成功更新班级： %s " % group.name)
            redirect_url = reverse('oa_class_list') + "?sid=" + str(group.school.id)
            return redirect(redirect_url)

    else:
        school = group.school
        form = ClassForm(instance=group,  user=request.user)
        teachers = school.teacher_set.all()
        class_teachers = teachers
        ctx.update({'teachers':teachers,'class_teachers':class_teachers})
    
    schools = get_schools(request.user)
    schools = [s for s in schools if not s.parent_id==0]
    ctx.update({"form": form, "group": group,"school":school,"schools":schools})
    return render(request, template_name, ctx)

def check_teachers(request, template_name="oa/class_check_teachers.html"):
    """  """
    schools = get_schools(request.user)
    school_id = request.POST.get("sid",None)
    group_id = request.POST.get("gid")
    try:
        group = get_object_or_404(Group, pk=group_id)
    except:
        group = None

    try:
        school = get_object_or_404(School,id=school_id)
    except:
        school = None
    
    teachers = school.teacher_set.all() if school else None
    class_teachers = teachers
    channel = request.POST.get("channel","school")
    if teachers and channel == "group":
        group_teacher_ids = [t.teacher_id for t in GroupTeacher.objects.filter(type_id=1)]
        class_teachers = teachers.exclude(pk__in=group_teacher_ids)

    data = render(request, template_name, {'class_teachers':class_teachers,\
                                           'group':group,'teachers':teachers,'channel':channel})
    con=data.content
    return ajax_ok('成功',con)

def get_school_teacher(request):
    sid = request.GET.get("sid", "")
    return helpers.get_school_teacher(sid)

@Has_permission('manage_class')
def batch_import(request, template_name="oa/class_import.html"):
    schools = helpers.get_schools(request.user)
    return render(request, template_name, {'schools':schools})

@Has_permission('manage_class')
def template(request):
    """xls template for import"""
#    response = HttpResponse(mimetype="application/ms-excel")
#    response['Content-Disposition'] = 'attachment; filename=class-template.xls'
#
#    wb = xlwt.Workbook()
#    ws = wb.add_sheet(_("Group List"))
#
#    for idx, col in enumerate([ _("Name"), _("Grade")]):
#        ws.write(0, idx, col)
#
#    wb.save(response)
#    return response

    file = get_object_or_404(Attachment,name="class-template_batch-import")
    filename = "class-template.xls"
    
    if "MSIE" in request.META['HTTP_USER_AGENT']:
        filename=urlquote(filename)
    else:
        filename=smart_str(filename)
    response = HttpResponse(file.file, content_type=get_content_type_by_filename(file.file.name))

    response['Content-Disposition'] = 'attachment; filename=%s' % filename
    return response

@Has_permission('manage_class')
def import_view(request):
    """
    """
    # 获得导入数据(文件)
    schools = helpers.get_schools(request.user)
    template_name="oa/class_import.html"
    roles_xls = request.FILES.get('classes')
    try:
        school_id = request.POST['school']
        school = get_object_or_404(School, pk=school_id)
    except:
        school = schools[0]
    
    imported_num = 0
    cache_key = "import_class_" + str(school.id) + '_' + str(request.user.id)
    if request.method == 'POST':
        data = cache.get(cache_key)
        print data,'aaaaaaaaaaaaaaaaaaaaaaaaaaaaa'
        if not data:
            messages.error(request, "您还没有上传文件")
            return render(request, template_name, {'schools':schools,'school':school,'file_error':"您还没有上传文件"})
        
        for d in data:
            try:
                group,created = Group.objects.get_or_create(name=d['name'],grade_id=d['grade'],creator=request.user,school=school)
                if created:
                    imported_num = imported_num + 1
            except:
                pass
                
            print imported_num,datetime.datetime.now(),'---------------------------------'
        
    if imported_num:
        msg = u"成功导入 %(imported_num)s 个  %(role)s" % {'imported_num': imported_num, 'role': '班级'}
        print msg,'mmmmmmmmmmmmmmmm'
        cache.delete(cache_key)
        messages.success(request, msg)
    return render(request, template_name, {'schools':schools,'school':school})


def check_import(request, template_name="oa/class_import.html"):
    schools = helpers.get_schools(request.user)
    roles_xls = request.FILES.get('classes')
    error_list = []
    num = 0
    
    try:
        school_id = request.POST['school']
        school = get_object_or_404(School, pk=school_id)
    except:
        school = schools[0]
    
    if not roles_xls:
        messages.error(request, _("Files Missing"))
        return render(request, template_name, {'schools':schools,'school':school})
    try:
        wb = xlrd.open_workbook(file_contents=roles_xls.read())
        s = wb.sheet_by_index(0)
    except xlrd.biffh.XLRDError:
        messages.error(request, _("Unsupported format, or corrupt file"))
        return render(request, template_name, {'schools':schools,'school':school})
 
    try:
        trans_map = {
            "name": s.cell(0, 0).value,
            "grade": s.cell(0, 1).value,
        }
    except:
        trans_map = None
    xls_cache = []  
    for row in range(s.nrows)[1:]:
        name  = ''
        grade = ''
        num = num + 1
        try:
            name = s.cell(row, 0).value.strip()
        except Exception, e:
            print e
        
        try:
            grade = s.cell(row, 1).value.strip()
        except Exception, e:
            print e
            
        if not name:
            messages.error(request, u"导入的 Excel 文件缺少需要的列, 或者该列数据为空.")
            return redirect('oa_class_batch_import')
        
       
        try:
            groupgrade = GroupGrade.objects.get(name=grade)
        except:
#            error_list.append({'name':name,'grade':grade,'row':row,'msg':'年级名称错误'})
#            continue
            groupgrade = GroupGrade.objects.get(id=6)
        
#        initial_data = {"name": name, "grade": groupgrade.id}
#        form = StudentForm(initial_data)
#        if not form.is_valid():
#            error_list.append({'name':name,'mobile':mobile,'row':row,'group':class_name,'msg':form.errors})
#            continue
        try:
            group = Group.objects.get(name=name,grade_id=groupgrade.id,creator=request.user,school=school)
            error_list.append({'name':name,'grade':grade,'row':row,'msg':'该班级已存在'})
            continue
        except:
            pass
       
        xls_cache.append({"name": name, "grade": groupgrade.id})
        
    cache_key = "import_class_" + str(school.id) + '_' + str(request.user.id)
#     data = cache.get(cache_key)
    rs = cache.set(cache_key, xls_cache)
    
    data = cache.get(cache_key)
    print data,'ddddddddddddddddddddddddddd'
    ctx = {'schools':schools,'errors':error_list,'school':school,\
            'num':num,'error_num':len(error_list),'filename':str(roles_xls),'checked':True}
    return render(request, template_name, ctx)
