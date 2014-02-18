# # -*- coding: utf-8 -*-
# 
# from django.db import models
# from django.utils.translation import ugettext as _
# from django.contrib.auth.models import User
# from kinger.profiles.models import Profile
# from easy_thumbnails.fields import ThumbnailerImageField
# from kinger.mixins import *
# from kinger.utils import upload_to_mugshot,ThumbnailerImageFields
# from django.core.exceptions import ObjectDoesNotExist
# from djangoratings.fields import RatingField
# import datetime,time
# from decimal import Decimal as D
# from django.contrib.auth.forms import SetPasswordForm
# from userena import signals as userena_signals
# from django.contrib.sites.models import Site
# from django.contrib.contenttypes.models import ContentType
# from django.contrib.contenttypes import generic
# from kinger.models import BaseModel,School
# 
# ##########
# # Models #
# ##########
# 
# SITE_INFO = Site.objects.get_current()
# 
# # class Agency(BaseModel, ActiveMixin, SoftDeleteMixin):
# #     
# #     creator = models.ForeignKey(User,verbose_name = _('creator'))
# #     admins = models.ManyToManyField(User, related_name="manageAgencies", null=True,verbose_name = _('agency admins'))
# #     name = models.CharField(_('Name'),max_length=60, blank=True)
# #     status = models.IntegerField(null=True, blank=True)
# #     description = models.TextField(_('Description'),max_length=765, blank=True)
# # 
# # 
# #     def __unicode__(self):
# #         return self.name
# # 
# #     class Meta:
# #         permissions = (
# #             ('can_manage_agency', '管理集团权限'),
# #         )
# #         verbose_name = _('agency')
# #         verbose_name_plural = _('agencies')
# #         ordering = ['name']
