# -*- coding: utf-8 -*-
from django.shortcuts import render_to_response, redirect, render, get_object_or_404
from django.http import Http404
from django.http import HttpResponse
from kinger.models import WebSite,School,Part,PartCategory,Album,Photo,Link
from oa.forms import AlbumForm,PhotoForm,PartForm,LinkForm
from django.contrib import messages
from django.core.urlresolvers import reverse
from oa.helpers import get_schools

def index(request,site_id,template_name="oa/link_list.html"):
    """友情链接列表"""  
    schools = get_schools(request.user)
    site = get_object_or_404(WebSite,id=site_id,school__in=schools)
    q = request.GET.get("q",'')
    links = Link.objects.filter(site=site)
    if q:
        links = links.filter(title__contains=q)
    ctx = {'site':site,'links':links,'q':q}
    return render(request, template_name,ctx)

def delete(request,site_id):
    """删除友情链接"""  
    schools = get_schools(request.user)
    site = get_object_or_404(WebSite,id=site_id,school__in=schools)
    if request.method == 'POST':
        link_pks = request.POST.getlist('link_pks')
        links = Link.objects.filter(pk__in=link_pks)
        links.delete()
    return redirect(reverse('oa_link_list',kwargs={'site_id':site_id}))

def create(request,site_id,template_name="oa/link_form.html"):
    """创建友情链接""" 
    site = get_object_or_404(WebSite,id=site_id)
    if request.method == 'POST':
        form = LinkForm(request.POST)
        if form.is_valid():
            link = form.save(commit=False)
            link.site = site
            link.save()
            if link.id:
                messages.success(request, u'已成功创建%s ' % link.title)
                return redirect(reverse('oa_link_list',kwargs={'site_id':site.id}))
    else:
        form = LinkForm()
    ctx = {'form':form,'site':site}
    return render(request, template_name,ctx)
