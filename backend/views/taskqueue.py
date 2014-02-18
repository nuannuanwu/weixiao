# -*- coding: utf-8 -*-
from django.http import HttpResponse
from anyjson import serialize
from APNSWrapper import *
import binascii
from django.views.decorators.csrf import csrf_exempt
from sms.lib.trans import SmsTrans, SmsSendTrans
from sms.lib import send
from sms.models import SmsSend, SmsSendAccount, SmsPort2mobile
from backend.helpers import StaffTrans
from backend import helpers
from kinger.models import Tile,TinymceImage
from kinger.helpers import media_path
from oss_extra.storage import AliyunStorage
import sys,os
reload(sys) 
sys.setdefaultencoding('utf8')

@csrf_exempt
def apns(request): 
    print 'apns...........'
    try:
        token = request.POST.get('token')
        alert = request.POST.get('alert')
        badge = request.POST.get('badge',0)
        sound = request.POST.get('sound','default')

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
        alert = ''

#    return HttpResponse(alert)
    response = {'status': 'success', 'retval': alert}
    return HttpResponse(serialize(response), mimetype='application/json')


@csrf_exempt
def sms2send(request):
    print 'sms2send...........'
    resust = False
    try:
        sms_id = request.REQUEST.get('sms_id')
        st = SmsTrans()
        st.kinger_sms_to_sms(sms_id)
        result = st._msg

    except Exception, e:
        print e
        result = ''
#        return HttpResponse(e)
    
#    return HttpResponse(result)
    response = {'status': 'success', 'retval': result}
    return HttpResponse(serialize(response), mimetype='application/json')


@csrf_exempt
def notice2staff(request):
    print 'notice2staff...........'
    resust = False
    try:
        staff_id = request.REQUEST.get('staff_id')
        unread_mentors = request.REQUEST.get('unread_mentors')
        unread_waiters = request.REQUEST.get('unread_waiters')
        st = StaffTrans()
        st.kinger_notice_to_staff(staff_id,unread_mentors,unread_waiters)
        result = st._msg

    except Exception, e:
        print e
#        return HttpResponse(e)
        result = ''
    
#    return HttpResponse(result)
    response = {'status': 'success', 'retval': result}
    return HttpResponse(serialize(response), mimetype='application/json')

@csrf_exempt
def sms2gate(request):
    print 'sms2gate...........'
    status = False
    now = datetime.datetime.now()
    result = 0
    try:
        id = request.REQUEST.get('id')
        st = SmsSendTrans()
        result = st.sms_send_to_gate(id)
        status = st._msg
    except Exception, e:
        print e
#        return HttpResponse(e)
        status = ''
    
#    return HttpResponse(status)
    response = {'status': 'success', 'retval': status}
    return HttpResponse(serialize(response), mimetype='application/json')

@csrf_exempt
def make_tile_img(request):
    
    try:
        img = request.POST.get('img')
#        tile = Tile.objects.get(pk=id)
#        img = tile.img
        img_large = media_path(img, size="img_large")
        img_middle = media_path(img, size="img_middle")
        img_small = media_path(img, size="img_small")
        img_axis = media_path(img, size="img_axis")
        status = True
    except Exception, e:
        print e,'======================================='
        status = ''

    response = {'status': 'success', 'retval': status}
    return HttpResponse(serialize(response), mimetype='application/json')

@csrf_exempt
def large_img(request):
    try:
        filename = request.POST.get('filename')
        file_path = request.POST.get('file_path')
        tileid = request.POST.get('tileid')
        fr = open(file_path,"rb")
        content = fr.read()
        fr.close()
        try:
            if os.path.isfile(file_path):
                os.remove(file_path)
        except:
            pass
        AliyunStorage(). _put_file(filename, content)
        
        status = True
    except Exception, e:
        status = ''
        
    if tileid:
        try:
            tile = Tile.objects.get(id=tileid)
            img = tile.img
            img_large = media_path(img, size="img_large")
            img_middle = media_path(img, size="img_middle")
            img_small = media_path(img, size="img_small")
            img_axis = media_path(img, size="img_axis")
        except:
            pass
        
    response = {'status': 'success', 'retval': status}
    return HttpResponse(serialize(response), mimetype='application/json')

def httptest(request):
    x = int(request.GET.get('x',100))
    y = int(request.GET.get('y',100))
    z = x + y
    print "===start====="
    print z
    print "===end====="
    response = {'status': 'success', 'retval': z}
    return HttpResponse(serialize(response), mimetype='application/json')

