# -*- coding: utf-8 -*-
from django.shortcuts import redirect, render, get_object_or_404
from kinger.models import DiskCategory,Disk,Attachment,School
from django.contrib.auth.models import User
from django.core.context_processors import csrf
from django.contrib import messages
from django.db.models import Q
from django.utils.translation import ugettext as _
from django.http import HttpResponse
from django.views.decorators.http import require_POST, require_GET
import datetime,os
from kinger.settings import FILE_PATH
from django.core.exceptions import ObjectDoesNotExist, MultipleObjectsReturned
from userena import signals as userena_signals
from django.core.urlresolvers import reverse
from django.forms.formsets import formset_factory
from oa.decorators import Has_permission
from django.contrib import auth
from django.contrib.auth.views import logout
from oa.helpers import get_schools,is_agency_user,user_manage_school,disk_category_group
from oa.supply.forms import DiskCategoryForm,DiskForm
from kinger.helpers import ajax_ok
from oss_extra.storage import AliyunStorage
from django.contrib.sites.models import Site
from celery.task.http import URL
try:
    import simplejson as json
except ImportError:
    import json
from oa.decorators import Has_permission

@Has_permission('manage_disk')
def disk_category(request, template_name="disk/category_form.html"):
    """网盘类别设置"""
    schools = get_schools(request.user)
    school_id = int(request.GET.get("sid")) if request.GET.get("sid") else 0
    type = int(request.GET.get("ty")) if request.GET.get("ty") else 0
    school = user_manage_school(request.user,school_id)
    extra = int(request.GET.get("extra", 0))
    categorys = []
    category_list = []
    if type == 1 and request.user.teacher.school.parent_id == 0:
        p_list = DiskCategory.objects.filter(school_id=school_id,parent_id=0,type=type)
    else:
        p_list = DiskCategory.objects.filter(school=school,parent_id=0,type=type)
    if type == 0:
        p_list = p_list.filter(user=request.user)
    for p in p_list:
        categorys.append(p)
        category_list.append({'name':p.name,'parent':None})
        for s in DiskCategory.objects.filter(school=school,parent=p,type=type):
            categorys.append(s)
            category_list.append({'name':s.name,'parent':s.parent})
    
    if request.method == 'POST':
        if type == 1 and school_id == 0:
            messages.success(request, u'请选择机构')
            return redirect(reverse('oa_disk_category') + "?sid=" + str(school_id) + "&ty=" + str(type)) 
        extra = request.POST['form-TOTAL_FORMS']
        formset = formset_factory(DiskCategoryForm, extra=extra)
        form = formset(request.POST,initial=category_list)
        
        if request.is_ajax():
            error_list = []
            for fo in for4:
                error_list = error_list + fo.errors.items()
            return helpers.ajax_validate_form_error_list(error_list)
        
        if form.is_valid():
            i = 0
            for f in form:
                try:
                    cat = categorys[i]
                    cat.name = f['name'].value()
                    if type == 0:
                        cat.user = request.user
                    cat.save()
                except:
                    cat = f.save(commit=False)
                    if not f['parent'].value():
                        cat.parent_id = 0
                    cat.school = school
                    cat.type = type
                    if type == 0:
                        cat.user = request.user
                    cat.save()
                i += 1
            messages.success(request, u'操作成功')
            return redirect(reverse('oa_disk_category') + "?sid=" + str(school_id) + "&ty=" + str(type)) 
    else:
        formset = formset_factory(DiskCategoryForm,extra=extra)
        form = formset(initial=category_list)

    ctx = {'form':form,'extra':extra,'categorys':categorys,'sid':school_id,'schools':schools,"type":type}
    return render(request, template_name,ctx)

@Has_permission('manage_disk')
def get_extra_form(request,template_name="oa/extra_form.html"):
    """公文类别附加表单"""
    order = int(request.POST.get('order'))
    formset = formset_factory(DiskCategoryForm, extra=order + 1)
    form = formset()
    pid = request.POST.get('parent_id',0)
    parent = None
    if pid:
        parent_list = []
        parent = get_object_or_404(DiskCategory,id=pid)
        for i in range(order):
            parent_list.append({'name':'','parent':parent})
        form = formset(initial=parent_list)
    
    form = form[order]
    ctx = {'form':form,'order':order,'parent':parent}
    
    data = render(request,template_name,ctx)
    con=data.content
    return ajax_ok('成功',con)

@Has_permission('manage_disk')
def delete_category(request,cat_id):
    """删除公文类别"""
    ty = request.GET.get('ty','')
    sid = request.GET.get('sid','')
    schools = get_schools(request.user)
    category = get_object_or_404(DiskCategory,id=cat_id,school__in=schools)
    update_disk_category(category)
    if category.parent_id == 0:
        sub_categories = DiskCategory.objects.filter(parent=category)
        sub_categories.delete()
    category.delete()
    messages.success(request, u'删除成功')
    return redirect(reverse('oa_disk_category') + "?sid=" + sid + "&ty=" + ty) 

@Has_permission('manage_disk')
def disk_index(request, template_name="disk/disk_index.html"):
    """物资列表页"""
    if request.method == 'POST':
        ty = request.POST.get("ty",'')
        disk_pks = request.POST.getlist("disks")
        disks = Disk.objects.filter(id__in=disk_pks)
        disks.delete()
        messages.success(request, u'删除成功 ')
    
    user = request.user
    school = user.teacher.school
    set_default_category(user)
    schools = []
    ty = request.GET.get('ty','')
    sid = int(request.GET.get("sid",0))
    if ty == 'school':
        if school.parent_id == 0:
            schools = school.subschools.all()
            if sid:
                disks = Disk.objects.filter(school_id=sid).exclude(parent_id=0)
            else:
                disks = Disk.objects.filter(school__parent_id=school.id).exclude(parent_id=0)
        else:
            disks = Disk.objects.filter(school=school).exclude(parent_id=0)
            
    elif ty == "agency":
        disks = Disk.objects.filter(school=school,school__parent_id=0).exclude(parent_id=0)
    else:
        disks = Disk.objects.filter(creator=user,parent_id=0,school=school)
        
    query = request.GET.get("q", '')
    st = request.GET.get("st", '')
    et = request.GET.get("et", '')
   
    qq = Q(title__contains=query) if query else Q()
    qs = (Q(mtime__startswith=st) | Q(mtime__gte=st)) if st else Q()
    qe = (Q(mtime__startswith=et) | Q(mtime__lte=et)) if et else Q()
    q = qs & qe & qq
    disks = disks.filter(q)
    ctx = {"school":school,"disks":disks,"ty":ty,"query":query,"st":st,"et":et,"sid":sid,"schools":schools}
    return render(request, template_name, ctx)

#@Has_permission('manage_disk')
#def create_disk(request, template_name="disk/disk_form.html"):
#    categorys = []
#    user = request.user
#    school = user.teacher.school
#    personal_list = disk_category_group(school,user)
#    school_list = disk_category_group(school)
#    
#    ctx = {}
#    file_list = []
#    school = user.teacher.school
#    if request.method == 'POST':
#        form = DiskForm(request.POST)
#        if form.is_valid():
#            disk = form.save(commit=False)
#            disk.creator = request.user
#            disk.school = school
#            disk.save()
#            for f in request.FILES.getlist('files'):
#                atta = Attachment()
#                atta.name = f.name
#                atta.file = f
#                atta.save()
#                file_list.append(atta)
#            disk.files = file_list
#            is_share = request.POST.get('is_share') 
#            print is_share,'is_share--------------------'
#            if is_share:
#                pid = disk.id
#                scat = request.POST.get('scat')
#                school_disk = disk
#                school_disk.id = None
#                school_disk.category_id = scat
#                school_disk.parent_id = pid
#                school_disk.save()
#                school_disk.files = file_list
#
#            messages.success(request, u'已成功创建文档%s ' % disk.title)
#            redirect_url = reverse('oa_disk_index')
#            return redirect(redirect_url)
#    else:
#        form = DiskForm()
#        
#    schools = get_schools(request.user)
#    ctx.update({'form':form,"school":school,'personal_list':personal_list,'school_list':school_list})
#    return render(request, template_name, ctx)

@Has_permission('manage_disk')
def create_disk(request, template_name="disk/disk_form.html"):
    categorys = []
    user = request.user
    school = user.teacher.school
    personal_list = disk_category_group(school,user)
    school_list = disk_category_group(school)
    form = DiskForm()
    ctx = {}
    file_list = []
    school = user.teacher.school
    if request.method == 'POST':
        
        f = request.FILES.get('files')
        chunks = int(request.POST.get('chunks',1))
        if chunks == 1 or not f:
            form = DiskForm(request.POST)
            if form.is_valid():
                disk = form.save(commit=False)
                disk.creator = request.user
                disk.school = school
                disk.save()
                try:
                    atta = Attachment()
                    atta.name = f.name
                    atta.file = f
                    atta.save()
                    file_list.append(atta)
                    disk.files = file_list
                except:
                    pass
                is_share = request.POST.get('is_share') 
                if is_share:
                    disk.subdisks.all().delete()
                    pid = disk.id
                    scat = request.POST.get('scat')
                    school_disk = disk
                    school_disk.id = None
                    school_disk.category_id = scat
                    school_disk.parent_id = pid
                    school_disk.save()
                    school_disk.files = file_list
                
                if disk.id:
                    if request.is_ajax():
                        return HttpResponse(json.dumps({'status':1,'desc':"ok"}))
                    else:
                        redirect_url = reverse('oa_disk_index')
                        return redirect(redirect_url)
            return HttpResponse(json.dumps({'status':0,'desc':"error"}))
        else:
            chunk = int(request.POST.get('chunk'))
            file_id = request.POST.get('file_id')
            name = request.POST.get('name')
            
            file_path = FILE_PATH + '/temp/' + str(file_id)
            fp = open(file_path,"a+b")
            fp.write(f.read())
            fp.close()
            
            if chunk + 1  == chunks:
                filename = 'attachment/' + str(file_id) + '.' +  name.split('.')[-1].lower()
                try:
                    URL('http://' + SITE_INFO.domain + reverse('cron_make_large_img')).post_async(filename=filename,file_path=file_path)
                except:
                    fr = open(file_path,"rb")
                    content = fr.read()
                    fr.close()
                    if os.path.isfile(file_path):
                        os.remove(file_path)
                    AliyunStorage(). _put_file(filename, content)
                    
                form = DiskForm(request.POST)
                if form.is_valid():
                    atta  = Attachment(name=file_id,file=filename)
                    atta.save()
                    file_list.append(atta)
                    
                    disk = form.save(commit=False)
                    disk.creator = request.user
                    disk.school = school
                    disk.file = filename
                    disk.save()
                    disk.files = file_list
                    is_share = request.POST.get('is_share') 
                    if is_share:
                        disk.subdisks.all().delete()
                        pid = disk.id
                        scat = request.POST.get('scat')
                        school_disk = disk
                        school_disk.id = None
                        school_disk.category_id = scat
                        school_disk.parent_id = pid
                        school_disk.save()
                        school_disk.files = file_list
                    data = json.dumps({'status':1,'desc':"ok"})
                    return HttpResponse(data)
                else:
                    return HttpResponse(json.dumps({'status':0,'desc':"error"}))
            data = json.dumps({'status':1,'desc':"ok"})
            return HttpResponse(data)
        
    schools = get_schools(request.user)
    ctx.update({'form':form,"school":school,'personal_list':personal_list,'school_list':school_list})
    return render(request, template_name, ctx)

#@Has_permission('manage_disk')
#def update_disk(request, disk_id, template_name="disk/disk_form.html"):
#    disk = get_object_or_404(Disk,id=disk_id)
#    categorys = []
#    user = request.user
#    school = user.teacher.school
#    personal_list = disk_category_group(school,user)
#    school_list = disk_category_group(school)
#    
#    ctx = {}
#    file_list = []
#    school = user.teacher.school
#    if request.method == 'POST':
#        form = DiskForm(request.POST,instance=disk)
#        
#        if form.is_valid():
#            disk = form.save(commit=False)
#            disk.save()
#            for f in request.FILES.getlist('files'):
#                atta = Attachment()
#                atta.name = f.name
#                atta.file = f
#                atta.save()
#                file_list.append(atta)
#                disk.files.add(atta)
#        
#            is_share = request.POST.get('is_share') 
#            print is_share,'is_share--------------------'
#            if is_share:
#                pid = disk.id
#                scat = request.POST.get('scat')
#                school_disk = disk
#                school_disk.id = None
#                school_disk.category_id = scat
#                school_disk.parent_id = pid
#                school_disk.save()
#                school_disk.files = file_list
#
#            messages.success(request, u'已成功创建文档%s ' % disk.title)
#            ty = request.GET.get('ty','')
#            query = request.GET.get("q", '')
#            st = request.GET.get("st", '')
#            st = '' if st == '开始时间' else st
#            et = request.GET.get("et", '')
#            et = '' if et == '结束时间' else et
#            query = '' if query == '关键字' else query
#            redirect_url = reverse('oa_disk_index') + "?ty=" + ty + "&q=" + query + "&st=" + st + "&et=" + et
#            return redirect(redirect_url)
#    else:
#        form = DiskForm(instance=disk)
#        
#    schools = get_schools(request.user)
#    ctx.update({'form':form,"school":school,'personal_list':personal_list,'school_list':school_list,"disk":disk})
#    return render(request, template_name, ctx)

@Has_permission('manage_disk')
def update_disk(request, disk_id, template_name="disk/disk_form.html"):
    disk = get_object_or_404(Disk,id=disk_id)
    categorys = []
    user = request.user
    school = user.teacher.school
    personal_list = disk_category_group(school,user)
    school_list = disk_category_group(school)
    form = DiskForm(instance=disk)
    ctx = {}
    file_list = disk.files
    school = user.teacher.school
    if request.method == 'POST':
        f = request.FILES.get("files")
        chunks = int(request.POST.get('chunks','1'))
        if chunks == 1 or not f:
            form = DiskForm(request.POST,instance=disk)
            if form.is_valid():
                disk = form.save(commit=False)
                disk.save()
                delete_file = request.POST.get('delete_file')
                if delete_file and not f:
                    disk.files = []
                else:
                    if f:
                        atta = Attachment()
                        atta.name = f.name
                        atta.file = f
                        atta.save()
                        file_list = []
                        file_list.append(atta)
                        disk.files = file_list
                is_share = request.POST.get('is_share') 
                if is_share:
                    disk.subdisks.all().delete()
                    pid = disk.id
                    scat = request.POST.get('scat')
                    school_disk = disk
                    school_disk.id = None
                    school_disk.category_id = scat
                    school_disk.parent_id = pid
                    school_disk.save()
                    
                if disk.id:
                    if request.is_ajax():
                        return HttpResponse(json.dumps({'status':1,'desc':"ok"}))
                    else:
                        redirect_url = reverse('oa_disk_index')
                        return redirect(redirect_url)
            return HttpResponse(json.dumps({'status':0,'desc':"error"}))
        else:
            chunk = int(request.POST.get('chunk'))
            file_id = request.POST.get('file_id')
            name = request.POST.get('name')
            
            file_path = FILE_PATH + '/temp/' + str(file_id)
            fp = open(file_path,"a+b")
            fp.write(f.read())
            fp.close()
            
            if chunk + 1  == chunks:
                filename = 'disk/' + str(file_id) + '.' +  name.split('.')[-1].lower()
                try:
                    URL('http://' + SITE_INFO.domain + reverse('cron_make_large_img')).post_async(filename=filename,file_path=file_path)
                except:
                    fr = open(file_path,"rb")
                    content = fr.read()
                    fr.close()
                    if os.path.isfile(file_path):
                        os.remove(file_path)
                    AliyunStorage(). _put_file(filename, content)
                    
                form = DiskForm(request.POST,instance=disk)
                if form.is_valid():
                    disk = form.save(commit=False)
                    disk.creator = request.user
                    disk.school = school
                    disk.save()
                    
                    atta  = Attachment(name=file_id,file=filename)
                    atta.save()
                    file_list = []
                    file_list.append(atta)
                    disk.files = file_list
                    is_share = request.POST.get('is_share') 
                    if is_share:
                        disk.subdisks.all().delete()
                        pid = disk.id
                        scat = request.POST.get('scat')
                        school_disk = disk
                        school_disk.id = None
                        school_disk.category_id = scat
                        school_disk.parent_id = pid
                        school_disk.save()
                    return HttpResponse(json.dumps({'status':1,'desc':"ok"}))
                else:
                    return HttpResponse(json.dumps({'status':0,'desc':"error"}))
            return HttpResponse(json.dumps({'status':1,'desc':"ok"}))
    schools = get_schools(request.user)
    ctx.update({'form':form,"school":school,'personal_list':personal_list,'school_list':school_list,"disk":disk})
    return render(request, template_name, ctx)

@Has_permission('manage_disk')
def disk_detail(request,disk_id,template_name="disk/disk_detail.html"):
    """网盘详情页"""
    disk = get_object_or_404(Disk,id=disk_id)
    files = disk.files.all()
    ctx = {'disk':disk,'files':files}
    return render(request, template_name, ctx)

def set_default_category(user):
    school = user.teacher.school
    uc,cuc = DiskCategory.objects.get_or_create(name="其他",user=user,type=0,order=1,school=school)
    school = user.teacher.school
    if school.parent_id > 0:
        ch,cch = DiskCategory.objects.get_or_create(name="其他",school=school,type=1,order=1)
    else:
        sc,cus = DiskCategory.objects.get_or_create(name="其他",school=school,type=2,order=1)
        schools = School.objects.filter(parent=school)
        for s in schools:
            ch,cch = DiskCategory.objects.get_or_create(name="其他",school=s,type=1,order=1)
            
def update_disk_category(category):
    q = (Q(category=category) | Q(category__parent_id=category.id))
    disks = Disk.objects.filter(q)
    if category.type == 0:
        cat,c = DiskCategory.objects.get_or_create(name="其他",user=category.user,type=0,order=1,school=category.school)
    else:
        cat,c = DiskCategory.objects.get_or_create(name="其他",school=category.school,type=category.type,order=1)
    disks.update(category=cat)
