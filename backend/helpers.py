# -*- coding: utf-8 -*-
from django.core.exceptions import ObjectDoesNotExist
from django.shortcuts import HttpResponse
from django.utils.translation import ugettext_lazy as _
from django.core.cache import cache
from django.contrib.sites.models import Site
from django.contrib.auth.models import User
from kinger import settings
import datetime
from django.core.mail import send_mail
from django.core.mail import EmailMessage 
from kinger.models import RelevantStaff
import hashlib
from django.contrib.sites.models import Site
from django.core.urlresolvers import reverse
from os import environ

import sys
reload(sys)
sys.setdefaultencoding('utf8') 

SITE_INFO = Site.objects.get_current()

def send_user_cookbook(user,cookbook,content):
    from kinger.models import CookbookRead,Sms
    c = CookbookRead.objects.set_cookbook_unread(user=user,cookbook=cookbook,ty="send")
    if not c:
        return False 
    
    msg = Sms()
    msg.sender_id = cookbook.creator_id
    msg.receiver_id = user.id
    msg.mobile = user.get_profile().mobile
    msg.type_id = 3
    msg.content = content
    msg.save()
    return True
            
def set_cookbook_content(cookbook):       
    content = ""
    if cookbook.breakfast:
        content = content + "早餐【" + cookbook.breakfast + "】"
    if cookbook.light_breakfast:
        content = content + "早点【" + cookbook.light_breakfast + "】"
    if cookbook.lunch:
        content = content + "午餐【" + cookbook.lunch + "】"
    if cookbook.light_lunch:
         content = content + "午点【" + cookbook.light_lunch + "】"
    if cookbook.dinner:
         content = content + "晚餐【" + cookbook.dinner + "】"
    if cookbook.light_dinner:
         content = content + "晚点【" + cookbook.light_dinner + "】"
    if content:
        content = "尊敬的用户，您的孩子的食谱是:" + content
    return content      

def send_staff_mobile(mobile,msg): 
    """发送一条短信"""
    from kinger.models import Sms
    mes = Sms()
    mes.sender_id = 1
    mes.receiver_id = -1
    mes.mobile = mobile
    mes.type_id = 99
    mes.content = msg
    mes.save()
    return True
    

def send_staff_email(email,msg):
    """发送一条email"""
    email_list = []
    email_list.append(email)
    try:
        send_mail(SITE_INFO.name + '未读提醒', msg, settings.EMAIL_HOST_USER, email_list)
        return True
    except:
        return False
    

class StaffTrans:
    """
    发送职员提醒处理
    """
    _msg = False
    
    def __init__(self):
        pass

    def run(self):
        pass

    def kinger_notice_to_staff(self,staff_id,unread_mentors,unread_waiters):
        """
        发送一名职员提醒
        """
        try:
            s = RelevantStaff.objects.get(id=staff_id)
            if s.send_mentor and int(unread_mentors) and s.email:
                msg = "<" + SITE_INFO.name + ">导师留言后台有" + str(unread_mentors) + "条新客户留言. 请及时登录回复. 登录地址: " + SITE_INFO.domain + reverse('aq')
                send_staff_email(s.email,msg)
            if s.send_waiter and int(unread_waiters) and s.email:
                msg = "<" + SITE_INFO.name + ">客服后台有" + str(unread_waiters) + "条新客服留言. 请及时登录回复. 登录地址: " + SITE_INFO.domain + reverse('waiter')
                send_staff_email(s.email,msg)

        except:
            pass
            
def get_pem_file():
    """"""
    islocalhost = not environ.get("APP_NAME","")
    if environ.get("APP_NAME",""):
        try:
            SAE_TEST_APPNAME = settings.SAE_TEST_APPNAME
#            PEM_FILE_NAME = "ck_development.pem"
            PEM_FILE_NAME = "20131127_ck_distribution_1.pem"
        except:
#            PEM_FILE_NAME = "ck_production.pem"
            PEM_FILE_NAME = "20131127_ck_distribution_1.pem"
    else:
#        PEM_FILE_NAME = "ck_development.pem"
        PEM_FILE_NAME = "20131127_ck_distribution_1.pem"
    return PEM_FILE_NAME

