# -*- coding: utf-8 -*-
from django.shortcuts import render_to_response, redirect, render, get_object_or_404
from django.http import Http404
from django.http import HttpResponse
from kinger.models import WebSite,School,Part,PartCategory,Album,Photo,Link,ChangeUsername,\
                            Teacher,Student,MailBox,Tile,Registration
from oa.forms import AlbumForm,PhotoForm,PartForm,LinkForm,MailBoxForm,RegistrationForm,RegistGuardianForm
from django.contrib import messages
from django.forms.formsets import formset_factory,BaseFormSet
from django.core.urlresolvers import reverse
from django.contrib.auth import authenticate, login, logout, REDIRECT_FIELD_NAME
from userena.forms import (SignupForm, SignupFormOnlyEmail, AuthenticationForm,
                           ChangeEmailForm, EditProfileForm)
from django.utils.translation import ugettext as _
from userena import settings as userena_settings
from oa import helpers
from oa.helpers import is_teacher,get_site
from django.db.models import Q
from captcha.models import CaptchaStore
from captcha.helpers import captcha_image_url
from django.contrib.auth.views import logout

import datetime, time
import md5
from django.contrib import auth
try:
    import simplejson as json
except ImportError:
    import json
   

def index(request,template_name="oa/site/index.html",domain="huaban"): 
    
    parent_domain = helpers.get_parent_domain(request)
    site = get_site(request)
    if not site:
        return render(request, "404.html")
    ctx = {'channel':'site_index'}
    if request.user.is_authenticated():
        ctx.update({'user_login':request.user})
    school = site.school
    auth_form = AuthenticationForm
    if request.method == 'POST':
        form = auth_form(request.POST)
        
        if request.is_ajax():
            return helpers.ajax_validate_error(form)
        
        if form.is_valid():
            identification, password, remember_me = (form.cleaned_data['identification'],
                                                     form.cleaned_data['password'],
                                                     form.cleaned_data['remember_me'])
            user = authenticate(identification=identification,password=password)
            try:
                profile = user.get_profile()
            except:
                p = Profile()
                p.user = user
                p.save()
            if user.is_active:
                login(request, user)
#                 log = Access_log()
#                 log.type = 1
#                 log.user = user
#                 log.url = request.get_full_path()
#                 log.save()
                
                if remember_me:
                    request.session.set_expiry(userena_settings.USERENA_REMEMBER_ME_DAYS[1] * 86400)
                else: request.session.set_expiry(0)
                messages.success(request, _('You have been signed in.'))
                # Whereto now?
                return redirect(request.get_full_path())
            else:
                return redirect(reverse('userena_disabled',
                                        kwargs={'username': user.username}))
    else:
        form = AuthenticationForm()
        
    school_actives = school_active(request,site.id,17)
    student_actives = school_active(request,site.id,18)
    articals = get_parts(request,site.id,19)
    news = get_parts(request,site.id,10)
    print news,'nnnnnnnnnnnnnn'
    announces = get_parts(request,site.id,9)
    tip = get_tip(request,site.id)
    start_teachers = get_start(request,school,'teacher')
    start_students = get_start(request,school,'student')
    tiles = Tile.objects.get_tiles_all_unlogin()[0:4]
    links = Link.objects.filter(site=site)
    ctx.update({'form':form,'school_actives':school_actives,'student_actives':student_actives,\
                'articals':articals,'news':news,'announces':announces,'tip':tip,'links':links,\
                'start_teachers':start_teachers,'start_students':start_students,'tiles':tiles,\
                'site':site,'parent_domain':parent_domain})
    return render(request, template_name,ctx)

def teacher_starts(request,template_name="oa/site/start_teacher.html",domain="huaban"):
    site = get_site(request)
    if not site:
        return render(request, "404.html")
    school = site.school
    starts = Teacher.objects.filter(school=school,user__figure__is_show=True)
    ctx = {'starts':starts,'class':'startes','site':site}
    return render(request, template_name,ctx)

def student_starts(request,template_name="oa/site/start_student.html",domain="huaban"):
    site = get_site(request)
    if not site:
        return render(request, "404.html")
    school = site.school
    starts = Student.objects.filter(school=school,user__figure__is_show=True)
    ctx = {'starts':starts,'class':'startes','site':site}
    return render(request, template_name,ctx)

def introduction(request,template_name="oa/site/intro.html",domain="huaban"):
    site = get_site(request)
    if not site:
        return render(request, "404.html")
    school = site.school
    intro = get_introduction(request,school,site,5)
    appearance = get_introduction(request,school,site,6)
    elegant = get_introduction(request,school,site,7)
    ctx = {'school':school,'intro':intro,'appearance':appearance,'elegant':elegant,\
           'channel':'site_intro','class':'gakenintro','site':site}
    return render(request, template_name,ctx)

def teache(request,template_name="oa/site/teaching.html",domain="huaban"):
    site = get_site(request)
    if not site:
        return render(request, "404.html")
    school = site.school
    teaches = Part.objects.filter(site=site,category_id=4).exclude(type=0).order_by("-type","-ctime")
    ctx = {'teaches':teaches,'site':site,'school':school,\
           'channel':'site_teache','class':'gakenintro','category_id':4}
    return render(request, template_name,ctx)

def announce(request,template_name="oa/site/teaching.html",domain="huaban"):
    site = get_site(request)
    if not site:
        return render(request, "404.html")
    school = site.school
    teaches = Part.objects.filter(site=site,category_id=9).exclude(type=0).order_by("-type","-ctime")
    ctx = {'teaches':teaches,'site':site,'school':school,'channel':'site_announce','class':'gakenintro','site':site,'category_id':9}
    return render(request, template_name,ctx)

def news(request,template_name="oa/site/teaching.html",domain="huaban"):
    site = get_site(request)
    if not site:
        return render(request, "404.html")
    school = site.school
    teaches = Part.objects.filter(site=site,category_id=10).exclude(type=0).order_by("-type","-ctime")
    ctx = {'teaches':teaches,'site':site,'school':school,'class':'gakenintro','category_id':10}
    return render(request, template_name,ctx)

def articals(request,template_name="oa/site/teaching.html",domain="huaban"):
    site = get_site(request)
    if not site:
        return render(request, "404.html")
    school = site.school
    teaches = Part.objects.filter(site=site,category_id=19).exclude(type=0).order_by("-type","-ctime")
    ctx = {'teaches':teaches,'site':site,'school':school,'class':'gakenintro','site':site,'category_id':19}
    return render(request, template_name,ctx)

def part_detail(request,part_id,template_name="oa/site/teaching_content.html",domain="huaban"):
    site = get_site(request)
    part = get_object_or_404(Part,id=part_id)
    ctx = {'part':part,'class':'gakenintro'}
    if part.category_id == 4:
        ctx.update({'channel':'site_teache'})
    part.view_count += 1
    part.save()
    ctx.update({'site':site})
    return render(request, template_name,ctx)

def feature(request,template_name="oa/site/feature.html",domain="huaban"):
    site = get_site(request)
    if not site:
        return render(request, "404.html")
    school = site.school
    features = Part.objects.filter(site=site,category_id=2).exclude(type=0).order_by("-type","-ctime")
    ctx = {'features':features,'site':site,'school':school,\
           'channel':'site_feature','class':'gakenintro','site':site}
    return render(request, template_name,ctx)

def recruit(request,template_name="oa/site/recruit.html",domain="huaban"):
    site = get_site(request)
    if not site:
        return render(request, "404.html")
    school = site.school
    recruits = Part.objects.filter(site=site,category_id=3)
    ctx = {'recruits':recruits,'site':site,'school':school,\
           'channel':'site_recruit','class':'gakenintro'}
    return render(request, template_name,ctx)

def videos(request,template_name="oa/site/video.html",domain="huaban"):
    site = get_site(request)
    if not site:
        return render(request, "404.html")
    school = site.school
    order= request.GET.get('order','date')
    videos = Part.objects.filter(site=site,category_id=12).order_by('-ctime')
    if order == "time":
        videos = videos.order_by('-view_count')
    ctx = {'videos':videos,'site':site,'school':school,'class':'startes','order':order,'page_type':'video'}
    return render(request, template_name,ctx)

def video_detail(request,video_id,template_name="oa/site/video_content.html",domain="huaban"):
    site = get_site(request)
    if not site:
        return render(request, "404.html")
    school = site.school
    videos = Part.objects.filter(site=site,category_id=12).order_by('-ctime')
    video = get_object_or_404(Part,id=video_id)
    video.view_count += 1
    video.save()
    
    ctx = {'video':video,'videos':videos,'class':'startes','site':site,'page_type':'video'}
    return render(request, template_name,ctx)

def mailbox(request,template_name="oa/site/email.html",domain="domain"):
    site = get_site(request)
    if not site:
        return render(request, "404.html")
    school = site.school
    
    if request.GET.get('newsn')=='1':
        csn=CaptchaStore.generate_key()
        cimageurl= captcha_image_url(csn)
        parent_domain = helpers.get_parent_domain(request)
        return HttpResponse(parent_domain + cimageurl)
    
    if request.method == 'POST':
        form = MailBoxForm(request.POST)
        print form.errors,'eeeeeeeeeeeeeeeeeee'
        if request.is_ajax():
            return helpers.ajax_validate_form(form)
        
        if form.is_valid():
            human = True
            mail = form.save(commit=False)
#            mail.user = school.header
            mail.site = site
            mail.save()
            if mail.id:
                messages.success(request, u'已成功发送%s ' % mail.title)
                return redirect(request.get_full_path())
    else:
        form = MailBoxForm()
    ctx = {'form':form,'class':'startes','site':site}
    return render(request, template_name, ctx)

def album(request,template_name="oa/site/active.html",domain="huaban"):
    site = get_site(request)
    if not site:
        return render(request, "404.html")
    cty = int(request.GET.get("cty"))
    albums = Album.objects.filter(site=site,category_id=cty).order_by('-ctime')
    ctx = {'albums':albums,'class':'startes','cty':cty,'site':site}
    return render(request, template_name, ctx)

def album_photo(request,photo_id,template_name="oa/site/active_con.html",domain="huaban"):
    site = get_site(request)
    photo = get_object_or_404(Photo,id=photo_id)
    album = photo.album
    photos = Photo.objects.filter(album=album) 
    ctx = {'photo':photo,'album':album,'photos':photos,'class':'startes','site':site}
    return render(request, template_name, ctx)

def album_photos(request,album_id,template_name="oa/site/active_con.html",domain="huaban"):
    site = get_site(request)
    album = get_object_or_404(Album,id=album_id)
    photos = Photo.objects.filter(album=album) 
    ctx = {'album':album,'photos':photos,'class':'startes','site':site}
    return render(request, template_name, ctx)

class RequiredFormSet(BaseFormSet):
    def __init__(self, *args, **kwargs):
        super(RequiredFormSet, self).__init__(*args, **kwargs)

        for form in self.forms:
            form.empty_permitted = True
        self.forms[0].empty_permitted = False
            
def regist(request,template_name="oa/site/registration.html",domain="huaban"):
    ctx = {'channel':'site_regist'}
    site = get_site(request)
    if not site:
        return render(request, "404.html")
    school = site.school
    
    extra = int(request.GET.get("extra", 4))
    if request.GET.get('newsn')=='1':
        csn=CaptchaStore.generate_key()
        cimageurl= captcha_image_url(csn)
        parent_domain = helpers.get_parent_domain(request)
        return HttpResponse(parent_domain + cimageurl)
    
    if request.method == 'POST':
        form1 = RegistrationForm(request.POST)
        extra = request.POST['form-TOTAL_FORMS']
        formset = formset_factory(RegistGuardianForm,formset=RequiredFormSet,extra=extra)
        form2 = formset(request.POST)
        print form1.errors,'11111'
        print form2[0].errors,'222222222'
        print form2[0].is_valid(),'vvvvv'
        
        if request.is_ajax():
            form2_error_list = []
            for fo in form2:
                form2_error_list = form2_error_list + fo.errors.items()
            error_list = form1.errors.items() + form2_error_list
            return helpers.ajax_validate_form_error_list(error_list)
        
        if form1.is_valid() and form2[0].is_valid():
            human = True
            reg = form1.save(commit=False)
            reg.school = school
            reg.status = 0
            reg.save()
            for f in form2:
                print f.errors
                if f.is_valid():
                    guardian = f.save(commit=False)
                    if guardian.relation and guardian.name and guardian.mobile and guardian.unit:
                        guardian.regist = reg
                        guardian.save()
            messages.success(request, u"报名表%s 保存成功" % reg.name)
            return redirect(request.get_full_path())
    else:
        form1 = RegistrationForm()
        form2 = formset_factory(RegistGuardianForm,formset=RequiredFormSet,extra=extra)
    ctx = {'form1':form1,'form2':form2,'class':'startes','site':site}
    return render(request, template_name, ctx)

def school_active(request,site_id,cty):
    """学园活动，幼儿作品"""
    site = get_object_or_404(WebSite,id=site_id)
    albums = Album.objects.filter(site=site,category_id=cty)
    photos = Photo.objects.filter(album__in=albums,is_show=True)
    return photos

def get_parts(request,site_id,cty):
    """精彩文章，新闻动态，公告通知"""
    site = get_object_or_404(WebSite,id=site_id)
    parts = Part.objects.filter(site=site,category_id=cty,is_show=True).exclude(type=0).order_by("-type","-ctime")
    return parts

def get_tip(request,site_id):
    site = get_object_or_404(WebSite,id=site_id)
    parts = Part.objects.filter(site=site,category_id=11).order_by("-ctime")
    if parts.count():
        return parts[0]
    else:
        return None

def get_start(request,school,ty):
    if ty == 'teacher':
        starts = Teacher.objects.filter(school=school,user__figure__is_show=True)
    else:
        starts = Student.objects.filter(school=school,user__figure__is_show=True)
    return starts

def get_introduction(request,school,site,cty):
    try:
        intro = Part.objects.filter(school=school,site=site,category_id=cty).order_by('-mtime')[0]
    except:
        intro = None
    return intro

def ajax_login(request,domain="domain"): 
    username = request.POST.get('username','')
    password = request.POST.get('password','')
    user = auth.authenticate(username=username, password=password)
    user_id = user.id if user else ''
    salt = time.time()
    mask = '3n7j6m9s'
    m = md5.new(str(user_id) + str(salt) + mask)
    hash = m.hexdigest()
    data = {'uid':user_id,'salt':str(salt),'hash':hash}
    return HttpResponse(json.dumps(data))

def ajax_logout(request,domain="domain"):
    user = request.user
    user_id = user.id if user else ''
    salt = time.time()
    mask = '0q2o4f6s'
    m = md5.new(str(user_id) + str(salt) + mask)
    hash = m.hexdigest()
    try:
        logout(request)
        status = True
    except:
        status = False
    data = {'uid':user_id,'salt':str(salt),'hash':hash,'status':status}
    return HttpResponse(json.dumps(data))
