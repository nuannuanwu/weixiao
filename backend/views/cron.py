# -*- coding: utf-8 -*-

from django.http import HttpResponse
from kinger.models import Mentor,ApplePushNotification,Device,Tile,Sms,Cookbook,CookbookRead,Student,Access_log,RelevantStaff
from sms.models import SmsSend, SmsSendAccount
from django.contrib.auth.models import User
from sms.models import SmsNotifyStatus,SmsReceipt,SmsReceive,SmsPort2mobile
from userena.contrib.umessages.models import Message, MessageRecipient, MessageContact
from backend import helpers
from aq.views.default import get_unread_mentor_count as unread_mentor
from waiter.views.default import get_unread_waiter_count as unread_waiter

from kinger.settings import DATABASES
from APNSWrapper import *
import binascii
import MySQLdb
from sms.lib.trans import SmsTrans, SmsSendTrans
from django.core.urlresolvers import reverse
from django.contrib.sites.models import Site
# from backend import queue
# from celery.decorators import task
try:
    from sae.taskqueue import Task, TaskQueue
except:
    pass
import urllib

import sys 
reload(sys) 
sys.setdefaultencoding('utf8')

SITE_INFO = Site.objects.get_current()

#class Apns:
#
#    def __init__(self, cert_id = None, body = None, force_ssl_command = False, debug_ssl = False):
#        pass
#
#    def push(self,body,token):
#
#        aps = body.get('aps')
#        alert = aps.get('alert')
#        badge = aps.get('badge',1)
#        sound = aps.get('sound','default')
#        data = {"alert":alert,"badge":badge,"sound":sound,"token":token}
##         payload = urllib.urlencode(data)
#        #print payload,"========"
#
#        try:
##             queue.apns.delay(data)
#            queue = TaskQueue('apns')
#            queue.add(Task("/backend/taskqueue/apns",payload))
#        except:
#            #print "send by myself =========="
#            alert = alert.encode('utf-8')
#            wrapper = APNSNotificationWrapper(helpers.get_pem_file())
#            message = APNSNotification()
#            deviceToken = binascii.unhexlify(token)
#            message.token(deviceToken)
#            message.alert(alert)
#            message.badge(int(badge))
#            message.sound(sound)
#            wrapper.append(message)
#            rs = wrapper.notify()            
#            pass

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
        
def push_tile(request,template_name="default/index.html"): 
#     queue = TaskQueue('apns')
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
                #data = {"alert":n.alert,"badge":n.badge,"sound":n.sound,"token":deviceToken}
#                 payload = urllib.urlencode(data)
                #print payload
                #tasks = [Task("/tasks/update", user) for user in users]
                #queue.add(tasks)
                count = count + 1
                #queue.add(Task("/backend/taskqueue/apns",payload))
#                Apns.push(data, deviceToken)
                Apns().push(data, deviceToken)
            n.is_send = 1
            n.save()

    result = "total push:"+str(count)
    return HttpResponse(result)

from django.db import connection
def push_unread_message(request): 
    count = 0
    start_time = datetime.datetime.now() + datetime.timedelta(seconds = -300)
    #unread_message_list = MessageRecipient.objects.filter(read_at__isnull=True,deleted_at__isnull=True).all()
    send_time = datetime.datetime.now()
#    sql = "select a.id,a.user_id,a.message_id,b.token from umessages_messagerecipient a  left join kinger_device b on a.user_id = b.user_id  left join umessages_message c on a.message_id = c.id where c.sent_at<'" + str(send_time) + "' and a.no_need_send=0 and a.is_push =0 and a.read_at is null and a.deleted_at is null and b.token is not null limit 0,1000"
    sql = "select a.id,a.user_id,a.message_id,b.token from umessages_messagerecipient a  left join kinger_device b on a.user_id = b.user_id  left join umessages_message c on a.message_id = c.id where c.sent_at>'" + str(start_time) + "' and c.sent_at<='" + str(send_time) + "' and a.is_push =0 and a.read_at is null and a.deleted_at is null and b.token is not null limit 0,1000"
    cursor = connection.cursor()
    cursor.execute(sql)
    unread_message_list = cursor.fetchall()

    apns = Apns()
    if unread_message_list:
        for n in unread_message_list:
            device_token = n[3]
            message_id = n[2]
            mr_id = n[0]

            m = Message.objects.get(id=message_id)
            sender_name = m.sender.get_profile().chinese_name() or m.sender.username
            try:
                sender_name = m.sender.get_profile().chinese_name() or m.sender.username
                alert = sender_name+":"+m.body
                body = {"aps":{"alert":alert}}
                result = apns.push( body , device_token )

                mr = MessageRecipient.objects.get(id=mr_id)
                mr.is_push = 1
                mr.save()
            except:
                pass


            count = count +1

    result = "total push message:"+str(count)
    return HttpResponse(result)


#发送未读消息
def send_unread_message(request): 
    print 'cron----------------------------------------'
    count = 0
    #unread_message_list = MessageRecipient.objects.filter(read_at__isnull=True,deleted_at__isnull=True).all()
    time_start = datetime.datetime.now() + datetime.timedelta(weeks = -1)
    time_end = datetime.datetime.now() + datetime.timedelta(seconds = -1800)
    sql = "select a.id,a.user_id,a.message_id,c.sender_id,c.body from umessages_messagerecipient a  left join umessages_message c on a.message_id = c.id where c.sent_at>'" + str(time_start) + "' and c.sent_at<'" + str(time_end) + "' and a.no_need_send=0 and a.is_send =0 and a.read_at is null limit 0,1000"
    
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
        msg.content = m['body']
        msg.save()
        
        unread = MessageRecipient.objects.get(pk=m['id'])
        unread.is_send = 1
        unread.save()
        count = count + 1
    result = "total push message:"+str(count)
    return HttpResponse(result)


#发送紧急通知
def send_emergency_message(request): 
    count = 0
    time_start = datetime.datetime.now() + datetime.timedelta(weeks = -1)
    time_end = datetime.datetime.now() + datetime.timedelta(seconds = -300)
    sql = "select a.id,a.user_id,a.message_id,c.sender_id,c.body from umessages_messagerecipient a  left join umessages_message c on a.message_id = c.id where c.type=1 and c.sent_at>'" + str(time_start) + "' and c.sent_at<'" + str(time_end) + "' and a.no_need_send=0 and a.is_send =0 and a.read_at is null limit 0,1000"
    
    cursor = connection.cursor()
    cursor.execute(sql)
    desc = cursor.description
    unread_list = [dict(zip([col[0] for col in desc], row)) for row in cursor.fetchall()]
    for m in unread_list:
        msg = Sms()
        msg.sender_id = m['sender_id']
        msg.receiver_id = m['user_id']
        msg.mobile = User.objects.get(pk=m['user_id']).get_profile().mobile
        msg.type_id = 5
        msg.content = m['body']
        msg.save()
        
        unread = MessageRecipient.objects.get(pk=m['id'])
        unread.is_send = 1
        unread.save()
        count = count + 1
    result = "total push message:"+str(count)
    return HttpResponse(result)


#发送未读导师及客服提醒
def send_staff_unread(request): 
   
    unread_mentors = unread_mentor()
    unread_waiters = unread_waiter()
    if not unread_mentors and not unread_waiters:
        return HttpResponse("")
    
    staffs = RelevantStaff.objects.exclude(send_mentor=False,send_waiter=False)
    
    for s in staffs:
        #发送短信,已有队列
        if s.send_mentor and unread_mentors and s.mobile:
            msg = "<" + SITE_INFO.name + ">导师留言后台有" + str(unread_mentors) + "条新客户留言. 请及时登录回复. 登录地址: " + SITE_INFO.domain + reverse('aq')
            helpers.send_staff_mobile(s.mobile,msg)
        if s.send_waiter and unread_waiters and s.mobile:
            msg = "<" + SITE_INFO.name + ">客服后台有" + str(unread_waiters) + "条新客服留言. 请及时登录回复. 登录地址: " + SITE_INFO.domain + reverse('waiter')
            helpers.send_staff_mobile(s.mobile,msg)
             
    for s in staffs: 
        #发送邮件队列   
        data = {"staff_id":s.id,"unread_mentors":unread_mentors,"unread_waiters":unread_waiters}
#         payload = urllib.urlencode(data)
        #执行转换
        try:
#             queue.notice2staff.delay(data)
            queue = TaskQueue('notice2staff')
            queue.add(Task("/backend/taskqueue/notice2staff",payload))
        except:
            st = helpers.StaffTrans()
            st.kinger_notice_to_staff(s.id,unread_mentors,unread_waiters)
    return HttpResponse('')


#发送未读食谱
def send_unread_cookbook(request): 
    count = 0
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
            
    result = "total push cookbooks:"+str(count)
    return HttpResponse(result)
 

def send_user_message(request): 
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
                msg.content = "您有" + str(unread_count) + "条新内容未查看，您可以登陆网站或者安装客户端来查看，详情请登录 http://jytn365.com/welcom [记忆童年]"
                msg.save()
                count = count + 1
            
    result = "total push user_message:"+str(count)
    return HttpResponse(result)
 
    
def push_unread_tile(request): 
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
    return HttpResponse(result)


def sms2send(request): 
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
#                 queue.sms2send.delay(data)
#                 print '+++++++++++'
                queue = TaskQueue('sms2send')
                queue.add(Task("/backend/taskqueue/sms2send",payload))
            except:
                st = SmsTrans()
                st.kinger_sms_to_sms(id)
                print '-------------'

    result = "成功转换 "+str(convert_count)

    return HttpResponse(result)


def sms2gate(request): 

    count = 0
    now = datetime.datetime.now()
    sms_list = SmsSend.objects.not_send_yet_sms2gate()[0:1000]
    
    if sms_list:
        #sendclient = send()
        for record in sms_list:

            data = {"id":record.id}
#             payload = urllib.urlencode(data)
            #print payload,"========"
            try:
#                 queue.sms2gate.delay(data)
                queue = TaskQueue('sms2gate')
                queue.add(Task("/backend/taskqueue/sms2gate",payload))
                count+=1
            except:
                st = SmsSendTrans()
                st.sms_send_to_gate(record.id)
            #print record.receive_mobile

    result = "total push message:"+str(count)
    return HttpResponse(result)

# @task
def mytest(request):
#     for i in range(100):
#         r = queue.mytest.delay(100,400)
    return HttpResponse('')