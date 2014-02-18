# -*- coding: utf-8 -*-

from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
from kinger.validators import validate_mobile_number,validate_id_number,validate_telephone_number
from kinger import helpers

from userena.models import UserenaBaseProfile
#from caching.base import CachingMixin, CachingManager
from kinger import helpers
from userena import settings as userena_settings  

class Profile(UserenaBaseProfile):
    #objects = CachingManager()
    """ Default profile """
    GENDER_CHOICES = (
        (1, _('Male')),
        (2, _('Female')),
    )

    user = models.OneToOneField(User,unique=True,verbose_name=_('User'),related_name='profile')
#     user = models.ForeignKey(User,unique=True,verbose_name=_('User'),related_name='profile')

    gender = models.PositiveSmallIntegerField(_('Gender'),
                                              choices=GENDER_CHOICES,
                                              blank=True,
                                              null=True)

    # website = models.URLField(_('Website'), blank=True, verify_exists=True)
    # location =  models.CharField(_('Location'), max_length=255, blank=True)

    birth_date = models.DateField(_('Birth date'), blank=True, null=True,\
        help_text=_("Please use the following format: YYYY-MM-DD"))
    about_me = models.TextField(_('About me'), blank=True)
    mobile = models.CharField(_('Mobile'), max_length=20, blank=True, \
        validators=[validate_mobile_number])
    is_mentor = models.BooleanField(default=False, blank=False)
    is_waiter = models.BooleanField(default=False, blank=False)
    last_access = models.DateTimeField(null=True,blank=True,verbose_name = _('last access time'))
    id_number = models.CharField(_('IdNumber'), max_length=20, blank=True, \
        validators=[validate_id_number])
    office_phone = models.CharField(_('Office Phone'), max_length=20, blank=True, \
        validators=[validate_telephone_number])
    other_phone = models.CharField(_('Other Phone'), max_length=20, blank=True, \
        validators=[validate_telephone_number])
    office_email = models.EmailField(_('office e-mail address'), blank=True)
    other_email = models.EmailField(_('other e-mail address'), blank=True)
    address = models.CharField(_('Address'), max_length=150, blank=True)
    # update_username_at = models.DateField(blank=True, null=True)
    # def can_change_username(self):
        # return self.update_username_at

    # 真实姓名，解决用户的名字显示问题(学生、教师、导师)。
    realname = models.CharField(_('realname'), max_length=30, blank=True)
    
    def last_access_time(self):
        if self.last_access:
            return self.last_access
        else:
            return self.user.last_login
            
    @property
    def age(self):
        return helpers.calculate_age(self.birth_date)

    def chinese_name(self):
        """
        Returns the first_name plus the last_name, with a space in between.
        """
        full_name = u'%s %s' % (self.user.last_name, self.user.first_name)
        return full_name.strip()

    @property
    def is_vip(self):
        """
        目前仅判断家长身份,对推荐的瓦片进行公开的限制
        """
        try:
            self.user.student
            return True
        except Exception, e:
            return False

    @property
    def get_avatar(self):
        try:
            #self.mugshot['avatar'].url              
            return self.mugshot
        except Exception, e:           
            return helpers.get_avatar()

    def chinese_name_or_username(self):
        """
        显示的机制为 realname >> first_name,last_name >> username
        """        
        
        try:
            if self.user.teacher.name:
                return self.user.teacher.name
        except:
            pass
        try:
            if self.user.student.name:
                return self.user.student.name
        except:
            pass
        
        if self.realname:
            return self.realname

        user = self.user
        
        if user.first_name or user.last_name:
            # We will return this as translated string. Maybe there are some
            # countries that first display the last name.
            name = u"%(last_name)s%(first_name)s" % \
                {'first_name': user.first_name,
                 'last_name': user.last_name}
        else:
            # Fallback to the username if usernames are used
            if not userena_settings.USERENA_WITHOUT_USERNAMES:
                name = "%(username)s" % {'username': user.username}
            else:
                name = "%(email)s" % {'email': user.email}
        
        return name.strip()


@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)
