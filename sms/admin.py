# -*- coding: utf-8 -*-
from django.contrib import admin
from django.db import models

# from django.utils.translation import ugettext as _

from django.utils.translation import ugettext, ugettext_lazy as _
from django.contrib.admin import widgets, helpers
from django.contrib.admin.util import unquote

from sms.models import SmsNotifyStatus,SmsReceipt,SmsReceive,SmsPort2mobile,SmsSend,SmsSendAccount
from kinger.admin import BackendRoleAdmin
import base64


class SmsPort2mobileAdmin(BackendRoleAdmin):
    list_display = ('sender','send_mobile','receive_mobile','send_status')    
    list_filter = ('sender','send_mobile','receive_mobile')
    search_fields = ['sender__username','send_mobile','receive_mobile']

    def send_status(self, obj):        
        #得到某个唯一匹配的最后发送状态
        send_mobile = obj.send_mobile
        mobile = obj.receive_mobile
        sr = SmsReceipt.objects.filter(ucNum=send_mobile,cee=mobile).order_by('-pk')
        if sr.count():
            res = sr[0].res
        else:
            res = ''
        return res
    send_status.short_description = '最后发送状态'  
    

class SmsSendAdmin(BackendRoleAdmin):
    list_display = ('is_deal','is_in_queue','send_mobile','receive_mobile','content','receipt_status','send_date','content_hash','sender','description')    
    list_filter = ('send_mobile','receive_mobile','send_date')
    search_fields = ['sender__username','send_mobile','receive_mobile','send_date']
    

class SmsSendAccountAdmin(BackendRoleAdmin):
    list_display = ('uc','pw','user_id','status')    
    search_fields = ['uc',]
    

class SmsReceiveAdmin(BackendRoleAdmin):
    list_display = ('is_deal','send_mobile','receive_mobile','receive_date','detail','deal_date')    
    search_fields = ['send_mobile','receive_mobile']
    def detail(self, obj):
        try:
            body = base64.decodestring(obj.content)
            return unicode(body,"gbk")
        except:
            return obj.content
    detail.short_description = '内容'
    detail.allow_tags = True
    
class SmsReceiptAdmin(BackendRoleAdmin):
    list_display = ('id','ucNum','cee','msgid','res','recvt')
    
    
class SmsNotifyStatusAdmin(BackendRoleAdmin):
    list_display = ('id','eventID','sessionID','res','para1')
    

admin.site.register(SmsPort2mobile,SmsPort2mobileAdmin)
admin.site.register(SmsSend,SmsSendAdmin)
admin.site.register(SmsSendAccount,SmsSendAccountAdmin)
admin.site.register(SmsReceipt,SmsReceiptAdmin)
admin.site.register(SmsNotifyStatus,SmsNotifyStatusAdmin)
admin.site.register(SmsReceive,SmsReceiveAdmin)







