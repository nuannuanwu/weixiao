# -*- coding: utf-8 -*-

from django.db import models
from django.contrib.auth.models import User
from django.utils.translation import ugettext as _
from sms.managers import SmsSendAccountManager
from manage.managers import SmsSendManager

class SmsSend(models.Model):
    """
    短信发送表
    """
    tag_id = models.IntegerField()
    receive_mobile = models.CharField(max_length=36)
    send_mobile = models.CharField(max_length=36)
    content = models.CharField(max_length=765, blank=True)
    send_date = models.DateTimeField(auto_now=True)
    is_deal = models.BooleanField(default=False)
    deal_date = models.DateTimeField(null=True)
    receipt_status = models.IntegerField(null=True,default=0)
    receipt_date = models.DateTimeField(null=True, blank=True)
    is_delete = models.BooleanField(default=False)
    is_in_queue = models.BooleanField(default=False)
    source = models.IntegerField(null=True,default=0)
    content_hash = models.CharField(null=True,max_length=96, blank=True)
    resend_times = models.IntegerField(null=True,default=0)
    sender = models.ForeignKey(User, db_column='sender_uid', verbose_name = u'sender',null=True)
    description = models.CharField(_('Description'),max_length=765, blank=True)
    
    objects = SmsSendManager()
    
    class Meta:
        db_table = u'sms_send'
        
    def receiver(self):
        try:
            from kinger.models import Sms
            sms = Sms.objects.get(id=self.tag_id)
            return sms.receiver
        except:
            pass
        return None

class SmsSendAccount(models.Model):
    """
    发送端口号表
    """
    account_id = models.AutoField(primary_key=True)
    uc = models.CharField(max_length=39, unique=True)
    pw = models.CharField(max_length=36)
    user_id = models.IntegerField()
    status = models.CharField(max_length=60)

    objects = SmsSendAccountManager()

    class Meta:
        db_table = u'sms_send_account'

class SmsNotifyStatus(models.Model):
    eventID = models.IntegerField(null=True, blank=True)
    sessionID = models.CharField(max_length=765, blank=True)
    res = models.CharField(max_length=765, blank=True)
    para1 = models.CharField(max_length=765, blank=True)

    def __unicode__(self):
        return unicode(self.eventID)
    class Meta:
        db_table = 'sms_notify_status'

# @soap(String,String,Integer,Integer,String)
# data_json = {'ucNum':ucNum,'cee':cee,'msgid':msgid,'res':res,'recvt':recvt}
class SmsReceipt(models.Model):
    ucNum = models.CharField(max_length=765, blank=True)
    cee = models.CharField(max_length=765, blank=True)
    msgid = models.IntegerField(null=True, blank=True)
    res = models.IntegerField(null=True, blank=True)
    recvt = models.CharField(max_length=765, blank=True)

    def __unicode__(self):
        return unicode(self.msgid)
    class Meta:
        db_table = 'sms_receipt'
        
    def save(self, *args, **kwargs):
        try:
            sms_send = SmsSend.objects.get(pk=self.msgid)
            sms_send.receipt_status = self.res
            sms_send.save()
        except:
            pass
        super(SmsReceipt, self).save(*args, **kwargs)

#  @soap(String,String,String,String,_returns=Integer)
# data_json = {'send_mobile':caller,'receive_mobile':ucNum,'content':cont,'receive_date':time}
class SmsReceive(models.Model):
    send_mobile = models.CharField(max_length=765, blank=True)
    receive_mobile = models.CharField(max_length=50, blank=True)
    content = models.CharField(max_length=765, blank=True)
    receive_date = models.CharField(max_length=765, blank=True)
    is_deal = models.BooleanField(default=False)
    deal_date = models.DateTimeField(null=True)

    def __unicode__(self):
        return self.content
    class Meta:
        db_table = 'sms_receive'

class SmsPort2mobile(models.Model):
    """
    解决用户手机号码，跟不同的发送者，一致端口号。sender跟receive_mobile是唯一
    """
    sender = models.ForeignKey(User,verbose_name = _('sender'),null=True) #发送者用户id   
    send_mobile = models.CharField(max_length=50, blank=True)  #发送端口号
    receive_mobile = models.CharField(max_length=50, blank=True)  #接收者号码

    def __unicode__(self):
        return self.send_mobile

    class Meta:
        db_table = 'sms_port2mobile'
        unique_together = (('sender','receive_mobile'),)
        
class SmsReplay(models.Model):
    """
    短信回复统计
    """
    sender = models.ForeignKey(User,verbose_name = _('sender'),null=True) #发送者用户id   
    target = models.ForeignKey(SmsReceive,verbose_name = _('receive'),null=True)

    class Meta:
        db_table = 'sms_replay'