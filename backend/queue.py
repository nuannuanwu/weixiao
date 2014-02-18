# -*- coding: utf-8 -*-
from django.http import HttpResponse
from APNSWrapper import *
import binascii
from django.views.decorators.csrf import csrf_exempt
from sms.lib.trans import SmsTrans, SmsSendTrans
from sms.lib import send
from sms.models import SmsSend, SmsSendAccount, SmsPort2mobile
from backend.helpers import StaffTrans
from backend import helpers
from celery.decorators import task
import sys 
reload(sys) 
sys.setdefaultencoding('utf8')

@task
def apns(data): 
    try:
        token = data['token']
        alert = data['alert']
        badge = data['badge']
        sound = data['sound']

        alert = alert.encode('utf-8')
        wrapper = APNSNotificationWrapper(helpers.get_pem_file())
        #deviceToken = binascii.unhexlify(token)
        message = APNSNotification()
        deviceToken = binascii.unhexlify(token)
        message.token(deviceToken)
        message.alert(alert)
        message.badge(int(badge))
        message.sound(sound)
        wrapper.append(message)
        rs = wrapper.notify()
    except Exception, e:
        print e

#     return HttpResponse(alert)


@task
def sms2send(data):
    result = False
    try:
        
        sms_id = data['sms_id']
        st = SmsTrans()
        st.kinger_sms_to_sms(sms_id)
        result = st._msg
    except Exception, e:
        print e




@task
def notice2staff(data):
    result = False
    try:
        staff_id = data['staff_id']
        unread_mentors = data['unread_mentors']
        unread_waiters = data['unread_waiters']
        st = StaffTrans()
        st.kinger_notice_to_staff(staff_id,unread_mentors,unread_waiters)
        result = st._msg

    except Exception, e:
        print e
#         return HttpResponse(e)
#     
#     return HttpResponse(result)

@task
def sms2gate(data):
    
    status = False
    now = datetime.datetime.now()
    result = 0
    try:
        id = data['id']
        st = SmsSendTrans()
        result = st.sms_send_to_gate(id)
        status = st._msg
    except Exception, e:
        print e
#         return HttpResponse(e)
#     
#     return HttpResponse(status)
    
@task
def mytest(x, y):
    z = x + y
    print "===start====="
    print z
    print "===end====="
    return z

from django.http import HttpResponse
from anyjson import serialize
def httptest(request, x, y):
    z = x + y
    print "===start====="
    print z
    print "===end====="
    response = {'status': 'success', 'retval': z}
    return HttpResponse(serialize(response), mimetype='application/json')
