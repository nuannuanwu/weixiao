# -*- coding: utf-8 -*-
from django.shortcuts import render_to_response, redirect, render, get_object_or_404
from django.http import Http404
from django.http import HttpResponse
from kinger.models import WebSite,School,Part,PartCategory,Template,Teacher,StarFigure,Student,Group
from django.contrib.auth.models import User
from oa.forms import WebSiteForm,PartForm,StarFigureForm
from django.contrib import messages
from django.core.urlresolvers import reverse
from oa.helpers import is_teacher,is_student,get_schools
from oa.decorators import Has_permission
from django.db.models import Q
from oa import helpers
from kinger.settings import FILE_PATH
from oss_extra.storage import AliyunStorage
from django.contrib.sites.models import Site
from celery.task.http import URL
import os
try:
    import simplejson as json
except ImportError:
    import json

SITE_INFO = Site.objects.get_current()

@Has_permission('manage_school_website_list')
def index(request,template_name="oa/website_list.html"):
    schools = get_schools(request.user)
    school = schools[0]
    query = request.GET.get('q','')
    s = int(request.GET.get('s',-1))
    qq = Q(name__contains=query) if query else Q()
    qs = Q(school_id=s) if s != -1 else Q()
    q = qs & qq
    
    if request.method == 'POST':
        status = int(request.POST.get('status',0))
        site_pks = request.POST.getlist('site_pks')
        sites = WebSite.objects.filter(pk__in=site_pks)
        sites.update(status=status)
    websites = WebSite.objects.filter(school__in=schools)
    websites = websites.filter(q)
    domain_string = helpers.get_parent_domain_string(request)
    
    ctx = {'websites':websites,'query':query,'school_id':s,'schools':schools,'school':school,'domain_string':domain_string}
    return render(request, template_name,ctx)

@Has_permission('manage_school_website_list')
def update_website(request,site_id,template_name="oa/website_detail.html"):
    schools = get_schools(request.user)
    site = get_object_or_404(WebSite,id=site_id,school__in=schools)
    helpers.set_website_visit(request.user,site)
    if request.method == 'POST':
        form = WebSiteForm(request.POST,request.FILES,instance=site)
        
        if request.is_ajax():
            return helpers.ajax_validate_form(form)
        print form.errors,'eeeeeeeeee'
        if form.is_valid():
            site = form.save(commit=False)
            site.save()
            messages.success(request, u'已成功修改网站%s ' % site.name)
            return redirect(request.get_full_path())
    else:
        form = WebSiteForm(instance=site)
    ctx = {'form':form,'site':site}
    return render(request, template_name, ctx)
        
@Has_permission('manage_school_website_list')
def create(request,template_name="oa/website_form.html"):
    
    school = get_schools(request.user)[0]
    schools = get_schools(request.user)
    domain_string = helpers.get_parent_domain_string(request)
    if request.method == 'POST':
        form = WebSiteForm(request.POST)
        print form.errors
        if request.is_ajax():
            return helpers.ajax_validate_form(form)
        
        if form.is_valid():
            school_id = request.POST.get("school", '')
            if school_id:
                school = School.objects.get(pk=school_id)
                
            print school,'sssssss'
#            type = form.cleaned_data['type']
#            print type,'tttttttttt'
            website = form.save(commit=False)
            website.creator = request.user
#            if not type:
#                website.domain = website.domain + '.' + domain_string
            website.school = school
            website.save()
            if website.id:
                messages.success(request, u'已成功创建网站%s ' % website.name)
                return redirect("oa_website_list")
    else:
        form = WebSiteForm()
    
    ctx = {'form':form,'schools':schools,'school':school,'domain_string':domain_string}
    return render(request, template_name, ctx)

@Has_permission('manage_school_website_list')
def edit_website(request,site_id,template_name="oa/website_form.html"):
    schools = get_schools(request.user)
    site = get_object_or_404(WebSite,id=site_id,school__in=schools)
    school = site.school
    domain_string = helpers.get_parent_domain_string(request)
    if request.method == 'POST':
        form = WebSiteForm(request.POST,instance=site)
#        print form.errors
        if form.is_valid():
            website = form.save(commit=False)
            website.creator = request.user
            website.school = school
            website.save()
            if website.id:
                messages.success(request, u'已成功更新网站%s ' % website.name)
                return redirect("oa_website_list")
    else:
        form = WebSiteForm(instance=site)
    
    ctx = {'form':form,'schools':schools,'school':school,'domain_string':domain_string,'site':site}
    return render(request, template_name, ctx)

@Has_permission('manage_school_website_list')
def create_part(request,site_id,template_name="oa/part_form.html"):
    schools = get_schools(request.user)
    site = get_object_or_404(WebSite,id=site_id,school__in=schools)
    helpers.set_website_visit(request.user,site)
    cid = int(request.GET.get("cid", 5))
    try:
        category = get_object_or_404(PartCategory,id=cid)
    except:
        category = None
    try:
        if category.id == 4:
            part = None
        else:
            part = Part.objects.get(site=site,category=category)
        
    except:
        part =None

        
    categorys = []
    if category and category.parent_id == 1:
        categorys = PartCategory.objects.filter(parent=category.parent)
    school = site.school
    if request.method == 'POST':
        form = PartForm(request.POST,category=category,user=request.user,instance=part)
        
        if request.is_ajax():
            return helpers.ajax_validate_form(form)
        
        if form.is_valid():
            cid = int(request.POST.get("cid",0))
            category = get_object_or_404(PartCategory,id=cid)
            part = form.save(commit=False)
            if not form.cleaned_data['creator']:
                part.creator = request.user.teacher
            part.school = school
            part.category = category
            part.site = site
#             part.video_type = 0
#             part.type = 0
            print category,'ccccccccccc'
            part.save()
            if part.id:
                messages.success(request, u'已成功修改%s ' % part.category)
                if part.category_id == 4:
                    return redirect(reverse('oa_part_teache',kwargs={'site_id':site.id}))
    else:
        form = PartForm(category=category,user=request.user,instance=part)
    ctx = {'form':form,'category':category,'categorys':categorys,'site':site,'school':school}
    return render(request, template_name, ctx)

@Has_permission('manage_school_website_list')
def update_part(request,part_id,template_name="oa/part_form.html"):
    schools = get_schools(request.user)
    part = get_object_or_404(Part,id=part_id,site__school__in=schools)
    site = part.site
    helpers.set_website_visit(request.user,site)
    category = part.category
    cid = int(request.GET.get("cid", 5))
    categorys = PartCategory.objects.filter(parent_id=part.category.parent_id).exclude(parent_id=0)
    school = site.school
    if request.method == 'POST':
        form = PartForm(request.POST,category=category,user=request.user,instance=part)
        
        if request.is_ajax():
            return helpers.ajax_validate_form(form)
        
        if form.is_valid():
            cid = int(request.POST.get("cid"))
            category = get_object_or_404(PartCategory,id=cid)
            part = form.save(commit=False)
            if not form.cleaned_data['creator']:
                part.creator = request.user.teacher
            part.save()
            if part.id:
                messages.success(request, u'已成功创建%s ' % part.category)
#                return redirect("oa_website_list")
    else:
        form = PartForm(category=category,user=request.user,instance=part)
    ctx = {'form':form,'category':category,'categorys':categorys,'site':site}
    return render(request, template_name, ctx)

@Has_permission('manage_school_website_list')
def part_teache(request,site_id,template_name="oa/nav_teache_list.html"):
    schools = get_schools(request.user)
    site = get_object_or_404(WebSite,id=site_id,school__in=schools)
    helpers.set_website_visit(request.user,site)
    ty = int(request.GET.get('ty',-1))
    parts = Part.objects.filter(site=site,category_id=4).order_by('-type','-ctime')
    if ty != -1:
        parts = parts.filter(type=ty)
        
    if request.method == 'POST':
        part_pks = request.POST.getlist('part_pks')
        parts = Part.objects.filter(pk__in=part_pks)
        
        oty = int(request.POST.get('operate',-1))
        if oty != -1:
            if oty == 0:
                parts.delete()
            else:
                parts.update(type=oty)
                messages.success(request, u'操作成功 ')
            return redirect(reverse('oa_part_teache',kwargs={'site_id':site_id}) + "?ty=" + str(ty))
    ctx = {'site':site,'parts':parts,'ty':ty}
    return render(request, template_name, ctx)

@Has_permission('manage_school_website_list')
def delete_part_teaches(request):
    schools = get_schools(request.user)
    if request.method == 'POST':
        part_pks = request.POST.getlist('part_pks')
        parts = Part.objects.filter(pk__in=part_pks,school__in=schools)
        parts.delete()
        site_id = int(request.POST.get('sid'))
        messages.success(request, u'删除成功 ')
    return redirect(reverse('oa_part_teache',kwargs={'site_id':site_id}))

@Has_permission('manage_school_website_list')
def announcement_list(request,site_id,template_name="oa/announcement_list.html"):
    type = int(request.GET.get("ty",-1))
    schools = get_schools(request.user)
    site = get_object_or_404(WebSite,id=site_id,school__in=schools)
    helpers.set_website_visit(request.user,site)
    category = get_object_or_404(PartCategory,id=9)
    categorys = PartCategory.objects.filter(parent=category.parent)
    parts = Part.objects.filter(site=site,category=category).order_by('-type','-ctime')
    if type != -1:
        parts = parts.filter(type=type)
    ctx = {'site':site,'parts':parts,'category':category,'categorys':categorys,'type':type}
    return render(request, template_name, ctx)

@Has_permission('manage_school_website_list')
def announcement_create(request,site_id,template_name="oa/announcement_form.html"):
    schools = get_schools(request.user)
    site = get_object_or_404(WebSite,id=site_id,school__in=schools)
    helpers.set_website_visit(request.user,site)
    category = get_object_or_404(PartCategory,id=9)
    school = get_schools(request.user)[0]
    if request.method == 'POST':
        form = PartForm(request.POST,user=request.user,category=category)
        
        if request.is_ajax():
            return helpers.ajax_validate_form(form)
        
        if form.is_valid():
            part = form.save(commit=False)
            if not form.cleaned_data['creator']:
                part.creator = request.user.teacher
            part.school = school
            part.category = category
            part.site = site
            part.save()
            if part.id:
                messages.success(request, u'已成功创建%s ' % part.category)
                return redirect(reverse('oa_part_con_anc_list',kwargs={'site_id':site.id}))
    else:
        form = PartForm(category=category,user=request.user)
    ctx = {'form':form,'category':category,'site':site}
    return render(request, template_name, ctx)

@Has_permission('manage_school_website_list')
def update_announcement(request,part_id,template_name="oa/announcement_form.html"):
    schools = get_schools(request.user)
    part = get_object_or_404(Part,id=part_id,site__school__in=schools)
    site = part.site
    helpers.set_website_visit(request.user,site)
    category = part.category
    if request.method == 'POST':
        form = PartForm(request.POST,category=category,user=request.user,instance=part)
        
        if request.is_ajax():
            return helpers.ajax_validate_form(form)
        
        if form.is_valid():
            part = form.save(commit=False)
            if not form.cleaned_data['creator']:
                part.creator = request.user.teacher
            part.save()
            if part.id:
                messages.success(request, u'已成功修改%s ' % part.category)
                return redirect(reverse('oa_part_con_anc_list',kwargs={'site_id':site.id}))   
    else:
        form = PartForm(category=category,user=request.user,instance=part)
    ctx = {'form':form,'category':category,'site':site}
    return render(request, template_name, ctx)
 
@Has_permission('manage_school_website_list')
def operate_part_announcements(request):
    schools = get_schools(request.user)
    if request.method == 'POST':
        type = request.POST.get('operate')
        part_pks = request.POST.getlist('part_pks')
        parts = Part.objects.filter(pk__in=part_pks,site__school__in=schools)
        if type == 'delete':
            parts.delete()
        if type == 'top':
            parts.update(type=2)
        if type == 'cancel_top':
            parts.update(type=1)
        site_id = int(request.POST.get('sid'))
        
        if type:
            messages.success(request, u'操作成功')
    return redirect(reverse('oa_part_con_anc_list',kwargs={'site_id':site_id})) 
    
@Has_permission('manage_school_website_list')
def news_list(request,site_id,template_name="oa/news_list.html"):
    schools = get_schools(request.user)
    site = get_object_or_404(WebSite,id=site_id,school__in=schools)
    helpers.set_website_visit(request.user,site)
    category = get_object_or_404(PartCategory,id=10)
    categorys = PartCategory.objects.filter(parent=category.parent)
    parts = Part.objects.filter(site=site,category=category).order_by('-type','-ctime')
    type = int(request.GET.get("ty",-1))
    if type != -1:
        parts = parts.filter(type=type)
    ctx = {'site':site,'parts':parts,'category':category,'categorys':categorys,'type':type}
    return render(request, template_name, ctx)

@Has_permission('manage_school_website_list')
def news_create(request,site_id,template_name="oa/news_form.html"):
    schools = get_schools(request.user)
    site = get_object_or_404(WebSite,id=site_id,school__in=schools)
    helpers.set_website_visit(request.user,site)
    category = get_object_or_404(PartCategory,id=10)
    school = get_schools(request.user)[0]
    if request.method == 'POST':
        form = PartForm(request.POST,category=category,user=request.user)
        
        if request.is_ajax():
            return helpers.ajax_validate_form(form)
        
        if form.is_valid():
            part = form.save(commit=False)
            if not form.cleaned_data['creator']:
                part.creator = request.user.teacher
            part.school = school
            part.category = category
            part.site = site
            part.save()
            if part.id:
                messages.success(request, u'已成功创建%s ' % part.category)
                return redirect(reverse('oa_part_con_news_list',kwargs={'site_id':site.id}))
    else:
        form = PartForm(category=category,user=request.user)
    ctx = {'form':form,'category':category,'site':site}
    return render(request, template_name, ctx)

@Has_permission('manage_school_website_list')
def update_news(request,part_id,template_name="oa/news_form.html"):
    schools = get_schools(request.user)
    part = get_object_or_404(Part,id=part_id,site__school__in=schools)
    site = part.site
    helpers.set_website_visit(request.user,site)
    category = part.category
    if request.method == 'POST':
        form = PartForm(request.POST,category=category,user=request.user,instance=part)
        
        if request.is_ajax():
            return helpers.ajax_validate_form(form)
        
        if form.is_valid():
            part = form.save(commit=False)
            if not form.cleaned_data['creator']:
                part.creator = request.user.teacher
            part.save()
            if part.id:
                messages.success(request, u'已成功修改%s ' % part.category)
                return redirect(reverse('oa_part_con_news_list',kwargs={'site_id':site.id}))  
    else:
        form = PartForm(category=category,user=request.user,instance=part)
    ctx = {'form':form,'category':category,'site':site}
    return render(request, template_name, ctx)
 
@Has_permission('manage_school_website_list') 
def delete_part_news(request):
    schools = get_schools(request.user)
    if request.method == 'POST':
        type = request.POST.get('operate')
        part_pks = request.POST.getlist('part_pks')
        parts = Part.objects.filter(pk__in=part_pks,site__school__in=schools)
        if type == 'delete':
            parts.delete()
        if type == 'top':
            parts.exclude(type=0).update(type=2)
        if type == 'cancel_top':
            parts.exclude(type=0).update(type=1)
        if type:
            messages.success(request, u'操作成功')

        site_id = int(request.POST.get('sid'))
    return redirect(reverse('oa_part_con_news_list',kwargs={'site_id':site_id}))   

def tips_create(request,site_id,template_name="oa/tips_form.html"):
    schools = get_schools(request.user)
    site = get_object_or_404(WebSite,id=site_id,school__in=schools)
    helpers.set_website_visit(request.user,site)
    try:
        category = get_object_or_404(PartCategory,id=11)
    except:
        category = None
    try:
        part = Part.objects.get(site=site,category=category)
    except:
        part =None
    school = get_schools(request.user)[0]
    if request.method == 'POST':
        form = PartForm(request.POST,category=category,user=request.user,instance=part)
        
        if request.is_ajax():
            return helpers.ajax_validate_form(form) 
        
        if form.is_valid():
            part = form.save(commit=False)
            if not form.cleaned_data['creator']:
                part.creator = request.user.teacher
            part.school = school
            part.category = category
            part.site = site
            part.type = 0
            part.save()
            if part.id:
                messages.success(request, u'已成功修改%s ' % part.category)
                return redirect(reverse('oa_part_con_tips_create',kwargs={'site_id':site.id}))
    else:
        form = PartForm(category=category,user=request.user,instance=part)
    ctx = {'form':form,'category':category,'site':site}
    return render(request, template_name, ctx)

@Has_permission('manage_school_website_list')    
def video_list(request,site_id,template_name="oa/video_list.html"):
    schools = get_schools(request.user)
    site = get_object_or_404(WebSite,id=site_id,school__in=schools)
    helpers.set_website_visit(request.user,site)
    category = get_object_or_404(PartCategory,id=12)
    categorys = PartCategory.objects.filter(parent=category.parent)
    parts = Part.objects.filter(site=site,category=category).order_by('-type','-mtime')
    type = int(request.GET.get("ty",-1))
    if type != -1:
        parts = parts.filter(type=type)
    ctx = {'site':site,'parts':parts,'category':category,'categorys':categorys,'type':type}
    return render(request, template_name, ctx)

@Has_permission('manage_school_website_list')
def video_create(request,site_id,template_name="oa/video_form.html"):
    schools = get_schools(request.user)
    site = get_object_or_404(WebSite,id=site_id,school__in=schools)
    helpers.set_website_visit(request.user,site)
    category = get_object_or_404(PartCategory,id=12)
    school = get_schools(request.user)[0]
    if request.method == 'POST':
        chunks = request.POST.get('chunks')
        if chunks:#if request.is_ajax():
            f = request.FILES["video"]
            chunk = int(request.POST.get('chunk'))
            chunks = int(chunks)
            file_id = request.POST.get('file_id')
            name = request.POST.get('name')
            
            file_path = FILE_PATH + '/temp/' + str(file_id)
            fp = open(file_path,"a+b")
            fp.write(f.read())
            fp.close()
            
            if chunk + 1  == chunks:
                filename = 'part/' + str(file_id) + '.' +  name.split('.')[-1].lower()
                try:
                    URL('http://' + SITE_INFO.domain + reverse('cron_make_large_img')).post_async(filename=filename,file_path=file_path)
                except:
                    fr = open(file_path,"rb")
                    content = fr.read()
                    fr.close()
                    if os.path.isfile(file_path):
                        os.remove(file_path)
                    AliyunStorage(). _put_file(filename, content)
                    
                part = Part()
                part.creator = request.user.teacher
                part.school = school
                part.category = category
                part.site = site
                part.video = filename
                part.title = request.POST.get('title',name)
                part.video_type = request.POST.get('video_type') or 0
                part.type = request.POST.get('type') or 0
                part.save()
                if part.id:
                    data = json.dumps({'status':1,'desc':"ok"})
                    return HttpResponse(data)

            else:
                return HttpResponse(json.dumps({'status':1,'desc':"ok"}))
            data = json.dumps({'status':0,'desc':"error"})
            return HttpResponse(data) 
         
            
        else:  
            print 'fffffffffffffffffffff'
            form = PartForm(request.POST,request.FILES,user=request.user,category=category)
            if form.is_valid():
                part = form.save(commit=False)
                if not form.cleaned_data['creator']:
                    part.creator = request.user.teacher
                part.school = school
                part.category = category
                part.site = site
                part.type = form.cleaned_data['type'] or 0
                print part.video,'vvvvvvvvvv'
                part.save()
                if part.id:
                    messages.success(request, u'已成功上传%s ' % part.category)
                    return redirect(reverse('oa_part_con_video_list',kwargs={'site_id':site.id}))
    else:
        form = PartForm(category=category,user=request.user)
    ctx = {'form':form,'category':category,'site':site}
    return render(request, template_name, ctx)

@Has_permission('manage_school_website_list')
def update_video(request,part_id,template_name="oa/video_form.html"):
    schools = get_schools(request.user)
    part = get_object_or_404(Part,id=part_id,site__school__in=schools)
    site = part.site
    helpers.set_website_visit(request.user,site)
    category = part.category
    form = PartForm(category=category,user=request.user,instance=part)
    if request.method == 'POST':
        chunks = request.POST.get('chunks')
        if chunks:#if request.is_ajax():
            f = request.FILES["video"]
            chunk = int(request.POST.get('chunk'))
            chunks = int(chunks)
            file_id = request.POST.get('file_id')
            name = request.POST.get('name')
            
            file_path = FILE_PATH + '/temp/' + str(file_id)
            fp = open(file_path,"a+b")
            fp.write(f.read())
            fp.close()
            
            if chunk + 1  == chunks:
                filename = 'part/' + str(file_id) + '.' +  name.split('.')[-1].lower()

                try:
                    URL('http://' + SITE_INFO.domain + reverse('cron_make_large_img')).post_async(filename=filename,file_path=file_path)
                except:
                    fr = open(file_path,"rb")
                    content = fr.read()
                    fr.close()
                    if os.path.isfile(file_path):
                        os.remove(file_path)
                    AliyunStorage(). _put_file(filename, content)
                    
                part = Part()
                part.creator = request.user.teacher
                part.school = school
                part.category = category
                part.site = site
                part.video = filename
                part.title = request.POST.get('title',name)
                part.video_type = request.POST.get('video_type') or 0
                part.type = request.POST.get('type') or 0
                part.save()
                if part.id:
                    data = json.dumps({'status':1,'desc':"ok"})
                    return HttpResponse(data)

            else:
                return HttpResponse(json.dumps({'status':1,'desc':"ok"}))
            data = json.dumps({'status':0,'desc':"error"})
            return HttpResponse(data) 
        else:
            form = PartForm(request.POST,request.FILES,user=request.user,category=category,instance=part)
            if form.is_valid():
                part = form.save(commit=False)
                if not form.cleaned_data['creator']:
                    part.creator = request.user.teacher
                part.save()           
                if part.id:
                    messages.success(request, u'已成功修改%s ' % part.category)
                    return redirect(reverse('oa_part_con_video_list',kwargs={'site_id':site.id}))   
    else:
        form = PartForm(category=category,user=request.user,instance=part)
    ctx = {'form':form,'category':category,'site':site,'part':part}
    return render(request, template_name, ctx)
 
@Has_permission('manage_school_website_list') 
def delete_part_video(request):
    schools = get_schools(request.user)
    if request.method == 'POST':
        type = request.POST.get('operate')
        part_pks = request.POST.getlist('part_pks')
        parts = Part.objects.filter(pk__in=part_pks,site__school__in=schools)
        if type == 'delete':
            parts.delete()
        if type == 'top':
            parts.exclude(type=0).update(type=2)
        if type == 'cancel_top':
            parts.exclude(type=0).update(type=1)
        if type:
            messages.success(request, u'操作成功')

        site_id = int(request.POST.get('sid'))
    return redirect(reverse('oa_part_con_video_list',kwargs={'site_id':site_id}))

@Has_permission('manage_school_website_list')
def template(request,site_id,template_name="oa/template_list.html"):
    schools = get_schools(request.user)
    site = get_object_or_404(WebSite,id=site_id,school__in=schools)
    helpers.set_website_visit(request.user,site)
    templates = Template.objects.filter(site=site)
    ctx = {'templates':templates,'site':site}
    return render(request, template_name, ctx)

@Has_permission('manage_school_website_list')
def change_template(request,template_id):
    schools = get_schools(request.user)
    template = get_object_or_404(Template,id=template_id,site__school__in=schools)
    site = template.site
    helpers.set_website_visit(request.user,site)
    template.is_show = 1
    template.save()
    ctx = {'template':template,'site':site}
    return redirect(reverse('oa_template_list',kwargs={'site_id':site.id}))

@Has_permission('manage_school_website_list')
def site_admin(request,site_id,template_name="oa/siteadmin_list.html"):
    schools = get_schools(request.user)
    site = get_object_or_404(WebSite,id=site_id,school__in=schools)
    helpers.set_website_visit(request.user,site)
    teachers = Teacher.objects.filter(school=site.school)
    admins = [u for u in site.admins.all()]
    admin_pks = [u.id for u in site.admins.all()]
    print admin_pks,'pppppppppp'
    
    s = int(request.GET.get("status", -1))
    a = int(request.GET.get("active", -1))
    n = request.GET.get("name",'')
    u = request.GET.get("username",'')
    
    qs = Q(postjob__status=s) if s != -1 else Q()
    if a != -1:
        qa = Q(user__in=admins) if a == 0 else ~Q(user__in=admins)
    else:
        qa = Q()
    qn = Q(name__contains=n) if n else Q()
    qu = Q(user__username__contains=u) if u else Q()
    q = qs & qn & qu & qa
    
    teachers = teachers.filter(q)
    
    uid = request.GET.get('uid','')
    ctx = {'teachers':teachers,'site':site,'admins':admins,'admin_pks':admin_pks,'s':s,'a':a,'n':n,'u':u}
#    return render(request, template_name, ctx)
    if request.method == 'POST':
        uid = request.POST.get('uid')
        user = get_object_or_404(User,id=uid)
        if user in admins:
            site.admins.remove(user)
            admin_pks.remove(user.id)
            data = json.dumps({'status':0})
        else:
            site.admins.add(user)
            admin_pks.append(user.id)
            data = json.dumps({'status':1})
        return HttpResponse(data)
    else:
        return render(request, template_name, ctx)

@Has_permission('manage_school_website_list')    
def star_figure_teacher(request,site_id,template_name="oa/start_teacher_list.html"):
    schools = get_schools(request.user)
    site = get_object_or_404(WebSite,id=site_id,school__in=schools)
    helpers.set_website_visit(request.user,site)
    teachers = Teacher.objects.filter(school=site.school,is_delete=False)
    groups = Group.objects.filter(school=site.school).exclude(type=3)
    type = int(request.GET.get("ty",-1))
    gid = int(request.GET.get("group",-1))
    if type != -1:
        if type == 1:
            teachers = teachers.filter(user__figure__is_show=True)
        else:
            teachers = teachers.exclude(user__figure__is_show=True)
    if gid != -1:
        teachers = Teacher.objects.group_teachers(teachers,gid)
    ctx = {'site':site,'teachers':teachers,'type':type,'groups':groups,'gid':gid}
    return render(request, template_name, ctx)

@Has_permission('manage_school_website_list')
def star_figure_student(request,site_id,template_name="oa/start_student_list.html"):
    schools = get_schools(request.user)
    site = get_object_or_404(WebSite,id=site_id,school__in=schools)
    helpers.set_website_visit(request.user,site)
    students = Student.objects.filter(school=site.school)
    groups = Group.objects.filter(school=site.school).exclude(type=3)
    type = int(request.GET.get("ty",-1))
    gid = int(request.GET.get("group",-1))
    if type != -1:
        if type == 1:
            students = students.filter(user__figure__is_show=True)
        else:
            students = students.exclude(user__figure__is_show=True)
    if gid != -1:
        students = students.filter(group_id=gid)
    ctx = {'site':site,'students':students,'type':type,'groups':groups,'gid':gid}
    return render(request, template_name, ctx)

@Has_permission('manage_school_website_list') 
def star_teacher_status(request):
    if request.method == 'POST':
        type = request.POST.get('operate')
        start_pks = request.POST.getlist('start_pks')
        print start_pks,'pppppppppppppppppp'
        figures = StarFigure.objects.filter(pk__in=start_pks)
        if type == 'show':
            figures.update(is_show=True)
        if type == 'hide':
            figures.update(is_show=False)
        if type:
            messages.success(request, u'操作成功')

        site_id = int(request.POST.get('sid'))
    return redirect(reverse('oa_star_figure_teacher',kwargs={'site_id':site_id}))

@Has_permission('manage_school_website_list') 
def star_student_status(request):
    if request.method == 'POST':
        type = request.POST.get('operate')
        start_pks = request.POST.getlist('start_pks')
        figures = StarFigure.objects.filter(pk__in=start_pks)
        if type == 'show':
            figures.update(is_show=True)
        if type == 'hide':
            figures.update(is_show=False)
        if type:
            messages.success(request, u'操作成功')
            
        site_id = int(request.POST.get('sid'))
    return redirect(reverse('oa_star_figure_student',kwargs={'site_id':site_id}))


@Has_permission('manage_school_website_list')
def star_figure_detail(request,site_id,user_id,template_name="oa/start_form.html"):
    user = get_object_or_404(User,id=user_id)
    schools = get_schools(request.user)
    site = get_object_or_404(WebSite,id=site_id,school__in=schools)
    helpers.set_website_visit(request.user,site)
    if is_teacher(user):
        next = reverse('oa_star_figure_teacher',kwargs={'site_id':site_id})
    else:
        next = reverse('oa_star_figure_student',kwargs={'site_id':site_id}) 
    try:
        figure = user.figure
    except:
        figure = StarFigure(user=user).save()
    
    if request.method == 'POST':
      form = StarFigureForm(request.POST,instance=figure)
      
      if request.is_ajax():
            return helpers.ajax_validate_form(form)
        
      if form.is_valid():
          part = form.save()
          messages.success(request, u'已成功修改%s ' % user.profile.realname)
          return redirect(next)
    else:
      form = StarFigureForm(instance=figure)
    ctx = {'form':form,'user':user,'next':next,'site':site}
    return render(request, template_name, ctx)
    
@Has_permission('manage_school_website_list')
def check_website_domain(request):
    domain = request.POST.get("param")
    site_id = request.GET.get("site_id",None)
    return helpers.checked_domain(domain,site_id)
        