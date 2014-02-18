# -*- coding: utf-8 -*-

from django.db import models
# from kinger.models import BaseModel
from django.contrib.auth.models import User
from django.utils.translation import ugettext as _

from userena.contrib.umessages.models import MessageContact,Message

class Track(models.Model):
	message_contact =  models.OneToOneField(MessageContact,verbose_name = _('the related message_contact'),related_name='mentor_track')
	is_track = models.BooleanField(default=False)
	user = models.ForeignKey(User, related_name="user_track",verbose_name = _('user track'))

	class Meta:
		verbose_name = "track for parent question"
		permissions = (
            ('can_answer_parent', '专家问答'),
        )

class OperatorsMessage(models.Model):
	message =  models.OneToOneField(Message,verbose_name = _('the related message'),related_name='operators_message')	
	user = models.ForeignKey(User, related_name="operators_user",verbose_name = _('Web site operators'))

	class Meta:
		verbose_name = "record operators for message"