# -*- coding: utf-8 -*-
from django.shortcuts import render_to_response, redirect, render, get_object_or_404
from django.http import Http404
from django.http import HttpResponse
from kinger.models import WebSite,School,Part,PartCategory,Album,Photo
from oa.forms import AlbumForm,PhotoForm,PartForm
from django.contrib import messages
from django.core.urlresolvers import reverse
from oa.helpers import get_schools

def index(request,site_id,template_name="oa/article_list.html"):  
    """精彩文章列表"""
    schools = get_schools(request.user)
    site = get_object_or_404(WebSite,id=site_id,school__in=schools)
    parts = Part.objects.filter(site=site,category_id=19).order_by('-type','-ctime')
    category = get_object_or_404(PartCategory,id=19)
    type = int(request.GET.get("ty",-1))
    if type != -1:
        if type == 1:
            parts = parts.filter(is_show=True)
        else:
            parts = parts.exclude(is_show=True)
    if request.method == 'POST':
        article_pks = request.POST.getlist("part_pks")
        attr = int(request.POST.get('attr',-1))
        if attr != -1:
            artcs = Part.objects.filter(site=site,category_id=19,id__in=article_pks)
            artcs.update(is_show=attr)
            return redirect(reverse('oa_article_list',\
                kwargs={'site_id':site.id}) + '?ty=' + str(type))
    ctx = {'site':site,'parts':parts,'category':category,'type':type}
    return render(request, template_name,ctx)

def article_create(request,site_id,template_name="oa/article_form.html"):
    """添加精彩文章"""
    schools = get_schools(request.user)
    site = get_object_or_404(WebSite,id=site_id,school__in=schools)
    category = get_object_or_404(PartCategory,id=19)
    if request.method == 'POST':
        form = PartForm(request.POST,category=category)
        if form.is_valid():
            part = form.save(commit=False)
            if not form.cleaned_data['creator']:
                part.creator = request.user.teacher
            part.category = category
            part.site = site
            part.save()
            if part.id:
                messages.success(request, u'已成功创建%s ' % part.title)
                return redirect(reverse('oa_article_list',kwargs={'site_id':site.id}))
    else:
        form = PartForm(category=category)
    ctx = {'form':form,'site':site,'category':category}
    return render(request, template_name,ctx)

def article_update(request,article_id,template_name="oa/article_form.html"):
    """更新精彩文章"""
    schools = get_schools(request.user)
    article = get_object_or_404(Part,id=article_id,site__school__in=schools)
    site = article.site
    category = article.category
    if request.method == 'POST':
        form = PartForm(request.POST,instance=article,category=category)
        if form.is_valid():
            part = form.save(commit=False)
            if not form.cleaned_data['creator']:
                part.creator = request.user.teacher
#            part.category = category
#            part.site = site
            part.save()
            if part.id:
                messages.success(request, u'已成功修改%s ' % part.title)
                return redirect(reverse('oa_article_list',kwargs={'site_id':site.id}))
    else:
        form = PartForm(instance=article,category=category)
    ctx = {'form':form,'site':site,'category':category,'article':article}
    return render(request, template_name,ctx)

