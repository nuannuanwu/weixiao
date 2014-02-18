# -*- coding: utf-8 -*-

from django.utils.translation import ugettext as _
from django.shortcuts import redirect, render, get_object_or_404

from kinger.models import VerifySms,Sms
from django.db.models import Q
from django.contrib.contenttypes.models import ContentType
from kinger import helpers
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from kinger.forms import MobileForm, PwdResetForm, PwdMobileForm
from kinger.profiles.models import Profile
from django.contrib.auth import views as auth_views
from django.contrib.sites.models import get_current_site
import random
from django.contrib import messages
from kinger.helper import verify_sms_helper

def pwd_back_mail(request, template_name="kinger/pwd_back/pwd_back_mail_a.html"):
    """
    通过邮箱找回密码页
    """

    request.session['pwd_back_mail'] = {
        'mail':request.POST.get('email')
    }

    post_reset_redirect = reverse('kinger_pwd_back_mail_done')

    return auth_views.password_reset(request, template_name="kinger/pwd_back/pwd_back_mail_a.html",\
     email_template_name='kinger/pwd_back/password_reset_message.txt',post_reset_redirect=post_reset_redirect,\
     extra_context={'mail':True})

def pwd_back_mail_done(request, template_name="kinger/pwd_back/pwd_back_mail_done.html"):
    """
    邮箱成功页
    """
  
    pwd_back_mail = request.session.get('pwd_back_mail')
    mail = ''

    if pwd_back_mail:
        mail = pwd_back_mail.get('mail')
        request.session.pop('pwd_back_mail')

    ctx = {
        'email':mail,
        'mail':True
    }
    return render(request, template_name, ctx)

def pwd_back_mail_reset(request,uidb36=None,token=None, \
    template_name='kinger/pwd_back/pwd_back_reset_mail.html'):
    """
    邮箱密码重置页
    """
    post_reset_redirect = reverse('kinger_pwd_back_success') + "?type=mail"
    return auth_views.password_reset_confirm(request,uidb36=uidb36, token=token, template_name=template_name,\
     post_reset_redirect=post_reset_redirect,
     extra_context={'mail':True})   

def pwd_back_mobile_get_vcode(request):
    """
    得到用户手机号码，并生成验证码
    """

    mobile = request.GET.get('mobile')   
    if mobile:
        message, code, extra = verify_sms_helper.get_vcode(mobile)
        return helpers.ajax_ok(message,con=extra,code=code)        

    return helpers.ajax_error('请先填写你的手机号码。', code=100)

def pwd_back_mobile(request, template_name="kinger/pwd_back/pwd_back_mobile_a.html"):
    """
    通过手机找回密码处理页面，单击下一步
    """
    print 2222
    if request.method == 'POST':
        print 333
        form = PwdMobileForm(request.POST) 
        if form.is_valid():
            mobile = form.cleaned_data['mobile']
            print mobile,'mobile'
            user = verify_sms_helper.get_user_from_mobile(mobile)
            VerifySms.objects.set_vcode_invalid(user)
            print 1111111111
            request.session['pwd_back'] = {
                'type':'mobile',
                'step':{                            
                    'turn':1,
                    'finish':True
                },
                'con':{
                    'user':user,
                    'mobile':mobile
                }
            }
            
            messages.success(request,'身份验证成功，请重置密码')
            return redirect('kinger_pwd_back_pwd_reset')
           
    else:
        form = PwdMobileForm()

    ctx = {
        'form':form,
        'mobile':True
    }
    return render(request, template_name, ctx)

def pwd_back_pwd_reset(request, template_name="kinger/pwd_back/pwd_back_reset.html"):
    """
    密码重置，mobile
    """
    s = request.session.get('pwd_back')

    if not s:
        return redirect('kinger_pwd_back_mobile')

    if s.get('step').get('turn') == 1 and s.get('step').get('finish') == True:
        user = s['con']['user']
        mobile = s['con']['mobile']
        back_type = s.get('type','mail')

    # 密码重置        
    if request.method == 'POST': 
        form = PwdResetForm(request.POST) 
        if form.is_valid():
            # 判断密码           
            pwd = form.cleaned_data['pwd']
            
            user.set_password(pwd)
            user.save()
           
            request.session.pop('pwd_back')                       
            
            url = reverse('kinger_pwd_back_success') + "?type=mobile"

            return redirect(url)
    else:
        form = PwdResetForm() # An unbound form

    ctx = {         
        'form':form,
        back_type:True
    }
       
    return render(request, template_name, ctx)

def pwd_back_success(request, template_name="kinger/pwd_back/pwd_back_success.html"):
    """
    密码设置成功跳转。 mail，mobile 通用
    """

    back_type = request.GET.get('type','mail')    
    ctx = {
        back_type:True
    }
    return render(request, template_name, ctx)

