# -*- coding: utf-8 -*-

from django.db import models
# from kinger.models import BaseModel
from django.contrib.auth.models import User
from django.utils.translation import ugettext as _

from userena.contrib.umessages.models import MessageContact,Message


class WaiterMessage(models.Model):
	message =  models.OneToOneField(Message,verbose_name = _('the related message'),related_name='waiter_message')	
	user = models.ForeignKey(User, related_name="waiter_user",verbose_name = _('waiter'))

	class Meta:
		verbose_name = "record operators for message"
		db_table = 'waiter_waiter_message'
		permissions = (
            ('can_answer_customer', '客服后台'),
        )