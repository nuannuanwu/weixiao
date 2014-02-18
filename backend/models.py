# # -*- coding: utf-8 -*-

# from django.db import models
# from django.contrib.auth.models import User
# from django.utils.translation import ugettext as _

# # Create your models here.
# #  @soap(Integer,String,String,Integer)
# # data_json = {'eventID':eventID,'sessionID':sessionID,'res':res,'para1':para1}
# class SmsNotifyStatus(models.Model):
#     eventID = models.IntegerField(null=True, blank=True)
#     sessionID = models.CharField(max_length=765, blank=True)
#     res = models.CharField(max_length=765, blank=True)
#     para1 = models.CharField(max_length=765, blank=True)

#     def __unicode__(self):
#         return self.eventID
#     class Meta:
#         db_table = 'sms_notify_status'

# # @soap(String,String,Integer,Integer,String)
# # data_json = {'ucNum':ucNum,'cee':cee,'msgid':msgid,'res':res,'recvt':recvt}
# class SmsReceipt(models.Model):
#     ucNum = models.CharField(max_length=765, blank=True)
#     cee = models.CharField(max_length=765, blank=True)
#     msgid = models.IntegerField(null=True, blank=True)
#     res = models.IntegerField(null=True, blank=True)
#     recvt = models.CharField(max_length=765, blank=True)

#     def __unicode__(self):
#         return unicode(self.msgid)
#     class Meta:
#         db_table = 'sms_receipt'

# #  @soap(String,String,String,String,_returns=Integer)
# # data_json = {'send_mobile':caller,'receive_mobile':ucNum,'content':cont,'receive_date':time}
# class SmsReceive(models.Model):
#     send_mobile = models.CharField(max_length=765, blank=True)
#     receive_mobile = models.CharField(max_length=50, blank=True)
#     content = models.CharField(max_length=765, blank=True)
#     receive_date = models.CharField(max_length=765, blank=True)

#     def __unicode__(self):
#         return self.content
#     class Meta:
#         db_table = 'sms_receive'

# class SmsPort2mobile(models.Model):
#     sender = models.OneToOneField(User,verbose_name = _('sender')) #发送者用户id   
#     send_mobile = models.CharField(max_length=50, blank=True)  #发送端口号
#     receive_mobile = models.CharField(max_length=50, blank=True)  #接收者号码

#     def __unicode__(self):
#         return self.send_mobile

#     class Meta:
#         db_table = 'sms_port2mobile'

