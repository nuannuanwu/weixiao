# -*- coding: utf-8 -*-
from django.shortcuts import render_to_response, redirect, render, get_object_or_404
from django.http import Http404
from django.http import HttpResponse
from kinger.models import WebSite,School,Part,PartCategory,Album,Photo
from oa.forms import AlbumForm,PhotoForm
from django.contrib import messages
from django.core.urlresolvers import reverse
from kinger.helpers import ajax_error,ajax_ok
from oa.helpers import get_schools
from oa.decorators import Has_permission
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

def school_albums(request,site_id,template_name="oa/school_albums_list.html"):
    """学园相册列表"""
    schools = get_schools(request.user)
    site = get_object_or_404(WebSite,id=site_id,school__in=schools)
    category_id = request.GET.get('cid',17)
    albums = Album.objects.filter(site=site,category_id=category_id).order_by('-mtime')
    category = get_object_or_404(PartCategory,id=category_id)
    form = AlbumForm()
    ctx = {'site':site,'albums':albums,'form':form,'category':category}
    return render(request, template_name,ctx)

def album_create(request,site_id):
    """创建相册"""
    schools = get_schools(request.user)
    site = get_object_or_404(WebSite,id=site_id,school__in=schools)
    if request.method == 'POST':
        form = AlbumForm(request.POST)
        if form.is_valid():
            category_id = int(request.POST.get('category',0))
            category = get_object_or_404(PartCategory,id=category_id)
            album = form.save(commit=False)
            album.creator = request.user
            album.category = category
            album.site = site
            album.save()
            if album.id:
                messages.success(request, u'已成功创建相册%s ' % album.name)
    return redirect(reverse('oa_album_school_list',kwargs={'site_id':site.id}) + "?cid=" + str(category_id))

def album_update(request,album_id):
    """修改相册名"""
    schools = get_schools(request.user)
    album = get_object_or_404(Album,id=album_id,site__school__in=schools)
    if request.method == 'POST':
        form = AlbumForm(request.POST,instance=album)
        if form.is_valid():
            form.save()
            messages.success(request, u'已成功修改相册')
    return redirect(reverse('oa_album_detail',kwargs={'album_id':album.id}))

def album_detail(request,album_id,template_name="oa/school_albums_detail.html"):
    """相册详情"""
    schools = get_schools(request.user)
    album = get_object_or_404(Album,id=album_id,site__school__in=schools)
    form1 = AlbumForm(instance=album)
    form2 = PhotoForm()
    site = album.site
    photos = Photo.objects.filter(album=album)
    type = int(request.GET.get('ty',-1))
    if type != -1:
        photos = photos.filter(is_show=type)
    ctx = {'site':site,'photos':photos,'album':album,'type':type,'form1':form1,'form2':form2}
    return render(request, template_name,ctx)

def delete_album(request,site_id):
    """删除相册"""
    if request.method == 'POST':
        schools = get_schools(request.user)
        album_pks = request.POST.getlist('album_pks')
        albums = Album.objects.filter(pk__in=album_pks,site__school__in=schools)
        try:
            category_id = albums[0].category_id
        except:
            category_id = 17
        albums.delete()
    return redirect(reverse('oa_album_school_list',kwargs={'site_id':site_id}) + "?cid=" + str(category_id))

def upload_photo(request,album_id):
    """上传照片"""
    schools = get_schools(request.user)
    album = Album.objects.get(pk=album_id,site__school__in=schools)
    if request.method == 'POST':
        f = request.FILES["img"]
        chunks = int(request.POST.get('chunks'))
        if chunks == 1:
            form = PhotoForm(request.POST,request.FILES)
            if form.is_valid():
                photo = Photo()
                photo.img = f
                photo.creator = request.user
                photo.album = album
                photo.is_show = True
                photo.save()
                if photo.id:
                    data = json.dumps({'status':1,'desc':"ok"})
                    return HttpResponse(data)
        else:
            chunk = int(request.POST.get('chunk'))
            file_id = request.POST.get('file_id')
            name = request.POST.get('name')
            
            file_path = FILE_PATH + '/temp/' + str(file_id)
            print file_path,'ppppppppppppppppppppp'
            fp = open(file_path,"a+b")
            fp.write(f.read())
            fp.close()
            
            if chunk + 1  == chunks:
                filename = 'photo/' + str(file_id) + '.' +  name.split('.')[-1].lower()
                try:
                    URL('http://' + SITE_INFO.domain + reverse('cron_make_large_img')).post_async(filename=filename,file_path=file_path)
                except:
                    fr = open(file_path,"rb")
                    content = fr.read()
                    fr.close()
                    if os.path.isfile(file_path):
                        os.remove(file_path)
                    AliyunStorage(). _put_file(filename, content)
                    
                photo = Photo()
                photo.img = filename
                photo.creator = request.user
                photo.album = album
                photo.is_show = True
                photo.save()
                data = json.dumps({'status':1,'desc':"ok"})
                return HttpResponse(data)

            else:
                return HttpResponse(json.dumps({'status':1,'desc':"ok"}))
            data = json.dumps({'status':0,'desc':"error"})
            return HttpResponse(data) 
    return redirect(reverse('oa_album_detail',kwargs={'album_id':album.id}))

def update_photo(request,photo_id):
    """更新相片"""
    schools = get_schools(request.user)
    photo = get_object_or_404(Photo,id=photo_id,album__site__school__in=schools)
    if request.method == 'POST':
        form = PhotoForm(request.POST,instance=photo)
        if form.is_valid():
            form.save()
            messages.success(request, u'修改成功')
    return redirect(reverse('oa_album_detail',kwargs={'album_id':photo.album_id}))

def show_photo(request,album_id):
    """设置照片显示状态"""
    if request.method == 'POST':
        photo_pks = request.POST.getlist('photo_pks')
        is_show = int(request.POST.get('attr'))
        if is_show != -1:
            schools = get_schools(request.user)
            photos = Photo.objects.filter(pk__in=photo_pks,album__site__school__in=schools)
            if is_show == 2:
                photos.delete()
            else:
                photos.update(is_show=is_show)
    return redirect(reverse('oa_album_detail',kwargs={'album_id':album_id}))

def photo_detail(request,template_name="oa/school_photo_detail.html"):
    """照片详情"""
    photo_id = int(request.POST.get('photo_id'))
    schools = get_schools(request.user)
    photo = get_object_or_404(Photo,id=photo_id,album__site__school__in=schools)
    form = PhotoForm(instance=photo)
    album = photo.album
    ctx = {'album':album,'form':form,'photo':photo}
    data = render(request, template_name,ctx) 
    con=data.content
    return ajax_ok('成功',con)

