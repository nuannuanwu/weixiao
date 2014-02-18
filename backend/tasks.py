# -*- coding: utf-8 -*-

from django.http import HttpResponse
from kinger.models import Mentor,ApplePushNotification,Device,Tile,Sms,Cookbook,CookbookRead,Student,Access_log,RelevantStaff
from sms.models import SmsSend, SmsSendAccount
from django.contrib.auth.models import User
from sms.models import SmsNotifyStatus,SmsReceipt,SmsReceive,SmsPort2mobile,SmsReplay
from userena.contrib.umessages.models import Message, MessageRecipient, MessageContact
from backend import helpers
from aq.views.default import get_unread_mentor_count as unread_mentor
from waiter.views.default import get_unread_waiter_count as unread_waiter

from kinger.settings import DATABASES,FILE_PATH
import os
import os.path,time,datetime
from APNSWrapper import *
import binascii
import MySQLdb
from sms.lib.trans import SmsTrans, SmsSendTrans
from django.core.urlresolvers import reverse
from django.contrib.sites.models import Site
from backend import queue
from celery.decorators import task
from anyjson import serialize
from celery.task.http import URL
import base64

import sys 
reload(sys) 
sys.setdefaultencoding('utf8')

SITE_INFO = Site.objects.get_current()

class Apns:

    def __init__(self, cert_id = None, body = None, force_ssl_command = False, debug_ssl = False):
        pass

    def push(self,body,token):

        aps = body.get('aps')
        alert = aps.get('alert')
        badge = aps.get('badge',1)
        sound = aps.get('sound','default')
        data = {"alert":alert,"badge":badge,"sound":sound,"token":token}

        try:
#            res = URL('http://' + SITE_INFO.domain + reverse('cron_push_tile')).post_async(alert=alert,badge=badge,sound=sound,token=token)
##            queue.apns.delay(data)
#        except:
            alert = alert.encode('utf-8')
            wrapper = APNSNotificationWrapper(helpers.get_pem_file())
            wrapper.sandbox = False
            message = APNSNotification()
            deviceToken = binascii.unhexlify(token)
            message.token(deviceToken)
            message.alert(alert)
            message.badge(int(badge))
            message.sound(sound)
            wrapper.append(message)
            rs = wrapper.notify()   
        except:         
            pass

@task
def push_tile(template_name="default/index.html"): 
    count = 0
    now = datetime.datetime.now()
    notification_list = ApplePushNotification.objects.filter(is_send=0, send_time__lt=now).all()[0:1000]
    if notification_list:
        deviceToken_list = Device.objects.all()

        for n in notification_list:
            aps = {"alert":n.alert,"badge":n.badge,"sound":n.sound}

            alert = n.alert.encode('utf-8')

            for d in deviceToken_list:
                deviceToken = d.token.encode('utf-8')
                data = {"aps":aps,"token":deviceToken}
                count = count + 1
#                Apns.push(data, deviceToken)
                Apns().push(data, deviceToken)
            n.is_send = 1
            n.save()

    result = "push_tile:"+str(count)
    return result

from django.db import connection
@task
def push_unread_message(): 
    count = 0
    start_time = datetime.datetime.now() + datetime.timedelta(seconds = -300)
    send_time = datetime.datetime.now()
#    sql = "select a.id,a.user_id,a.message_id,b.token from umessages_messagerecipient a  left join kinger_device b on a.user_id = b.user_id  left join umessages_message c on a.message_id = c.id where c.sent_at<='" + str(send_time) + "' and a.no_need_send=0 and a.is_push =0 and a.read_at is null and a.deleted_at is null and b.token is not null limit 0,1000"
    sql = "select a.id,a.user_id,a.message_id,b.token from umessages_messagerecipient a  left join kinger_device b on a.user_id = b.user_id  left join umessages_message c on a.message_id = c.id where c.sent_at>'" + str(start_time) + "' and c.is_send=1 and c.sent_at<='" + str(send_time) + "' and a.is_push =0 and a.read_at is null and a.deleted_at is null and b.token is not null limit 0,1000"
    cursor = connection.cursor()
    cursor.execute(sql)
    unread_message_list = cursor.fetchall()

#     apns = Apns()
#     if unread_message_list:
#         for n in unread_message_list:
#             device_token = n[3]
#             message_id = n[2]
#             mr_id = n[0]
# 
#             m = Message.objects.get(id=message_id)
#             sender_name = m.sender.get_profile().chinese_name() or m.sender.username
#             try:
#                 sender_name = m.sender.get_profile().chinese_name() or m.sender.username
#                 alert = sender_name+":"+m.body
#                 body = {"aps":{"alert":alert}}
#                 result = apns.push( body , device_token )
# 
#                 mr = MessageRecipient.objects.get(id=mr_id)
#                 mr.is_push = 1
#                 mr.save()
#             except:
#                 pass
# 
# 
#             count = count +1
    ect = {}
    apns = Apns()
    if unread_message_list:
        token_list = [t[3] for t in unread_message_list]
    
        token_list = list(set(token_list))
        for m in token_list:
            ect.update({m:0})
        for n in unread_message_list:
            device_token = n[3]
            mr_id = n[0]
            ect[device_token] += 1
        
            try:
                mr = MessageRecipient.objects.get(id=mr_id)
                mr.is_push = 1
                mr.save()
            except:
                pass

        for k,v in ect.items():
            try:
                alert = "您有" + str(v) + "条未读消息"
                body = {"aps":{"alert":alert}}
                result = apns.push( body , k )
            except:
                pass
        count = len(token_list)

    result = "push_unread_message:"+str(count)
    return result


#发送未读消息
@task
def send_unread_message(): 
    print 'send_unread_message-------------------------'
    count = 0
    time_start = datetime.datetime.now() + datetime.timedelta(weeks = -1)
#    time_end = datetime.datetime.now() + datetime.timedelta(seconds = -1800)
    time_end = datetime.datetime.now() + datetime.timedelta(seconds = -10)
    sql = "select a.id,a.user_id,a.message_id,c.sender_id,c.body from umessages_messagerecipient a  left join umessages_message c on a.message_id = c.id where c.sent_at>'" + str(time_start) + "' and c.sent_at<'" + str(time_end) + "' and c.is_send=1 and a.no_need_send=0 and a.is_send =0 and a.read_at is null limit 0,1000"
    
    cursor = connection.cursor()
    cursor.execute(sql)
    desc = cursor.description
    unread_list = [dict(zip([col[0] for col in desc], row)) for row in cursor.fetchall()]
    for m in unread_list:
        msg = Sms()
        msg.sender_id = m['sender_id']
        msg.receiver_id = m['user_id']
        msg.mobile = User.objects.get(pk=m['user_id']).get_profile().mobile
        msg.type_id = 2
        msg.content = str(m['body']) + '/' + str(User.objects.get(pk=m['sender_id']).get_profile().chinese_name_or_username()) 
        msg.save()
        
        unread = MessageRecipient.objects.get(pk=m['id'])
        unread.is_send = 1
        unread.save()
        count = count + 1
    result = "send_unread_message:"+str(count)
    print result,'rrrrrrrrrrr--------------------------------------'
    return result


#发送定时消息
@task
def send_timing_message(): 
    print 'send_timing_message-------------------'
    count = 0
    now = datetime.datetime.now()
    try:
        messages = Message.objects.filter(is_send=False,timing__isnull=False,timing__lte=now)
    except:
        messages = []
    for m in messages:
        m.is_send = True
        m.sent_at = m.timing
        m.save()
        count = count + 1
    result = "send_timing_message:"+str(count)
    print result,'rrrrrrrrrrr--------------------------------------'
    return result


#发送紧急通知
@task
def send_emergency_message(): 
    print 'send_emergency_message------------------------------'
    count = 0
    time_start = datetime.datetime.now() + datetime.timedelta(weeks = -1)
    time_end = datetime.datetime.now() + datetime.timedelta(seconds = -300)
    sql = "select a.id,a.user_id,a.message_id,c.sender_id,c.body from umessages_messagerecipient a  left join umessages_message c on a.message_id = c.id where c.type=1 and c.sent_at>'" + str(time_start) + "' and c.sent_at<'" + str(time_end) + "' and a.no_need_send=0 and a.is_send =0 and a.read_at is null limit 0,1000"
    
    cursor = connection.cursor()
    cursor.execute(sql)
    desc = cursor.description
    unread_list = [dict(zip([col[0] for col in desc], row)) for row in cursor.fetchall()]
    for m in unread_list:
        try:
            msg = Sms()
            msg.sender_id = m['sender_id']
            msg.receiver_id = m['user_id']
            msg.mobile = User.objects.get(pk=m['user_id']).get_profile().mobile
            msg.type_id = 5
            msg.content = str(m['body']) + '/' + str(User.objects.get(pk=m['sender_id']).get_profile().chinese_name_or_username())
            msg.save()
            
            unread = MessageRecipient.objects.get(pk=m['id'])
            unread.is_send = 1
            unread.save()
            count = count + 1
        except:
            pass
    result = "send_emergency_message:"+str(count)
    print result,'rrrrrrrrrrr--------------------------------------'
    return result


#发送紧急通知
@task
def send_emergency_message_unlogin(): 
    print 'send_emergency_message_unlogin---------------'
    count = 0
    time_start = datetime.datetime.now() + datetime.timedelta(weeks = -1)
    time_end = datetime.datetime.now()
    sql = "select a.id,a.user_id,a.message_id,c.sender_id,c.body from umessages_messagerecipient a  left join umessages_message c on a.message_id = c.id where c.type=1 and c.sent_at>'" + str(time_start) + "' and c.sent_at<'" + str(time_end) + "' and a.no_need_send=0 and a.is_send =0 and a.read_at is null limit 0,1000"
    
    cursor = connection.cursor()
    cursor.execute(sql)
    desc = cursor.description
    unread_list = [dict(zip([col[0] for col in desc], row)) for row in cursor.fetchall()]
    for m in unread_list:
        try:
            user = User.objects.get(pk=m['user_id'])
            times = Access_log.objects.filter(user=user).count()
            if times == 0:
                msg = Sms()
                msg.sender_id = m['sender_id']
                msg.receiver_id = m['user_id']
                msg.mobile = User.objects.get(pk=m['user_id']).get_profile().mobile
                msg.type_id = 5
                msg.content = str(m['body']) + '/' + str(User.objects.get(pk=m['sender_id']).get_profile().chinese_name_or_username())
                msg.save()
                
                unread = MessageRecipient.objects.get(pk=m['id'])
                unread.is_send = 1
                unread.save()
                count = count + 1 
        except:
            pass
        
    result = "send_emergency_message:"+str(count)
    print result,'rrrrrrrrrrr--------------------------------------'
    return result


#发送未读导师及客服提醒
@task
def send_staff_unread(): 
    
    time_limit = datetime.datetime.now() + datetime.timedelta(seconds = -1800)
    has_send = Sms.objects.filter(type_id=99,send_time__gt=time_limit).count()
    if has_send:
        print '30分钟内已发送过短信'
        return '30分钟内已发送过短信'
    unread_mentors = unread_mentor()
    unread_waiters = unread_waiter()
    print unread_mentors,unread_waiters,'unread_mentors,unread_waiters---------'
    if not unread_mentors and not unread_waiters:
        return HttpResponse("")
    
    staffs = RelevantStaff.objects.exclude(send_mentor=False,send_waiter=False)
    
    for s in staffs:
        #发送短信,已有队列
        if s.send_mentor and unread_mentors and s.mobile:
            print 'send_mentor-----------------------------'
            msg = "<" + SITE_INFO.name + ">导师留言后台有" + str(unread_mentors) + "条新客户留言. 请及时登录回复. 登录地址: " + SITE_INFO.domain + reverse('aq')
            helpers.send_staff_mobile(s.mobile,msg)
        if s.send_waiter and unread_waiters and s.mobile:
            print 'send_waiter------------------------------'
            msg = "<" + SITE_INFO.name + ">客服后台有" + str(unread_waiters) + "条新客服留言. 请及时登录回复. 登录地址: " + SITE_INFO.domain + reverse('waiter')
            helpers.send_staff_mobile(s.mobile,msg)
             
    for s in staffs: 
        #发送邮件队列   
        data = {"staff_id":s.id,"unread_mentors":unread_mentors,"unread_waiters":unread_waiters}
        #执行转换
        try:
            res = URL('http://' + SITE_INFO.domain + reverse('cron_push_notice_staff')).post_async(staff_id=s.id,unread_mentors=unread_mentors,unread_waiters=unread_waiters)
#            queue.notice2staff.delay(data)
        except:
            st = helpers.StaffTrans()
            st.kinger_notice_to_staff(s.id,unread_mentors,unread_waiters)
    return ''


#发送未读食谱
@task
def send_unread_cookbook(): 
    count = 0
    time_limit = datetime.datetime.now() + datetime.timedelta(seconds = -1800)
    has_send = Sms.objects.filter(type_id=3,send_time__gt=time_limit).count()
    if has_send:
        print '30分钟内已发送过短信'
        return '30分钟内已发送过短信'
    c_day = datetime.datetime.now() + datetime.timedelta(days = 1)
    date = c_day.date()
    cookbooks = Cookbook.objects.filter(date=date,is_send=False).exclude(breakfast='',light_breakfast='',
                lunch='',light_lunch='',dinner='',light_dinner='')
    
    school_cookbooks = cookbooks.filter(school__isnull=False)
    group_cookbooks = cookbooks.filter(group__isnull=False)
    group_pks = []
    if group_cookbooks:
        for gc in group_cookbooks:
            content = helpers.set_cookbook_content(gc)
            g_user = [s.user for s in gc.get_student()]
            group_pks.append(gc.group_id)
            for gu in g_user:
                if helpers.send_user_cookbook(gu,gc,content):
                    count = count + 1
                    
            gc.is_send = True
            gc.save()
                
    if school_cookbooks: 
        for sc in school_cookbooks:
            school_user =[]
            content = helpers.set_cookbook_content(sc)
            students = Student.objects.filter(school_id=sc.school_id).exclude(group_id__in=group_pks)
            school_user = [s.user for s in students]

            for su in school_user:
                if helpers.send_user_cookbook(su,sc,content):
                    count = count + 1
            
            sc.is_send = True
            sc.save()
            
    result = "send_unread_cookbook:"+str(count)
    return result

#给7天未登录，且有未读瓦片的用户发送短信
@task
def send_user_message(): 
    count = 0
    time_limit = datetime.datetime.now() + datetime.timedelta(weeks = -1)
    users = [s.user for s in Student.objects.all() if s.user.get_profile().last_access_time() < time_limit]
    for user in users:
        has_send = Sms.objects.filter(type_id=98,send_time__gt=time_limit,receiver_id=user.id).count()
        if not has_send:
            unread_count = Tile.objects.count_unread_tiles_for(user)
            if unread_count:
                msg = Sms()
                msg.sender_id = 1
                msg.receiver_id = user.id
                msg.mobile = user.get_profile().mobile
                msg.type_id = 98
                msg.content = "您有" + str(unread_count) + "条新内容未查看，您可以登陆网站或者安装客户端来查看，详情请登录" + str(SITE_INFO.domain) + "[" + str(SITE_INFO.name) + "]"
                msg.save()
                count = count + 1
            
    result = "send_user_message:"+str(count)
    return result
 
@task  
def push_unread_tile(): 
    all_count = count = 0
    apns = Apns()
    deviceToken_list = Device.objects.all()

    for d in deviceToken_list:
        all_count +=1
        device_token = d.token.encode('utf-8')
        try:
            sender_name = d.user.get_profile().chinese_name() or d.user.username
        except:
            sender_name = d.user_id
            pass

        try:
            tile_count = Tile.objects.count_unread_tiles_for(d.user)
            alert = "亲爱的用户，"+sender_name+"，有"+str(tile_count)+"条推送信息。"
            print alert
        except:
            pass

        try:
            body = {"aps":{"alert":alert,"badge":1,"sound":''}}
            if tile_count > 0:
                result = apns.push( body , device_token )
                count = count +1
            else:
                print sender_name+"没有新消息"
        except:
            pass      

    result = str(all_count)+"device.total push tile:"+str(count)
    return result

@task
def sms2send(): 
    """
    转换并发送
    """
    convert_count = 0
    send_count = 0    

    now = datetime.datetime.now()

    k_sms_list = Sms.objects.not_send_yet_sms()[0:1000]

    # def get_test_sms(mobile=u'15814020825'):
    #     sms = Sms.objects.all()[0]
    #     sms.mobile = mobile
    #     return [sms]
    # sms_list = get_test_sms()
    
    if k_sms_list:        
        for record in k_sms_list:
            convert_count+=1
            id = record.id
            data = {"sms_id":id}
#             payload = urllib.urlencode(data)

            #执行转换
            try:
                res = URL('http://' + SITE_INFO.domain + reverse('cron_sms2send')).post_async(sms_id=id)
#                queue.sms2send.delay(data)
#                print '+++++++++++'
#                 queue = TaskQueue('sms2send')
#                 queue.add(Task("/backend/taskqueue/sms2send",payload))
            except:
                st = SmsTrans()
                st.kinger_sms_to_sms(id)
                print '-------------'

    result = "成功转换 "+str(convert_count)

    return result

@task
def sms2gate(): 

    count = 0
    now = datetime.datetime.now()
    sms_list = SmsSend.objects.not_send_yet_sms2gate()
    sms_list = sms_list.filter(is_in_queue=False)[0:1000]

    if sms_list:
        #sendclient = send()
        for record in sms_list:
            try:
                record.is_in_queue = True
                record.save()
            except:
                pass
            data = {"id":record.id}
#             payload = urllib.urlencode(data)
            #print payload,"========"
            try:
                res = URL('http://' + SITE_INFO.domain + reverse('cron_push_sms_send')).post_async(id=record.id)
#                queue.sms2gate.delay(data)
#                 queue = TaskQueue('sms2gate')
#                 queue.add(Task("/backend/taskqueue/sms2gate",payload))
                count+=1
            except:
                st = SmsSendTrans()
                st.sms_send_to_gate(record.id)
            #print record.receive_mobile

    result = "total push sms2gate:"+str(count)
    return result

#恢复smssend到队列
@task
def smssend_set(): 
    """恢复smssend到队列"""
    print 'smssend_set-------------------'
    count = 0
    try:
        sms_list = SmsSend.objects.not_send_yet_sms2gate()
        sms_list = sms_list.filter(is_in_queue=True)[0:1000]
    except:
        sms_list = []
    if sms_list:
        for record in sms_list:
            try:
                record.is_in_queue = False
                record.save()
                count += 1
            except:
                pass
        
    result = "smssend_set:"+str(count)
    print result,'rrrrrrrrrrr--------------------------------------'
    return result

#短信回复转换到message
@task
def smsreceive2message(): 
    """短信回复转换到message"""
    print 'smsreceive2message-------------------'
    count = 0
    smsrevs = SmsReceive.objects.filter(is_deal=False)
    for rev in smsrevs:
        p2ms = SmsSend.objects.filter(send_mobile=rev.receive_mobile,receive_mobile=rev.send_mobile,is_deal=True).order_by('-id')
        if p2ms.count() > 0:
            try:
                p2m = p2ms[0]
                body = base64.decodestring(rev.content)
                sender = p2m.receiver()
                to_user_list = []
                receiver = p2m.sender
                to_user_list.append(receiver)
                print sender,to_user_list,body,'++++++++++++++++++++++++++++++++++++++++'
                Message.objects.send_message(sender,to_user_list,unicode(body,"gbk"))
                rev.is_deal = True
                rev.deal_date = datetime.datetime.now()
                rev.save()
                r = SmsReplay(sender=sender,target=rev)
                r.save()
                count += 1
            except Exception, e:
                print e,'eeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeee'
            
    result = "smsreceive2message:"+str(count)
    print result,'rrrrrrrrrrr--------------------------------------'
    return result

@task
def remove_temporary_file():
    print 'remove_temporary_file------------------------------------'
    paths = [FILE_PATH + '/temp/',FILE_PATH + '/tile/']
    count = 0
    for file_path in paths:
        for files in os.listdir(file_path):
            try:
                if os.path.isfile(file_path + str(files)):
                    ctime = datetime.datetime.fromtimestamp(os.path.getctime(file_path + str(files)))
                    end_time = datetime.datetime.now() + datetime.timedelta(seconds = -1800)
                    if ctime < end_time:
                        os.remove(file_path + str(files))
                        count += 1
            except:
                pass
    result = "remove_temporary_file:"+str(count)
    print result,'rrrrrrrrrrr--------------------------------------'
    return result

@task
def mytest(times):
    for i in range(times):
        queue.mytest.delay(100,400)
    return HttpResponse('')