# -*- coding: utf-8 -*-

# This is an auto-generated Django model module.
# You'll have to do the following manually to clean this up:
#     * Rearrange models' order
#     * Make sure each model has one field with primary_key=True
# Feel free to rename the models, but don't rename db_table values or field names.
#
# Also note: You'll have to insert the output of 'django-admin.py sqlcustom [appname]'
# into your database.

from django.db import models
from django.utils.translation import ugettext as _
from django.contrib.auth.models import User
from kinger.profiles.models import Profile
from easy_thumbnails.fields import ThumbnailerImageField
from kinger.mixins import *
from kinger.utils import upload_to_mugshot,ThumbnailerImageFields
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.comments import Comment
from manage.managers import SchoolUserManager, TileManager, SmsManager, CookbookManager, CookbookSetManager, VerifySmsManager, \
TileCategoryManager,CharManager,CookbookreadManager,TeacherdManager,DailyRecordVisitorManager,SoftDeleteManager

# from kinger.validators import validate_not_spaces,user_is_exist,validate_max_size,validate_mobile_number
from kinger.validators import *
from kinger import helpers

from djangoratings.fields import RatingField
#喜欢按钮
from likeable.models import Likeable
import datetime,time
from decimal import Decimal as D
from django.contrib.auth.forms import SetPasswordForm
from userena import signals as userena_signals
from django.contrib.sites.models import Site
from django.contrib.comments import Comment
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes import generic
from django.core.cache import cache
from celery.task.http import URL
from django.core.urlresolvers import reverse

##########
# Models #
##########

#from django.conf import settings
#from django.core import urlresolvers
#
#domain_type = cache.get('domain_parts_len')
#if domain_type == 3:
#    def reverse_subdomain(*args, **kwargs):
#        path_info = old_reverse(*args, **kwargs)
#        parts = path_info[1:].split('/', 1)
#        try:
#            path = parts[1]
#        except:
#            path = ''
#        path_info = 'http://%s%s/%s' % (
#                parts[0], '.lifedu.cn:8000', path)
#        return path_info
#    old_reverse = urlresolvers.reverse
#    urlresolvers.reverse = reverse_subdomain


SITE_INFO = Site.objects.get_current()

class BaseModel(models.Model):
    ctime = models.DateTimeField(auto_now_add=True)
    mtime = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class GroupTeacher(BaseModel, ActiveMixin, SoftDeleteMixin):
    group = models.ForeignKey("Group",verbose_name = _('group'))
    teacher = models.ForeignKey("Teacher",verbose_name = _('teacher'))
    type = models.ForeignKey("TeacherType",verbose_name = _('teacher type'))
    class Meta:
        verbose_name = _('group teacher')
        verbose_name_plural = _('group teachers')
        db_table = 'oa_groupteacher'
        
    def __unicode__(self):
        return unicode(self.teacher)
            
   
class Teacher(BaseModel, ActiveMixin, SoftDeleteMixin):
    creator = models.ForeignKey(User, related_name="+",verbose_name = _('creator'))
    user = models.OneToOneField(User,verbose_name = _('user'),validators=[user_is_exist])
    school = models.ForeignKey("School", null=True, blank=True,verbose_name = _('school'))
    is_authorize = models.BooleanField(default='', blank=False)
    name = models.CharField(_('Teacher name'), max_length=60,  validators=[validate_not_spaces])
    appellation = models.CharField(_('Appellation'), max_length=60, blank=True)
    description = models.TextField(_('Description'), max_length=765, blank=True)
    send_time = models.DateTimeField(null=True,blank=True,verbose_name = _('last send time'))
    pinyin = models.CharField(_('pinyin'), max_length=100, blank=True)
    objects = TeacherdManager()
    
    def __unicode__(self):
        return self.name

    def save(self, *args, **kwargs):
        self.pinyin = Char.objects.trans(self.name)

        profile = self.user.get_profile()
        profile.realname = self.name
        profile.save()
        create = False if self.id else True
        super(Teacher, self).save(*args, **kwargs)
        
#         if self.school_id > 0:
#             try:
#                 postjob,create = PostJob.objects.get_or_create(teacher_id=self.id,school_id=self.school_id)
#                 postjob.save()
#             except:
#                 pass
        
    def getgroups(self):
        groupteacher = GroupTeacher.objects.filter(teacher=self)
        groups = [g.group for g in groupteacher]
        return groups
        
    def getAvatar(self):
        profile = self.user.get_profile()
        return profile.mugshot

    def getMobile(self):
        mobile = ''
        try:
            profile = self.user.get_profile()
            mobile = profile.mobile
        except ObjectDoesNotExist:
            pass
        return mobile

    def resetPasswordAndSendSms(self, pass_form=SetPasswordForm, sender=None):
        #
        try:
            user = self.user
        except ObjectDoesNotExist:
            return False

        new_password = User.objects.make_random_password(length=6,allowed_chars='0123456789')
        data = {'new_password1': new_password, 'new_password2': new_password}
        form = pass_form(user=user, data=data)

        if form.is_valid():
            form.save()
            mobile = self.getMobile()
            content = False
            if mobile:
                username = user.username                
                content = u"尊敬的用户，您的登录帐号是:" + username + u",密码是:" + new_password+u"【" + SITE_INFO.name + "】"
                content = u"尊敬的用户您好，欢迎使用【" + SITE_INFO.name + "】家园沟通应用，您的帐号：" + username + u" 密码：" + new_password + u" 登入" + SITE_INFO.domain + "即刻体验,详情咨询：0755-86350888"
                userena_signals.password_complete.send(sender=None, user=user)
                # 记录到 sms表
                #sender = self.user
                receiver = self.user

                Sms.objects.create_send_account_sms(sender=sender, receiver=receiver, mobile=mobile, content=content)

        return content

    class Meta:
        verbose_name = _('teacher')
        verbose_name_plural = _('teachers')
        ordering = ['pinyin','name']


class TeacherType(BaseModel, ActiveMixin, SoftDeleteMixin):
    name = models.CharField(_('Name'),max_length=120, validators=[validate_not_spaces])
    class Meta:
        verbose_name = _('teacher type')
        verbose_name_plural = _('teacher types')
        ordering = ['name']
        db_table = 'oa_teachertype'
        
    def __unicode__(self):
        return self.name
    
    
class GroupGrade(BaseModel, ActiveMixin, SoftDeleteMixin):
    name = models.CharField(_('Name'),max_length=120, validators=[validate_not_spaces])
    class Meta:
        verbose_name = _('group grade')
        verbose_name_plural = _('group grades')
        ordering = ['id']
        db_table = 'oa_groupgrade'
        
    def __unicode__(self):
        return self.name
    

class Role(BaseModel, ActiveMixin, SoftDeleteMixin):
    name = models.CharField(_('Name'),max_length=120, validators=[validate_not_spaces])
    school = models.ForeignKey("School",verbose_name = _('school'))
    owners = models.ManyToManyField(User, related_name="roles", null=True, verbose_name = _('owners'))
    description = models.TextField(_('Description'), max_length=765, blank=True)
    TYPE_CHOICES = ((0, u'普通角色'),(1, u'内置角色'))
    type = models.IntegerField(_('type'),default=0,choices=TYPE_CHOICES)
    class Meta:
        verbose_name = _('role')
        verbose_name_plural = _('roles')
        ordering = ['name']
        db_table = 'oa_role'
        
    def __unicode__(self):
        return self.name    
    

class WorkGroup(BaseModel, ActiveMixin, SoftDeleteMixin):
    name = models.CharField(_('Name'),max_length=120, validators=[validate_not_spaces])
    school = models.ForeignKey("School",verbose_name = _('school'))
    user = models.ForeignKey(User,verbose_name = _('user'),blank=True,null=True)
    TYPE_CHOICES = (
        (0, u'全局虚拟组'),
        (1, u'个人虚拟组'),
    )
    type = models.IntegerField(_('type'),default=0,choices=TYPE_CHOICES)
    members = models.ManyToManyField(User, related_name="workgroups", null=True, verbose_name = _('members'))
    description = models.TextField(_('Description'), max_length=765, blank=True)
    class Meta:
        verbose_name = _('work group')
        verbose_name_plural = _('work groups')
        ordering = ['name']
        db_table = 'oa_workgroup'
        
    def __unicode__(self):
        return self.name   
    

class Communicate(BaseModel, ActiveMixin, SoftDeleteMixin):
    school = models.ForeignKey("School",verbose_name = _('school'))
    parent = models.ForeignKey("School",verbose_name = _('school'),related_name="communicates")
    description = models.TextField(_('Description'), max_length=765, blank=True)
    class Meta:
        verbose_name = _('communicate')
        verbose_name_plural = _('communicates')
        db_table = 'oa_communicate'
        
    def __unicode__(self):
        return self.name   
    

class Access(BaseModel, ActiveMixin, SoftDeleteMixin):
    name = models.CharField(_('Name'),max_length=120, validators=[validate_not_spaces])
    code = models.CharField(_('code'),max_length=20,blank=True)
    parent = models.ForeignKey('self',null=True,blank=True,default=0,verbose_name = _('access parent'))
    LEVEL_CHOICES = (
        (0, u'集团级别'),
        (1, u'学园级别'),
    )
    level = models.IntegerField(_('level'),default=0,choices=LEVEL_CHOICES)
    roles = models.ManyToManyField("Role",related_name="accesses", null=True, verbose_name = _('roles'))
    description = models.TextField(_('Description'), max_length=765, blank=True)
    class Meta:
        verbose_name = _('access')
        verbose_name_plural = _('accesses')
        #ordering = ['id']
        db_table = 'oa_access'
        
    def __unicode__(self):
        return self.name  
    
    def is_parent(self):
        return self.parent_id == 0
    
    def save(self, *args, **kwargs):
        if not self.parent_id:
            self.parent_id = 0
        if self.parent:
            self.level = self.parent.level
        super(Access, self).save(*args, **kwargs)
    
    
class BirthControl(BaseModel, ActiveMixin, SoftDeleteMixin):
    student = models.OneToOneField('Student',verbose_name = _('student'),null=True,related_name='birth')
    is_single = models.BooleanField(default='', blank=False)
    childnum = models.IntegerField(_('Child Num '),null=True, blank=True)
    order = models.IntegerField(_('Child Order'),null=True, blank=True)
    overtbirth = models.BooleanField(default='', blank=True)
    is_pay = models.BooleanField(default='', blank=True)
    class Meta:
        verbose_name = _('birth control')
        verbose_name_plural = _('birth controls')
        db_table = 'oa_birthcontrol'
        
    def __unicode__(self):
        return unicode(self.student)
    
    def save(self, *args, **kwargs):
        super(BirthControl, self).save(*args, **kwargs)
        
    
class Group(BaseModel, ActiveMixin, SoftDeleteMixin):
    TYPE_CHOICES = ((1, _('常规')),(2, _('预报名')),)
    SN_CHOICES = [[str(x).zfill(2) for i in range(0,2)] for x in range(1,21)]
    year = datetime.datetime.now().year
    YEAR_CHOICES = [[str(x) for i in range(0,2)] for x in range(year - 10,year + 10)]
    
    creator = models.ForeignKey(User,verbose_name = _('creator'))
    school = models.ForeignKey("School",verbose_name = _('school'))
    teachers = models.ManyToManyField(Teacher, related_name="groups", null=True,verbose_name = _('teacher'))
    name = models.CharField(_('Name'),max_length=120, validators=[validate_not_spaces])
    logo = ThumbnailerImageField(_('Logo'),
            blank=True,
            upload_to=upload_to_mugshot,
            )
    
    grade = models.ForeignKey("GroupGrade",verbose_name = _('grade'),blank=True, null=True)
    type = models.PositiveSmallIntegerField(_('Type'),choices=TYPE_CHOICES,default=1)
    headteacher = models.ForeignKey("Teacher",verbose_name = _('headteacher'),blank=True, null=True)
    send_time = models.DateTimeField(null=True,blank=True,verbose_name = _('last send time'))
    
    year = models.CharField(_('Year'),max_length=36, choices=YEAR_CHOICES,blank=True, null=True)
    sn = models.CharField(_('Sn'),max_length=36, choices=SN_CHOICES,blank=True, null=True)
    announcement = models.CharField(_('Announcement'),max_length=765, blank=True)
    description = models.TextField(_('Description'), max_length=765, blank=True)

    class Meta:
        verbose_name = _('school class')
        verbose_name_plural = _('school classes')
        ordering = ['-ctime']
        
    def __unicode__(self):
        return self.name
    
    def class_id(self):
        school_id = self.school_id
        try:
            group = Group.objects.get(name="全园班级",school_id=school_id,type=3)
            return group.id
        except:
            return 0
    
    def user(self):
        print self.avatar_large(),'llllllllllllllllllllll'
        u = {
                "username": self.name,
                "avatar_large": self.avatar_large(),
                "uid": self.id,
                "mobile": "",
                "gender": "",
                "last_login": "",
                "avatar": self.avatar(),
                "about_me": "",
                "name": self.name,
            }
        return u
    
    def avatar(self):
        try:
            url = self.logo
            url = helpers.media_path(url, "avatar")
            return url
        except Exception:
            return ""
    
    
    def avatar_large(self):
        try:
            url = self.logo
            url = helpers.media_path(url, "avatar_large")
            return url
        except Exception:
            return ""
    
    def get_teachers(self):
        teachers_pre = [t for t in self.teachers.all()]
        teachers_ext = [g.teacher for g in GroupTeacher.objects.filter(group=self)]
        schools = teacher_age_list = []
        school = self.school
        if school.is_delete:
            return teacher_age_list
        if school.parent_id == 0:
            schools.append(school)
            schools = schools + [s for s in School.objects.filter(parent=school,is_delete=False)]
        else:
            agency = school.parent
            schools.append(agency)
            schools = schools + [s for s in School.objects.filter(parent=agency,is_delete=False)]
        
        teacher_age_list = [t for t in Teacher.objects.filter(school__in=schools,is_authorize=True)]
        teacher_age = teacher_age_list
    
        teachers = teachers_pre + teachers_ext + teacher_age
        teachers = list(set(teachers))
        return teachers
        
    def save(self, *args, **kwargs):
        if not self.logo:
            self.logo = 'group/African_Pets_003.png'
        if not self.grade_id:
            self.grade_id = 6
        super(Group, self).save(*args, **kwargs)


class School(BaseModel, ActiveMixin, SoftDeleteMixin):
    AREA_CHOICES = (
        (u'罗湖区', u'罗湖区'),
        (u'南山区', u'南山区'),
        (u'福田区', u'福田区'),
        (u'龙岗区', u'龙岗区'),
        (u'盐田区', u'盐田区'),
        (u'宝安区', u'宝安区'),        
        )
    CITY_CHOICES = (
        (u'深圳市', u'深圳市'),
        )
    TYPE_CHOICES = (
        (1, _('幼儿园')),
        (2, _('集团')),
        )
    creator = models.ForeignKey(User,verbose_name = _('creator'),related_name="school")
    admins = models.ManyToManyField(User, related_name="manageSchools", null=True,verbose_name = _('school admins'))
    header = models.ForeignKey(User,verbose_name = _('header'),null=True, blank=True,related_name="schoolheader")
    name = models.CharField(_('Name'),max_length=60, blank=True)
    short_name = models.CharField(_('ShortName'),max_length=60, blank=True)
    area = models.CharField(_('Area'),max_length=60, blank=True,choices=AREA_CHOICES,)
    city = models.CharField(_('City'),max_length=60, blank=True,choices=CITY_CHOICES,)
    province = models.CharField(_('Province'),max_length=60, blank=True)
    sys = models.CharField(_('Sys'),max_length=9, null=True, blank=True)
#    agency = models.ForeignKey('Agency',verbose_name = _('agency'),null=True, blank=True)
    parent = models.ForeignKey('self',null=True,blank=True,verbose_name = _('school parent'),related_name="subschools")
#     type = models.IntegerField(_('Type'),null=True, blank=True)
    type = models.PositiveSmallIntegerField(_('Type'),choices=TYPE_CHOICES,blank=True,null=True)
    description = models.TextField(_('Description'),max_length=765, blank=True)
    objects = SoftDeleteManager()
    userObjects = SchoolUserManager()

    def __unicode__(self):
        return self.name

    class Meta:
        permissions = (
            ('can_manage_school', '管理学校权限'),
        )
        verbose_name = _('school')
        verbose_name_plural = _('schools')
        ordering = ['parent__id','name']
        
    def save(self, *args, **kwargs):
        create = False if self.id else True
        super(School, self).save(*args, **kwargs)
        if create:
            group,created = Group.objects.get_or_create(name="全园班级",school_id=self.id,type=3,creator=self.creator,grade_id=0)
            try:
                from oa.helpers import school_inner_role
                school_inner_role(self)
            except:pass


class Agency(BaseModel, ActiveMixin, SoftDeleteMixin):
    
    creator = models.ForeignKey(User,verbose_name = _('creator'))
    name = models.CharField(_('Name'),max_length=60, blank=True)
    school = models.OneToOneField('School',verbose_name = _('school'),null=True, blank=True)
#    user = models.ForeignKey(User,verbose_name = _('user'),related_name="realted_agency")
#    agency_school = models.OneToOneField('School',unique=True,verbose_name=_('school'),related_name='school_agency',help_text='sss')
    status = models.BooleanField(_('status'),default=True)
    description = models.TextField(_('Description'),max_length=765, blank=True)
    admins = models.ManyToManyField(User, related_name="manageAgencies", null=True,verbose_name = _('agency admins'))

    def __unicode__(self):
        return self.name

    class Meta:
        permissions = (
            ('can_manage_agency', '管理集团权限'),
        )
        verbose_name = _('agency')
        verbose_name_plural = _('agencies')
        ordering = ['name']
        db_table = 'oa_agency'
        
    def customSave(self,admin_pks):
        role,created = Role.objects.get_or_create(school_id=0,name='集团管理员')
        try:
            for u in self.admins.all():
                u.roles.remove(role)
        except:       
            pass
        admins = User.objects.filter(id__in=admin_pks)
        for a in admins:
            try:
                teacher = a.teacher
                teacher.school_id = self.school_id
                teacher.save()
            except:
                teacher = Teacher()
                teacher.user_id = a.id
                teacher.creator_id = self.creator_id
                teacher.school_id = self.school_id
                teacher.name = a.username
                teacher.save()
            a.roles.add(role)
            
    
    def save(self, *args, **kwargs):
        if not self.id:
            school = School(creator_id=self.creator_id,parent_id=0,name=self.name)
            school.save()
            self.school = school
        super(Agency, self).save(*args, **kwargs)


class Guardian(BaseModel, ActiveMixin, SoftDeleteMixin):
    name = models.CharField(_('Name'),max_length=60, blank=True)
    student = models.ForeignKey('Student',verbose_name = _('student'),related_name="guardians",null=True,blank=True)
    relation = models.CharField(_('Relation'),max_length=60, blank=True)
    mobile = models.CharField(_('Mobile'), max_length=20, blank=True)
    office_phone = models.CharField(_('Office Phone'), max_length=20, blank=True, \
        validators=[validate_telephone_number])
    other_phone = models.CharField(_('Other Phone'), max_length=20, blank=True, \
        validators=[validate_telephone_number])
    office_email = models.EmailField(_('office e-mail address'), blank=True)
    other_email = models.EmailField(_('other e-mail address'), blank=True)
    address = models.CharField(_('Address'), max_length=150, blank=True)
    unit = models.CharField(_('unit'), max_length=150, blank=True)
    regist = models.ForeignKey('Registration',verbose_name = _('regist'),related_name="guardians",null=True,blank=True)
    
    class Meta:
        verbose_name = _('guardian')
        verbose_name_plural = _('guardians')
        ordering = ['ctime','name']
        db_table = 'oa_guardian'
        
    def __unicode__(self):
        return self.name
    
    def save(self, *args, **kwargs):      
        super(Guardian, self).save(*args, **kwargs)
  
class PostJob(BaseModel, ActiveMixin, SoftDeleteMixin):
    STATUS_TYPE = (
        (0, _('在职')),
        (1, _('离职')),
    )
    school = models.ForeignKey('School',verbose_name = _('Belongs Agency'))
    department = models.ForeignKey('Department',verbose_name = _('Belongs Department'),null=True)
    position = models.ForeignKey('Position',verbose_name = _('Belongs Position'),null=True)
    teacher = models.OneToOneField('Teacher',verbose_name = _('Staff'),null=True,related_name='postjob')
    status = models.PositiveSmallIntegerField(_('Status'),choices=STATUS_TYPE,null=True, blank=True,default=0)
    
    class Meta:
        verbose_name = _('post job')
        verbose_name_plural = _('post jobs')
        db_table = 'oa_postjob'
    
    def state(self):
        return "离职" if self.status else "在职"
    
    def save(self, *args, **kwargs):      
        if self.teacher.school_id != self.school_id:
            self.teacher.school_id = self.school_id
            self.teacher.save()
        super(PostJob, self).save(*args, **kwargs)
 
class Position(BaseModel, ActiveMixin, SoftDeleteMixin):
    creator = models.ForeignKey(User, related_name="+",verbose_name = _('creator'))
    name = models.CharField(_('Name'),max_length=60, blank=True)
    school = models.ForeignKey(School,verbose_name = _('agency'),related_name="positions")
    sort = models.IntegerField(null=True, blank=True)
    description = models.TextField(_('Description'),max_length=765, blank=True)
    
    class Meta:
        verbose_name = _('position')
        verbose_name_plural = _('positions')
        ordering = ['sort']
        db_table = 'oa_position'
        
    def __unicode__(self):
        return self.name
    
    def save(self, *args, **kwargs):      
        super(Position, self).save(*args, **kwargs)
        
    
class Department(BaseModel, ActiveMixin, SoftDeleteMixin):
    creator = models.ForeignKey(User, related_name="+",verbose_name = _('creator'))
    name = models.CharField(_('Name'),max_length=60, blank=True)
    school = models.ForeignKey(School,verbose_name = _('agency'),related_name="departments")
    charger = models.ForeignKey('Teacher',verbose_name = _('charger'),blank=True,null=True)
    telephone_one = models.CharField(_('Mobile one'), max_length=20, blank=True, validators=[validate_mobile_number])
    telephone_two = models.CharField(_('Mobile two'), max_length=20, blank=True, validators=[validate_mobile_number])
    fax = models.CharField(_('Fax'), max_length=20, blank=True)
    description = models.TextField(_('Description'),max_length=765, blank=True)
    
    class Meta:
        verbose_name = _('department')
        verbose_name_plural = _('departments')
        ordering = ['name']
        db_table = 'oa_department'
        
    def __unicode__(self):
        return self.name
    
    def save(self, *args, **kwargs):      
        super(Department, self).save(*args, **kwargs)


class SmsType(BaseModel, SoftDeleteMixin):
    name = models.CharField(_('Name'),max_length=120)
    description = models.TextField(_('Description'),max_length=765, blank=True)

    def __unicode__(self):
        return self.name

    class Meta:
        verbose_name = _('sms type')
        verbose_name_plural = _('sms types')
        db_table = 'kinger_sms_type'
        ordering = ('id',)
        
        
class Sms(BaseModel, ActiveMixin, SoftDeleteMixin):
    """
    type = 0   普通短信
    type = 2   消息转换
    type = 100 系统发送账号重置密码短信 
    type = 101 发送验证码短信
    """
    GROUP_TYPE = (
        (0, _('System')),
        (1, _('Notice')),
        )
    sender = models.ForeignKey(User, related_name="sender", null=True,verbose_name = _('sender'))
    receiver = models.ForeignKey(User, related_name="receiver",verbose_name = _('receiver'))
    mobile = models.CharField(_('Mobile'),max_length=20, blank=True)
    send_time = models.DateTimeField(auto_now_add=True)
    is_send = models.BooleanField(_('is send'),default=False)
    type = models.ForeignKey(SmsType,verbose_name = _('sms type'),null=True, blank=True)
    #type = models.IntegerField(null=True, blank=True,help_text="type =2时，短信从 消息转换过来 ")
    content = models.CharField(max_length=765, blank=True,verbose_name = _('content'))
    description = models.CharField(_('Description'),max_length=765, blank=True)

    objects = SmsManager()

    def __unicode__(self):
        return self.content

    def getMobile(self):
        profile = self.user.get_profile()
        return profile.mobile

    class Meta:
        ordering = ['-ctime']
        verbose_name = _('sms')
        verbose_name_plural = _('sms')

        
        
class Student(BaseModel, ActiveMixin, SoftDeleteMixin):

    GENDER_CHOICES = (
        (1, _('Male')),
        (2, _('Female')),
        )
    STATUS_TYPE = (
        (0, _('在园')),
        (1, _('离园')),
    )
    creator = models.ForeignKey(User, related_name="+",verbose_name = _('creator'))
    user = models.OneToOneField(User,verbose_name = _('user'))
    school = models.ForeignKey(School,verbose_name = _('school'))
    group = models.ForeignKey(Group, null=True, blank=True, related_name="students",verbose_name = _('school class'))

    name = models.CharField(_('Name'),max_length=90, validators=[validate_not_spaces])
    gender = models.PositiveSmallIntegerField(_('Gender'),
                                              choices=GENDER_CHOICES,
                                              blank=True,
                                              null=True)
    school_date = models.DateField(_('School date'),blank=True, null=True)
    timecard = models.CharField(_('timecard'),max_length=36, blank=True)
    birth_date = models.DateField(_('Birth date'), blank=True, null=True,\
        help_text=_("Date format: YYYY-MM-DD"))
    sn = models.CharField(max_length=36, blank=True)
    description = models.TextField(_('Description'), max_length=765, blank=True)
#     status = models.BooleanField(default=True)
    status = models.PositiveSmallIntegerField(_('Status'),choices=STATUS_TYPE,null=True, blank=True,default=0)
    pinyin = models.CharField(_('pinyin'), max_length=100, blank=True)
    send_time = models.DateTimeField(null=True,blank=True,verbose_name = _('last send time'))

    class Meta:
        verbose_name = _('student')
        verbose_name_plural = _('students')
        ordering = ['id']

    def __unicode__(self):
        
        return self.name

    def save(self, *args, **kwargs):      
        self.pinyin = Char.objects.trans(self.name)

        profile = self.user.get_profile()
        profile.realname = self.name
        profile.save()

        super(Student, self).save(*args, **kwargs)

    @property
    def age(self):
        return helpers.calculate_age(self.birth_date)

    def getMobile(self):
        mobile = ''
        try:
            profile = self.user.get_profile()
            mobile = profile.mobile
        except ObjectDoesNotExist:
            pass
        
        if not mobile:
            try:
                mobile = Guardian.objects.filter(student_id=self.id)[0].mobile
            except:
                pass
        return mobile
    
    def state(self):
        return "离园" if self.status else "在园"
    
    def getAvatar(self):
        avatar = ''
        try:
            profile = self.user.get_profile()
            avatar = profile.mugshot
        except ObjectDoesNotExist:
            pass
        return avatar

    def resetPasswordAndSendSms(self, pass_form=SetPasswordForm, sender=None):
        #
        try:
            user = self.user
        except ObjectDoesNotExist:
            return False

        new_password = User.objects.make_random_password(length=6,allowed_chars='0123456789')
        data = {'new_password1': new_password, 'new_password2': new_password}
        form = pass_form(user=user, data=data)

        if form.is_valid():
            form.save()
            mobile = self.getMobile()
            content = False
            if mobile:
                username = user.username
                content = u"尊敬的用户，您的登录帐号是:" + username + u",密码是:" + new_password+u"【"+ SITE_INFO.name + "】"
                content = u"尊敬的用户您好，欢迎使用【" + SITE_INFO.name + "】家园沟通应用，您的账号：" + username + u" 密码：" + new_password+u" 登入" + SITE_INFO.domain + "即刻体验,详情咨询：0755-86350888"
                userena_signals.password_complete.send(sender=None, user=user)
                # 记录到 sms表
                #sender = self.user
                receiver = self.user

                Sms.objects.create_send_account_sms(sender=sender, receiver=receiver, mobile=mobile, content=content)

        return content


##########
# 订阅功能 #
##########

# tile标签表
class TileTag(BaseModel,SoftDeleteMixin):
    name = models.CharField(_('Name'),max_length=120, null=True, blank=False, unique=True)
    description = models.TextField(_('Description'),max_length=765, blank=True)

    def __unicode__(self):
        return self.name

    class Meta:
        verbose_name = _('tile tag')
        verbose_name_plural = _('tile tags')


##########
# 瓦片功能 #
##########
class TileType(BaseModel, SoftDeleteMixin):
    name = models.CharField(_('Name'),max_length=120)
    description = models.TextField(_('Description'),max_length=765, blank=True)
    img = ThumbnailerImageField(_('tiletype.img'),
            blank=True,
            upload_to="tiletype",
            )

    def __unicode__(self):
        return self.name

    class Meta:
        verbose_name = _('tile type')
        verbose_name_plural = _('tile types')
        db_table = 'kinger_tile_type'
        ordering = ('id',)
        #unique_together = (('app_label', 'model'),)


class NewTileType(BaseModel, SoftDeleteMixin):
    name = models.CharField(_('Name'),max_length=120)
    description = models.TextField(_('Description'),max_length=765, blank=True)
    img = ThumbnailerImageField(_('tiletype.img'),
            blank=True,
            upload_to="tiletype",
            )
    def __unicode__(self):
        return self.name

    class Meta:
        verbose_name = _('new tile type')
        verbose_name_plural = _('new tile types')
        db_table = 'kinger_new_tile_type'
        ordering = ('id',)
        
        
class TileCategory(BaseModel, SoftDeleteMixin):
    name = models.CharField(_('Name'),max_length=120)
    description = models.TextField(_('Description'),max_length=765, blank=True)
    img = ThumbnailerImageField(_('TileCategory.img'),
            blank=True,
            upload_to="TileCategory",
            )
    parent = models.ForeignKey('self',null=True,blank=True,verbose_name = _('tile category parent'))

    LOOKUP_CHOICES = (
        (0, u'教师发布'),
        (1, u'后台推广'),
    )
    is_tips = models.IntegerField(_('is_tips'),default=0,choices=LOOKUP_CHOICES)
    sort = models.IntegerField(_('sort'),default=0)

    objects = TileCategoryManager()

    @property
    def is_parent(self):
        return self.parent_id == 0

    def __unicode__(self):
        return self.name

    def picture(self):
        url = helpers.media_path(self.img)
        if url:
            return '<img src='+url +' style="max-height: 100px; max-width:100px;">'
        else:
            return ''
    picture.allow_tags = True
    
    class Meta:
        verbose_name = _('tile category')
        verbose_name_plural = _('tile categorys')
        db_table = 'kinger_tile_category'
        ordering = ('sort','id',)
        #unique_together = (('app_label', 'model'),)
        

class NewTileCategory(BaseModel, SoftDeleteMixin):
    name = models.CharField(_('Name'),max_length=120)
    description = models.TextField(_('Description'),max_length=765, blank=True)
    img = ThumbnailerImageField(_('TileCategory.img'),
            blank=True,
            upload_to="TileCategory",
            )
    parent = models.ForeignKey('self',null=True,blank=True,verbose_name = _('tile category parent'))

    LOOKUP_CHOICES = ((0, u'成长档案'),(1, u'育儿频道'),(2, u'生命学堂'),(3, u'父母商城'),)
    is_tips = models.IntegerField(_('is_tips'),default=0,choices=LOOKUP_CHOICES)
    sort = models.IntegerField(_('sort'),default=0)

    objects = TileCategoryManager()

    def __unicode__(self):
        return self.name
    
    def is_parent(self):
        return self.parent_id == 0
    
    class Meta:
        verbose_name = _('new tile category')
        verbose_name_plural = _('new tile categorys')
        db_table = 'kinger_new_tile_category'
        ordering = ('sort','id',)


class Tile(BaseModel,Likeable, SoftDeleteMixin):
    creator = models.ForeignKey(User, related_name="+",verbose_name = _('creator'))
    user = models.ForeignKey(User, related_name="tiles",verbose_name = _('user'), null=True, blank=True, help_text='瓦片所属用户（跟班级一起为空表示所有用户，不可两者同时存在，适用于baby，推荐的瓦片范围控制）')
    group = models.ForeignKey(Group,null=True, blank=True,verbose_name = _('school class'), help_text='瓦片所属班级')
    rating = RatingField(range=5) # 5 possible rating values, 1-5
    type = models.ForeignKey(TileType,verbose_name = _('tile type'),default=0,blank=True,null=True)
    new_type = models.ForeignKey(NewTileType,verbose_name = _('tile type'),default=0,blank=True,null=True)
    category = models.ForeignKey(TileCategory,verbose_name = _('tile category'), default=0, blank=True, null=True)
    new_category = models.ForeignKey(NewTileCategory,verbose_name = _('tile category'), default=0, blank=True, null=True)
    title = models.CharField(_('title'),max_length=120)
    img = ThumbnailerImageFields(_('tile.img'),
            blank=True,validators=[validate_max_size],
#            upload_to='tile/' + str(datetime.datetime.strftime(datetime.datetime.now(),"%Y%m%d")),
            upload_to = upload_to_mugshot,help_text='请控制图片尺寸在大小500x300以上'
            )

    n_comments = models.IntegerField(_('n_comments'),default=0, blank=True,null=True)
    n_likers = models.IntegerField(_('n_likers'),default=0, blank=True)
    view_count = models.IntegerField(_('view_count'),default=0,blank=True,null=True)
    api_count = models.IntegerField(_('api_count'),default=0,blank=True,null=True)
    is_public = models.BooleanField(_('is_public'),default=False,help_text='公开则所有用户可见（包括未收费），非公开则家长用户的身份可见。')

    LOOKUP_CHOICES = ((0, u'成长档案'),(1, u'育儿频道'),(2, u'生命学堂'),(3, u'父母商城'),)
    is_tips = models.IntegerField(_('is_tips'),default=0,null=True,choices=LOOKUP_CHOICES)
   # is_tips = models.BooleanField(_('is_tips'),default=False)


    video = models.CharField(_('video'),max_length=255, blank=True)
    # 一个tile属于的chanle
    tags = models.ManyToManyField(TileTag, related_name="tiles", blank=True, null=True,verbose_name = _('tile tag'))

    description = models.TextField(_('Description'),max_length=765, blank=True)
    content = models.TextField(_('Content'),max_length=765, blank=True)
    url = models.CharField(_('Url'),max_length=255, blank=True)
    
    start_time = models.DateTimeField(null=True,blank=True,verbose_name = _('start time'),help_text='瓦片的开始时间，小于将不显示。为空默认保存为当前时间')
    end_time = models.DateTimeField(null=True,blank=True, help_text='瓦片的结束时间，大于将不显示。为空默认9999年')
    microsecond = models.DecimalField(_('Microsecond'),default=0.00, blank=True,null=True,max_digits=17,decimal_places=6)
    
    objects = TileManager()

    class Meta:
        permissions = (
            ('can_public_tiles', '发布推广内容'),
        )
        ordering = ['-microsecond']
        verbose_name = _('tile')
        verbose_name_plural = _('tiles')

    def __unicode__(self):
        return unicode(self.title)

    def save(self, *args, **kwargs):
        
        if not self.start_time:
            self.start_time = datetime.datetime.now()
        
        if not self.title:
            try:
                self.title = self.new_type.name
            except:
                pass
          
        start_time_change = False    
        if self.pk is not None:
            orig = Tile.objects.get(pk=self.pk)
            if orig.start_time != self.start_time:
                start_time_change = True
            
        if not self.microsecond or start_time_change:
            timetuple = time.mktime(self.start_time.timetuple())
            self.microsecond = D(str(int(timetuple)) + '.' + str(datetime.datetime.now().microsecond))
        
        if not self.end_time:
            self.end_time = datetime.date(9999,12,31)

        if not self.category_id:
            self.category_id = self.type_id
        
        if not self.id and self.img:
            try:
                url = self.img.url
                res = URL('http://' + SITE_INFO.domain + reverse('cron_make_tile_img')).post_async(img=self.img)
            except:
                pass
        
        category_pks = [4   ,5   ,6   ,7   ,8   ,10  ,11  , 12 ,13  ,14  ,15  ,16  ,17  ,21  ,22  ,23  ,101 ,102 ,9] 
        new_category_pks = [1131,1132,1133,1134,1135,1130,1110,1111,1112,1113,1114,1115,1116,1120,1121,1122,1136,1137,9]  
        
        if not self.category_id and self.new_category_id:
            if self.is_tips == 0:
                try:
                    order = new_category_pks.index(self.new_category_id)
                    self.category_id = category_pks[order]
                except:
                    self.category_id = 17
            else:
                self.category_id = 32
                     
        if not self.new_category_id and self.category_id:
            if self.is_tips == 0:
               try:
                   order = category_pks.index(self.category_id)
                   self.new_category_id = new_category_pks[order]
               except:
                   self.new_category_id = 1116
            else:
               self.new_category_id = 2000
        
        if not self.type_id and self.new_type_id:
            self.type_id = 103 if int(self.new_type_id) > 3 else self.new_type_id
         
        if not self.new_type_id and self.type_id:
            if int(self.type_id) in [1,2,3]:
                self.new_type_id = self.type_id    
            else:
                self.new_type_id = 5
        
        if self.is_tips != 0:
            self.user_id = None
            self.group_id = None
             
        super(Tile, self).save(*args, **kwargs)

    @property
    def pub_time(self):
        return self.start_time or self.ctime
    
    def picture(self):
        url = helpers.media_path(self.img)
        if url:
            return '<img src='+url +' style="max-height: 100px; max-width:100px;">'
        else:
            return ''
    picture.allow_tags = True
    
    def decade_create_time(self):
        return self.ctime.strftime('%Y-%m-%d %H:%M:%S')
    decade_create_time.short_description = '创建时间'
    decade_create_time.admin_order_field = 'ctime'

    def after_add_comments(self):
        ct = ContentType.objects.get_by_natural_key("kinger", "tile")
        n_comments = Comment.objects.filter(object_pk=self.id, content_type=ct) \
            .filter(is_removed=False, is_public=True).count()
        self.n_comments = n_comments
        
        # 或者 直接 count comments 表 where content_type = tile and object_pk = self.id and is_removed = 0
        #if self.n_comments < 0:
            #self.n_comments = 0
        #else:
            #self.n_comments = self.n_comments + 1
        self.save()

    def after_del_comments(self):
        ct = ContentType.objects.get_by_natural_key("kinger", "tile")
        n_comments = Comment.objects.filter(object_pk=self.id, content_type=ct) \
            .filter(is_removed=False, is_public=True).count()
        self.n_comments = n_comments
        #if self.n_comments > 0:
            #self.n_comments = self.n_comments - 1
        #else:
            #self.n_comments = 0
        self.save()

    def comments(self, limit=3):
        if self.n_comments > 0:
            return Comment.objects.for_model(self) \
                .filter(is_public=True).filter(is_removed=False) \
                .order_by("-id")[0:limit]
        else:
            return None

    def is_report(self):
        return self.new_type_id > 4 or self.new_type_id == 3

    def is_daily(self):
        return self.type_id == 9
    
    def is_content(self):
        if self.is_tips and self.content:
            return True
        else:
            return False
    
    def creat_user_last_tile(self, uid, last_tile_id):
        try:
#            last,create = UserLastTile.objects.get_or_create(user_id=uid)
#            print last,'last-----------------------------------------------'
#            last.last_tile_id = tile_id
#            last.save()
            last,create = UserLastTile.objects.get_or_create(user_id=uid)
            last_tile = Tile.objects.get(pk=last_tile_id)
            last.last_tile_id = last_tile_id
            if last_tile.is_tips == 0:
                last.baby_time = last_tile.microsecond
            else:
                last.edu_time = last_tile.microsecond
            last.save()
        except Exception, e:
            print e,'creat_user_last_tile-----------------'
            pass
#        num = UserLastTile.objects.filter(user_id=uid).count()
#        if not num:
#            p = UserLastTile(user_id=uid,last_tile_id=tile_id)
#            p.save()    
             
            
#客户端瓦片tag
class TileCreateTag(models.Model):

    tile = models.OneToOneField('Tile',verbose_name = _('tile'),null=True,related_name='tiletag')
    tag = models.CharField(_('tag'),max_length=120)
    
    class Meta:
        verbose_name = _('tile tag')
        verbose_name_plural = _('tile tags')
        db_table = 'kinger_tile_create_tag'
        
        
#瓦片访问者历史表
class TileVisitor(BaseModel,SoftDeleteMixin):
    visitor = models.ForeignKey(User, verbose_name = _('visitor'), null=True, blank=True)
    tile = models.ForeignKey(Tile,verbose_name = _('tile'), default=0, blank=True, null=True)
    visit_time = models.DateTimeField(null=True,blank=True)
    microsecond = models.DecimalField(_('Microsecond'),default=0.00, blank=True,null=True,max_digits=17,decimal_places=6)

    def __unicode__(self):
        return unicode(self.visitor)
    
    def save(self, *args, **kwargs):
        if not self.visit_time:
            self.visit_time = datetime.datetime.now()
        if not self.microsecond:
            timetuple = time.mktime(self.visit_time.timetuple())
            self.microsecond = D(str(int(timetuple)) + '.' + str(datetime.datetime.now().microsecond))
        super(TileVisitor, self).save(*args, **kwargs)

    class Meta:
        verbose_name = _('tile visitor')
        verbose_name_plural = _('tile visitors')
        db_table = 'kinger_tile_visitor'
        
                     
##########
# 预设内容 #
##########
# 读取活动食谱预设配置 ps：与 http://192.168.1.222/wiki/doku.php?id=api_tiles_get_event_setting 接口相关

class EventType(BaseModel, SoftDeleteMixin):
    GROUP_TYPE = (
        (0, _('Event')),
        (1, _('Cookbook')),
        )

    name = models.CharField(_('Name'),max_length=120)
    img = ThumbnailerImageField(_('event_setting.img'),
            blank=True,
            upload_to="event_setting",
            )
    # 属于活动或者食谱
    group = models.IntegerField(null=True, blank=True, choices=GROUP_TYPE,verbose_name = _('type'))
    _content = ""

    @property
    def content(self):
        return self._content

    @content.setter
    def content(self, value):
        self._content = value

    def __unicode__(self):
        return self.name

    class Meta:
        verbose_name = _('event type')
        verbose_name_plural = _('event types')

class EventSetting(BaseModel, SoftDeleteMixin):
    # 早餐，午餐，早点等等类型
    type = models.ForeignKey(EventType, related_name='settings',verbose_name = _('type'))
    content = models.TextField(_('Content'),max_length=765, null=False,)#blank=True,
    # 如果所在学校没有默认设置时，则读取school_id = 0 的设置
    school = models.ForeignKey(School, null=True, blank=True,verbose_name = _('school'))

    def __unicode__(self):
        return self.content

    class Meta:
        verbose_name = _('event setting')
        verbose_name_plural = _('event settings')

##########
# comment templater #
##########

class CommentTemplaterType(BaseModel, SoftDeleteMixin):
    name = models.CharField(_('Name'),max_length=120)
    description = models.CharField(_('Description'),max_length=765, blank=True)

    def __unicode__(self):
        return self.name
    class Meta:
        db_table = "kinger_comment_templatertype"
        verbose_name = _('comment templater type')
        verbose_name_plural = _('comment templater types')

class CommentTemplater(BaseModel, SoftDeleteMixin):
    # 早餐，午餐，早点等等类型
    type = models.ForeignKey(CommentTemplaterType, related_name='templaters')
    content = models.TextField(max_length=765, blank=True)
    #
    creator = models.ForeignKey(User, related_name="+",verbose_name = _('creator'))

    def __unicode__(self):
        return self.content
    class Meta:
        db_table = "kinger_comment_templater"
        verbose_name = _('comment templater')
        verbose_name_plural = _('comment templaters')


##########
# 导师相关 #
##########
class Mentor(BaseModel, ActiveMixin, SoftDeleteMixin):
    creator = models.ForeignKey(User, related_name="+",verbose_name = _('creator'))
    user = models.OneToOneField(User,verbose_name = _('user'),related_name="mentor")

    name = models.CharField(_('Teacher name'),max_length=60)
    nationality = models.CharField(_('Nationality'),max_length=60,blank=True)
    appellation = models.TextField(_('Appellation'),max_length=60,blank=True)
    description = models.TextField(_('Description'),max_length=765, blank=True)


    def __unicode__(self):
        return self.name

    def save(self, *args, **kwargs):

        profile = self.user.get_profile()
        profile.realname = self.name
        profile.is_mentor = True
        profile.save()

        super(Mentor, self).save(*args, **kwargs)

    def getAvatar(self):
        profile = self.user.get_profile()
        return profile.mugshot

    def getMobile(self):
        mobile = ''
        try:
            profile = self.user.get_profile()
            mobile = profile.mobile
        except ObjectDoesNotExist:
            pass
        return mobile

    class Meta:
        verbose_name = _('mentor')
        verbose_name_plural = _('mentors')
        ordering = ['name']

##########
# 客服人员 #
##########
class Waiter(BaseModel, ActiveMixin, SoftDeleteMixin):
    creator = models.ForeignKey(User, verbose_name = _('creator'),related_name="waiter_creator",)
    user = models.OneToOneField(User,verbose_name = _('user'),related_name="waiter")

    name = models.CharField(_('Waiter name'),max_length=60)
    appellation = models.TextField(_('Appellation'),max_length=60)
    description = models.TextField(_('Description'),max_length=765, blank=True)


    def __unicode__(self):
        return self.name

    def save(self, *args, **kwargs):

        profile = self.user.get_profile()
        profile.realname = self.name
        profile.is_waiter = True
        profile.save()

        super(Waiter, self).save(*args, **kwargs)

    def getAvatar(self):
        profile = self.user.get_profile()
        return profile.mugshot

    def getMobile(self):
        mobile = ''
        try:
            profile = self.user.get_profile()
            mobile = profile.mobile
        except ObjectDoesNotExist:
            pass
        return mobile

    class Meta:
        verbose_name = _('waiter')
        verbose_name_plural = _('waiters')
        ordering = ['name']


class Device(BaseModel):
    user = models.ForeignKey(User, related_name='device',verbose_name = _('user'))
    token = models.CharField(unique=True, max_length=64)

    def __unicode__(self):
        return " %s's device" % self.user.username

    class Meta:
        verbose_name = _('device')
        verbose_name_plural = _('devices')

from APNSWrapper import *
import binascii

class ApplePushNotification(BaseModel):
    creator = models.ForeignKey(User, related_name="+",verbose_name = _('creator'))
    #user = models.OneToOneField(User,verbose_name = _('user'),related_name="pushto")

    alert = models.TextField(_('alert'))
    badge = models.IntegerField(_('badge'),max_length=30,blank=True,null=True,default=1)
    sound = models.CharField(_('sound'),max_length=30,blank=True)

    tile = models.OneToOneField(Tile,verbose_name = _('tile'),null=True,blank=True)

    is_send = models.BooleanField(_('is_send'),default=False)    
    send_time = models.DateTimeField(_('send time'),null=True,blank=True)
   
    def __unicode__(self):
        return self.alert

    class Meta:
        verbose_name = _('ApplePushNotification')
        verbose_name_plural = _('ApplePushNotifications')

        ordering = ['-ctime']


class CleanCharField(models.CharField):
        """Django's default form handling drives me nuts wrt trailing
        spaces.  http://code.djangoproject.com/attachment/ticket/6362
        """
        def clean(self, value, *args, **kwargs):
            if value is None:
                value = u''
            value = value.strip()
            value = super(models.CharField, self).clean(value, *args, **kwargs)
            return value

class UserLastTile(models.Model):
    user = models.OneToOneField(User, related_name='last_tile',verbose_name = _('user'))
    last_tile_id = models.IntegerField(max_length=11,blank=True)
    baby_time = models.DecimalField(_('baby time'),default=0.00, blank=True,null=True,max_digits=17,decimal_places=6)
    edu_time = models.DecimalField(_('edu time'),default=0.00, blank=True,null=True,max_digits=17,decimal_places=6)

class ChangeUsername(models.Model):
    user = models.ForeignKey(User, related_name="user")
    name = models.CharField(_('Name'),max_length=30)
    edittime = models.DateTimeField(auto_now=True)
    class Meta:
        verbose_name = _('ChangeUsername')
        verbose_name_plural = _('ChangeUsernames')

        ordering = ['-edittime']

##########
# 食谱 #
##########

class Cookbook(BaseModel):
    # 食谱发布者
    creator = models.ForeignKey(User, verbose_name = _('creator'))

    # 食谱条目
    breakfast = models.CharField(_('breakfast'),max_length=100,blank=True)
    light_breakfast = models.CharField(_('light breakfast'),max_length=100,blank=True)

    lunch = models.CharField(_('lunch'),max_length=100,blank=True)
    light_lunch = models.CharField(_('light lunch'),max_length=100,blank=True)

    dinner = models.CharField(_('dinner'),max_length=100,blank=True)
    light_dinner = models.CharField(_('light dinner'),max_length=100,blank=True)

    # 食谱时间
    date = models.DateField(_('cookbook date'),)

    school = models.ForeignKey(School, verbose_name = _('school'),null=True,blank=True)
    group = models.ForeignKey(Group, verbose_name = _('group'),null=True,blank=True)
    is_send = models.BooleanField(default=False, blank=False)


    objects = CookbookManager()
    
    @classmethod
    def get_items(cls):
        item = [
            'breakfast',
            'light_breakfast',
            'lunch',
            'light_lunch',
            'dinner',
            'light_dinner'
        ]
        return item
    
    def get_student(self):
        if self.group:
            return self.group.students.all()
        if self.school:
            return self.school.student_set.all()
        
    def __unicode__(self):
        cookbook = self.breakfast or self.lunch or self.dinner
        return cookbook

    class Meta:
        unique_together = (('school','date'),('group','date'))
        verbose_name = _('cookbook')
        verbose_name_plural = _('cookbook')


##########
# 食谱种类 #
##########
class CookbookType(BaseModel, SoftDeleteMixin):

    name = models.CharField(_('Name'),max_length=120)
    cname = models.CharField(_('Cname'),max_length=120)
    img = ThumbnailerImageField(_('CookbookType.img'),
            blank=True,
            upload_to="CookbookType",
            )

    def __unicode__(self):
        return self.name

    class Meta:
        verbose_name = _('cook book type')
        verbose_name_plural = _('cook book types')


##############
# 食谱已读状态 #
##############
class CookbookRead(BaseModel):

    user = models.ForeignKey(User,verbose_name = _('user'))
    cookbook = models.ForeignKey(Cookbook,verbose_name = _('cookbook'))
    date = models.DateField(_('cookbook date'),)
    is_read = models.BooleanField(default=False, blank=False)
    read_at = models.DateTimeField(_("read at"),null=True,blank=True)
    is_send = models.BooleanField(default=False, blank=False)
    objects = CookbookreadManager()

    def __unicode__(self):
        return unicode(self.user)

    class Meta:
        verbose_name = _('cookbook read')
        verbose_name_plural = _('cookbook reads')
        db_table = 'kinger_cookbook_read'
        
        ordering = ['-ctime']
        
        
##########
# 学校食谱设置 #
##########

class CookbookSet(BaseModel):
    school = models.OneToOneField(School, verbose_name = _('school'))

    # 食谱条目显示与否
    breakfast = models.BooleanField(default=True)
    light_breakfast = models.BooleanField(default=True)

    lunch = models.BooleanField(default=True)
    light_lunch = models.BooleanField(default=True)

    dinner = models.BooleanField(default=True)
    light_dinner = models.BooleanField(default=True)

    objects = CookbookSetManager()

    class Meta:
        verbose_name = _('cookbook set')
        verbose_name_plural = _('cookbook set')

##########
# 验证短信 #
##########

class VerifySms(BaseModel, ActiveMixin, SoftDeleteMixin):
    """
    验证码有效期30分钟，重置成功后，成为未激活状态。
    """
    sms = models.OneToOneField(Sms, verbose_name = _('sms'))

    user = models.ForeignKey(User, verbose_name = _('user'))
    mobile = models.CharField(_('Mobile'),max_length=20)

    content = models.CharField(max_length=765, blank=True)
    vcode = models.CharField(_('vcode'),max_length=20)

    objects = VerifySmsManager()

    class Meta:
        verbose_name = _('verify sms')
        verbose_name_plural = _('verify sms')

#############
#发送班级消息  #
#############

class MessageToClass(BaseModel, SoftDeleteMixin):
    group = models.ForeignKey(Group, verbose_name = _('group'),null=True,blank=True)
    user = models.ForeignKey(User, verbose_name = _('user'), null=True, blank=True)
    content = models.CharField(max_length=765, blank=True)
    
    class Meta:
        verbose_name = _('message to calss')
        verbose_name_plural = _('message to calsses')
        db_table = 'kinger_message_to_class'
        ordering = ['-ctime']


class RelevantStaff(BaseModel, SoftDeleteMixin):
    name = models.CharField(_('name'),max_length=60)
    mobile = models.CharField(_('Mobile'),max_length=20,blank=True)
    email = models.EmailField(_('e-mail address'), blank=True)
    send_mentor = models.BooleanField(_('send_mentor'),default=False)
    send_waiter = models.BooleanField(_('send_waiter'),default=False)
    
    def save(self, *args, **kwargs):
        if not self.mobile and self.email:
            send_mentor = False
            send_waiter = False
            
        super(RelevantStaff, self).save(*args, **kwargs)
    
    def __unicode__(self):
        return str(self.name)
    
    class Meta:
        verbose_name = _('relevant staff')
        verbose_name_plural = _('relevant staffs')
        db_table = 'kinger_relevant_staff'
    
    
############
# 拼音码表 #
############
class Char(models.Model):
    cn = models.CharField(max_length=60,blank=True)
    en =  models.CharField(max_length=60,blank=True,default='')

    objects = CharManager()

    class Meta:
        verbose_name = _('char')
        verbose_name_plural = _('char')
        

class Access_log(BaseModel):
    user = models.ForeignKey(User, verbose_name = _('user'), null=True, blank=True)   
    send_time = models.DateTimeField(_('send time'),auto_now_add=True)
    type = models.IntegerField(null=True, blank=True)
    url = models.CharField(_('Url'),max_length=255, blank=True)
   
    class Meta:
        verbose_name = _('access log')
        verbose_name_plural = _('access logs')

        ordering = ['-send_time']
        

class Comment_relation(BaseModel):
    target_object = models.ForeignKey(Comment, verbose_name = _('target object'), related_name='target_object')
    action_object = models.ForeignKey(Comment, verbose_name = _('action object'), related_name='action_object')
   
    class Meta:
        verbose_name = _('comment relation')
        verbose_name_plural = _('comment relations')
        
        ordering = ['-ctime']
        
        
class Activity(BaseModel,SoftDeleteMixin):
    creator = models.ForeignKey(User, related_name="+",verbose_name = _('creator'))
    user = models.ForeignKey(User, verbose_name = _('user'), null=True, blank=True)
    group = models.ForeignKey(Group, verbose_name = _('group'),null=True,blank=True)
    start_time = models.DateTimeField(null=True,blank=True)
    description = models.TextField(_('Description'),max_length=765, blank=True)
    microsecond = models.DecimalField(_('Microsecond'),default=0.00, blank=True,null=True,max_digits=17,decimal_places=6)
    
    def save(self, *args, **kwargs):
        if not self.start_time:
            self.start_time = datetime.datetime.now()
        if not self.microsecond:
            timetuple = time.mktime(self.start_time.timetuple())
            self.microsecond = D(str(int(timetuple)) + '.' + str(datetime.datetime.now().microsecond))
        super(Activity, self).save(*args, **kwargs)
    
    def __unicode__(self):
        return str(self.start_time)
    
    class Meta:
        verbose_name = _('activity')
        verbose_name_plural = _('activities')
        
        ordering = ['-start_time', '-microsecond']


class Schedule(BaseModel,SoftDeleteMixin):
    name = models.CharField(_('Name'),max_length=120,null=True,blank=True)
    user = models.ForeignKey(User, related_name="schedules",verbose_name = _('user'))
    start_time = models.DateTimeField(null=True,blank=True,verbose_name = _('start time'))
    group = models.ForeignKey(Group, verbose_name = _('group'))
    src = models.FileField(upload_to=upload_to_mugshot,verbose_name = _('schedule src'))

    def __unicode__(self):
        return str(self.name)
    
    def save(self, *args, **kwargs):
        if not self.start_time:
            self.start_time = datetime.datetime.now()
        if not self.name:
            self.name = self.src.name
        super(Schedule, self).save(*args, **kwargs)
    
    class Meta:
        verbose_name = _('schedule')
        verbose_name_plural = _('schedules')
        ordering = ['-start_time']



class TileToActivity(BaseModel):
    tile = models.ForeignKey(Tile, verbose_name = _('tile'),null=True,blank=True)
    active = models.ForeignKey(Activity, verbose_name = _('active'), null=True, blank=True)
    
    class Meta:
        verbose_name = _('tile to activity')
        verbose_name_plural = _('tile to activities')
        db_table = 'kinger_tile_to_activity'
        ordering = ['-ctime']
        

#日常记录访问者历史表
class DailyRecordVisitor(BaseModel,SoftDeleteMixin):
    visitor = models.ForeignKey(User, verbose_name = _('visitor'), null=True, blank=True)
    target_content_type = models.ForeignKey(ContentType, related_name='visitor_target')
    target_object_id = models.CharField(max_length=255)
    target = generic.GenericForeignKey('target_content_type', 'target_object_id')
    visit_time = models.DateTimeField(null=True,blank=True)
    microsecond = models.DecimalField(_('Microsecond'),default=0.00, blank=True,null=True,max_digits=17,decimal_places=6)
    objects = DailyRecordVisitorManager()

    def __unicode__(self):
        return unicode(self.visitor)
    
    def save(self, *args, **kwargs):
        if not self.visit_time:
            self.visit_time = datetime.datetime.now()
        if not self.microsecond:
            timetuple = time.mktime(self.visit_time.timetuple())
            self.microsecond = D(str(int(timetuple)) + '.' + str(datetime.datetime.now().microsecond))
        super(DailyRecordVisitor, self).save(*args, **kwargs)

    class Meta:
        verbose_name = _('daily record visitor')
        verbose_name_plural = _('daily record visitors')
        db_table = 'kinger_daily_record_visitor'
        

class ImageWithMd5(BaseModel,SoftDeleteMixin):
    src = models.CharField(verbose_name = _('image src'),max_length=120,null=True,blank=True)
    md5 = models.CharField(verbose_name = _('image md5'),max_length=64,null=True,blank=True)
    
    def __unicode__(self):
        return str(self.md5)
    
    def save(self, *args, **kwargs):
        super(ImageWithMd5, self).save(*args, **kwargs)
    
    class Meta:
        verbose_name = _('imagewithmd5')
        verbose_name_plural = _('imagewithmd5s')
        

class WebSite(BaseModel, ActiveMixin, SoftDeleteMixin):
    
    creator = models.ForeignKey(User,verbose_name = _('creator'))
    admins = models.ManyToManyField(User, related_name="manageWebsites", null=True,verbose_name = _('website admins'))
    school = models.ForeignKey("School",verbose_name = _('school'))
    domain = models.CharField(_('domain'), max_length=100)
    name = models.CharField(_('Name'),max_length=60, blank=True)
    logo = ThumbnailerImageField(_('Logo'),blank=True,upload_to=upload_to_mugshot,null=True)
#    charger = models.ForeignKey('Teacher',verbose_name = _('charger'),blank=True,null=True)
    charger = models.CharField(_('Name'),max_length=60, blank=True)
    telephone = models.CharField(_('telephone'), max_length=20, blank=True, \
        validators=[validate_telephone_number],null=True)
    email = models.EmailField(_('e-mail'), blank=True,null=True)
    STATUS_CHOICES = ((0, u'停用'),(1, u'启用'),)
    status = models.IntegerField(_('status'),default=1,choices=STATUS_CHOICES)
    TYPE_CHOICES = ((0, u'二级域名'),(1, u'独立域名'),)
    type = models.IntegerField(_('status'),default=0,choices=TYPE_CHOICES)
    description = models.TextField(_('Description'),max_length=765, blank=True)

    def __unicode__(self):
        return self.name

    class Meta:
        verbose_name = _('website')
        verbose_name_plural = _('websites')
        ordering = ['-ctime','name']
        db_table = 'oa_website'
    
    def save(self, *args, **kwargs):
        super(WebSite, self).save(*args, **kwargs)
 
        
class WebSiteAccess(BaseModel, SoftDeleteMixin):
    user = models.ForeignKey(User,verbose_name = _('user'),null=True,blank=True)
    website = models.ForeignKey('WebSite',verbose_name = _('website'),null=True,blank=True)
    access_time = models.DateTimeField(null=True,blank=True)
    
    class Meta:
        verbose_name = _('website access')
        verbose_name_plural = _('website accesses')
        db_table = 'oa_website_access'
        ordering = ['-access_time']
    
    def save(self, *args, **kwargs):
        if not self.access_time:
            self.access_time = datetime.datetime.now()
        super(WebSiteAccess, self).save(*args, **kwargs)
    
    
class PartCategory(BaseModel, SoftDeleteMixin):
    name = models.CharField(_('Name'),max_length=120)
    description = models.TextField(_('Description'),max_length=765, blank=True)
    parent = models.ForeignKey('self',null=True,blank=True,verbose_name = _('part category parent'))

    @property
    def is_parent(self):
        return self.parent_id == 0

    def __unicode__(self):
        return self.name

    class Meta:
        verbose_name = _('part category')
        verbose_name_plural = _('part categorys')
        db_table = 'oa_part_category'
        

class Part(BaseModel, ActiveMixin, SoftDeleteMixin):
    creator = models.ForeignKey(Teacher,verbose_name = _('creator'),blank=True, null=True)
    category = models.ForeignKey('PartCategory',verbose_name = _('part category'), default=0, blank=True, null=True)
    title = models.CharField(_('title'),max_length=120,blank=True)
    content = models.TextField(_('Content'),max_length=765, blank=True)
    attachment = models.FileField(upload_to=upload_to_mugshot,\
                    verbose_name = _('part attachment'),blank=True, null=True)
    video = models.FileField(upload_to=upload_to_mugshot,\
                    verbose_name = _('part video'),blank=True, null=True,validators=[validate_max_video_size])
    video_type = models.IntegerField(_('video type'),default=0,choices=((0, u'手动上传'),(1, u'输入链接'),))
    url = models.CharField(_('Url'),max_length=255, blank=True)
    TYPE_CHOICES = ((0, u'草稿'),(1, u'发布'),(2, u'置顶'),)
    type = models.IntegerField(_('type'),default=1,choices=TYPE_CHOICES)
    school = models.ForeignKey("School",verbose_name = _('school'),blank=True, null=True)
    site = models.ForeignKey("WebSite",verbose_name = _('site'))
    is_show = models.BooleanField(default=True, blank=False)
    view_count = models.IntegerField(_('view_count'),default=0,blank=True,null=True)
    
    def __unicode__(self):
        return self.title

    class Meta:
        verbose_name = _('part')
        verbose_name_plural = _('parts')
        db_table = 'oa_part'
#        ordering = ['-type','-ctime']
        

class StarFigure(BaseModel, ActiveMixin, SoftDeleteMixin):
    user = models.OneToOneField(User,verbose_name = _('user'),related_name='figure')
    content = models.TextField(_('Content'),max_length=765, blank=True)
    is_show = models.BooleanField(default=False, blank=False)
    class Meta:
        verbose_name = _('start figure')
        verbose_name_plural = _('start figures')
        db_table = 'oa_starfigure'
        
               
class Photo(BaseModel, SoftDeleteMixin):
    creator = models.ForeignKey(User, related_name="+",verbose_name = _('creator'))
    album = models.ForeignKey('Album',verbose_name = _('album'), blank=True, null=True)
    title = models.CharField(_('title'),max_length=120)
    img = ThumbnailerImageField(_('albums.img'),blank=True,upload_to=upload_to_mugshot)
    description = models.TextField(_('Description'),max_length=765, blank=True)
    is_show = models.BooleanField(default=False, blank=False)

    class Meta:
        verbose_name = _('photo')
        verbose_name_plural = _('photos')
        db_table = 'oa_photo'
        ordering = ['-ctime','-is_show']

    def __unicode__(self):
        return unicode(self.description) or unicode(self.title)

    def save(self, *args, **kwargs):
        super(Photo, self).save(*args, **kwargs)
        

class Album(BaseModel, ActiveMixin, SoftDeleteMixin):
    creator = models.ForeignKey(User, related_name="album",verbose_name = _('creator'))
    name = models.CharField(_('Name'),max_length=120)
    category = models.ForeignKey('PartCategory',verbose_name = _('part category'), default=0, blank=True, null=True)
    site = models.ForeignKey("WebSite",verbose_name = _('site'), blank=True, null=True)
    description = models.TextField(_('Description'),max_length=765, blank=True)
    class Meta:
        verbose_name = _('album')
        verbose_name_plural = _('albums')
        db_table = 'oa_album'
        
class Link(BaseModel, ActiveMixin, SoftDeleteMixin):
    title = models.CharField(_('Name'),max_length=120)
    site = models.ForeignKey("WebSite",verbose_name = _('site'), blank=True, null=True)
    url = models.CharField(_('Url'),max_length=255, blank=True)
    description = models.TextField(_('Description'),max_length=765, blank=True)
    class Meta:
        verbose_name = _('link')
        verbose_name_plural = _('links')
        db_table = 'oa_link'
        

class MailBox(BaseModel, ActiveMixin, SoftDeleteMixin):
    title = models.CharField(_('Name'),max_length=120)
    site = models.ForeignKey("WebSite",verbose_name = _('site'), blank=True, null=True)
    body = models.TextField(_('body'),max_length=765, blank=True)
    user = models.ForeignKey(User, related_name="mailbox",verbose_name = _('user'),null=True)
#    sender = models.ForeignKey(User,related_name="mailboxSender",verbose_name = _('user'))
    name = models.CharField(_('Name'),max_length=120)
    email = models.EmailField(_('e-mail'), blank=True)
    phone = models.CharField(_('phone'), max_length=20, blank=True)
    address = models.CharField(_('Address'), max_length=150, blank=True)
    is_read = models.BooleanField(default=False, blank=False)
    class Meta:
        verbose_name = _('mailbox')
        verbose_name_plural = _('mailboxs')
        db_table = 'oa_mailbox'
        

class Template(BaseModel, ActiveMixin, SoftDeleteMixin):
    title = models.CharField(_('Name'),max_length=120)
    site = models.ForeignKey("WebSite",verbose_name = _('site'), blank=True, null=True)
    img = ThumbnailerImageField(_('template img'),blank=True,upload_to=upload_to_mugshot)
    is_show = models.BooleanField(default=False, blank=False)
    
    class Meta:
        verbose_name = _('template')
        verbose_name_plural = _('templates')
        db_table = 'oa_template'


class DocumentCategory(BaseModel, ActiveMixin, SoftDeleteMixin):
    name = models.CharField(_('Name'),max_length=120)
    description = models.TextField(_('Description'),max_length=765, blank=True)
    school = models.ForeignKey("School",verbose_name = _('school'),null=True,blank=True)
    parent = models.ForeignKey('self',null=True,blank=True,verbose_name = _('document category parent'))

    @property
    def is_parent(self):
        return self.parent_id == 0

    def __unicode__(self):
        return self.name

    class Meta:
        verbose_name = _('document category')
        verbose_name_plural = _('document categorys')
        db_table = 'oa_document_category'
        

class Attachment(BaseModel, ActiveMixin, SoftDeleteMixin):
    name = models.CharField(_('Name'),max_length=120)
    file = models.FileField(upload_to=upload_to_mugshot)
    
    def __unicode__(self):
        if self.name:
            return self.name
        else:
            return str(self.file.name)
    
    class Meta:
        verbose_name = _('attachment')
        verbose_name_plural = _('attachment')
        db_table = 'oa_attachment'
        

class Document(BaseModel, ActiveMixin, SoftDeleteMixin):
    title = models.CharField(_('Name'),max_length=120)
    files = models.ManyToManyField('Attachment', related_name='docs')
    school = models.ForeignKey("School",verbose_name = _('school'),null=True,blank=True)
    category = models.ForeignKey('DocumentCategory',verbose_name = _('document category'), default=0, blank=True, null=True)
    LEVEL_CHOICES = ((0, u'普通'),(1, u'重要'),(2, u'机密'),)
    level = models.IntegerField(_('level'),default=0,choices=LEVEL_CHOICES)
    sender = models.ForeignKey(User,verbose_name = _('sender'))
    content = models.TextField(_('Content'),max_length=765, blank=True)
    send_msg = models.BooleanField(_('send smg'),default=False)
    msg_body = models.TextField(_('msg body'),max_length=765, blank=True)
    is_submit = models.BooleanField(_('is_submit'),default=False)
    STATUS_CHOICES = ((0, u'已发'),(1, u'草稿'),(2, u'作废'),)
    status = models.IntegerField(_('status'),default=0,choices=STATUS_CHOICES)
    remark = models.TextField(_('remark'),max_length=765, blank=True)
    inscribed = models.CharField(_('Name'),max_length=120)
    send_time = models.DateTimeField(null=True,blank=True,verbose_name = _('last send time'))
    is_approvaled = models.BooleanField(_('is_approvaled'),default=False)
    
    def __unicode__(self):
        return self.title

    class Meta:
        verbose_name = _('document')
        verbose_name_plural = _('documents')
        ordering = ['-mtime',]
        db_table = 'oa_document'
    
    def save(self, *args, **kwargs):
        if not self.send_time:
            self.send_time = datetime.datetime.now()
        if not self.send_msg:
            self.msg_body = ''
        if not self.is_submit:
            self.remark = ''
        super(Document, self).save(*args, **kwargs)


class DocumentReceiver(BaseModel, ActiveMixin, SoftDeleteMixin):
    user = models.ForeignKey(User, related_name="doc_receiver",verbose_name = _('user'))
    document = models.ForeignKey("Document",verbose_name = _('document'),\
                related_name="receivers",null=True,blank=True)
    send_time = models.DateTimeField(null=True,blank=True,verbose_name = _('last send time'))
    is_read = models.BooleanField(_('is_read'),default=False)
    is_send = models.BooleanField(_('is_send'),default=False)
    
    class Meta:
        verbose_name = _('document receiver')
        verbose_name_plural = _('document receivers')
        ordering = ['-mtime',]
        db_table = 'oa_document_receiver'
        
    
class DocumentApproval(BaseModel, ActiveMixin, SoftDeleteMixin):
    sender = models.ForeignKey(User,verbose_name = _('sender'),related_name="approval_sender")
    document = models.ForeignKey("Document",verbose_name = _('document'),null=True,blank=True)
    approvaler = models.ForeignKey(User,verbose_name = _('approvaler'),related_name="approvaler")
    receiver = models.ForeignKey(User,verbose_name = _('receiver'),related_name="approval_receiver",null=True,blank=True)
    STATUS_CHOICES = ((0, u'待审批'),(1, u'发出'),(2, u'发回'),(3, u'送审'),(4, u'已撤回'),(5, u'作废'),)
    status = models.IntegerField(_('status'),default=0,choices=STATUS_CHOICES)
    send_time = models.DateTimeField(null=True,blank=True,verbose_name = _('last send time'))
    remark = models.TextField(_('remark'),max_length=765, blank=True)
    
    class Meta:
        verbose_name = _('document approval')
        verbose_name_plural = _('document approvals')
        ordering = ['-send_time','-mtime']
        db_table = 'oa_document_approval'
        

class Registration(BaseModel, ActiveMixin, SoftDeleteMixin):
    school = models.ForeignKey("School",verbose_name = _('school'),null=True,blank=True)
    group = models.ForeignKey("Group",verbose_name = _('group'),null=True,blank=True)
    name = models.CharField(_('Name'),max_length=120)
    GENDER_CHOICES = ((1, _('Male')),(2, _('Female')),)
    gender = models.PositiveSmallIntegerField(_('Gender'),\
                    choices=GENDER_CHOICES,blank=True,null=True)
    hometown = models.CharField(_('Hometown'), max_length=150, blank=True)
    nation = models.CharField(_('Nation'), max_length=120, blank=True)
    address = models.CharField(_('Address'), max_length=150, blank=True)
    birth_date = models.DateField(_('Birth date'), blank=True, null=True)
    credential = models.CharField(_('credential'), max_length=150, blank=True)
    drug_allergy = models.CharField(_('drug allergy'), max_length=200, blank=True)
    nursery_time = models.DateTimeField(null=True,blank=True,verbose_name = _('nursery time'))
    examination = models.CharField(_('examination'), max_length=120, blank=True)
    disease_history = models.CharField(_('disease history'), max_length=400, blank=True)
#    charger = models.ForeignKey(User,verbose_name = _('charger'),blank=True, null=True)
    charger = models.CharField(_('Name'),max_length=60, blank=True)
    description = models.TextField(_('Description'),max_length=765, blank=True)
    signature = models.CharField(_('signature'),max_length=120)
    STATUS_CHOICES = ((0, _('待录取')),(1, _('未获录取')),(2, _('已录取')),\
                      (3, _('过期')),(4, _('待面试')),)
    status = models.PositiveSmallIntegerField(_('Status'),\
                    choices=STATUS_CHOICES,blank=True,null=True,default=0)
    
    send_msg = models.BooleanField(_('send smg'),default=False)
    msg_body = models.TextField(_('msg body'),max_length=765, blank=True)
    
    
    def __unicode__(self):
        return self.name

    class Meta:
        verbose_name = _('registration')
        verbose_name_plural = _('registrations')
        ordering = ['-ctime']
        db_table = 'oa_registration'
        
        
class TemporaryFiles(BaseModel):
    fileid = models.TextField(_('fileid'),max_length=765, blank=True)
    path =  models.TextField(_('path'),max_length=765, blank=True)
    
    class Meta:
        verbose_name = _('temporary file')
        verbose_name_plural = _('temporary files')
    
class TinymceImage(BaseModel, ActiveMixin, SoftDeleteMixin):
    img = ThumbnailerImageField(_('img'),blank=True,upload_to=upload_to_mugshot,null=True)

    class Meta:
        verbose_name = _('tinymce_image')
        verbose_name_plural = _('tinymce_images')
        db_table = 'oa_tinymce_image'
    
    def save(self, *args, **kwargs):
        super(TinymceImage, self).save(*args, **kwargs)
        
#class TileImage(BaseModel, ActiveMixin, SoftDeleteMixin):
#    img = ThumbnailerImageField(_('img'),blank=True,upload_to=upload_to_mugshot,null=True)
#
#    class Meta:
#        verbose_name = _('tile_image')
#        verbose_name_plural = _('tile_images')
#        db_table = 'kinger_tile_image'
#    
#    def save(self, *args, **kwargs):
#        super(TileImage, self).save(*args, **kwargs)

class SupplyCategory(BaseModel, ActiveMixin, SoftDeleteMixin):
    name = models.CharField(_('Name'),max_length=120)
    description = models.TextField(_('Description'),max_length=765, blank=True)
    school = models.ForeignKey(School,verbose_name = _('school'),null=True,blank=True)
    parent = models.ForeignKey('self',null=True,blank=True,verbose_name = _('supply category parent'))

    @property
    def is_parent(self):
        return self.parent_id == 0

    def __unicode__(self):
        return self.name

    class Meta:
        verbose_name = _('supply category')
        verbose_name_plural = _('supply categorys')
        db_table = 'oa_supply_category'
        
        
class Provider(BaseModel, ActiveMixin, SoftDeleteMixin):
    name = models.CharField(_('Name'),max_length=120)
    creator = models.ForeignKey(User,verbose_name = _('creator'),null=True,blank=True)
    charger = models.CharField(_('Name'),max_length=60, blank=True)
    description = models.TextField(_('Description'),max_length=765, blank=True)
    school = models.ForeignKey(School,verbose_name = _('school'),null=True,blank=True)
    mobile = models.CharField(_('Mobile'), max_length=20, blank=True, \
        validators=[validate_mobile_telephone])
    address = models.CharField(_('Address'), max_length=150, blank=True)
    remark = models.TextField(_('remark'),max_length=765, blank=True) 
    
    def __unicode__(self):
        return self.name

    class Meta:
        verbose_name = _('provider')
        verbose_name_plural = _('providers')
        ordering = ['-mtime',]
        db_table = 'oa_provider'


class Supply(BaseModel, ActiveMixin, SoftDeleteMixin):
    name = models.CharField(_('Name'),max_length=120)
    parent = models.ForeignKey('self',null=True,blank=True,verbose_name = _('supply parent'))
    creator = models.ForeignKey(User,verbose_name = _('creator'),null=True,blank=True)
    school = models.ForeignKey(School,verbose_name = _('school'),null=True,blank=True)
    provider = models.ForeignKey('Provider',verbose_name = _('provider'),null=True,blank=True)
    category = models.ForeignKey('SupplyCategory',verbose_name = _('supply category'), default=0, blank=True, null=True)
    num = models.IntegerField(_('Number'),default=0,blank=True,null=True)
    min = models.IntegerField(_('Number'),default=0,blank=True,null=True)
    stime = models.DateTimeField(null=True,blank=True,verbose_name = _('send time'))
    remark = models.TextField(_('remark'),max_length=765, blank=True) 
    is_show = models.BooleanField(_('is show'),default=True)#物资显示控制，替代删除物资
    
    def __unicode__(self):
        return self.name

    class Meta:
        verbose_name = _('supply')
        verbose_name_plural = _('supplies')
        ordering = ['-mtime','name']
        db_table = 'oa_supply'
        
    def get_parent(self):
        if self.parent_id == 0:
            return self
        else:
            return self.parent
    
    def save(self, *args, **kwargs):
        if not self.stime:
            self.stime = datetime.datetime.now()
        self.num = 0 if not self.num else self.num
        self.min = 0 if not self.min else self.min
        if not self.parent_id:
            self.parent_id = 0
        
        super(Supply, self).save(*args, **kwargs)
     
        
class SupplyRecord(BaseModel, ActiveMixin, SoftDeleteMixin):
    supply = models.ForeignKey('Supply',verbose_name = _('supply'),null=True,blank=True)
    parent = models.ForeignKey('self',null=True,blank=True,verbose_name = _('record parent'),related_name='subrecords')
    creator = models.ForeignKey(User,verbose_name = _('creator'),null=True,blank=True)
    school = models.ForeignKey(School,verbose_name = _('school'),null=True,blank=True)
    provider = models.ForeignKey('Provider',verbose_name = _('provider'),null=True,blank=True)
    num = models.IntegerField(_('Number'),default=0,blank=True,null=True)
    back = models.IntegerField(_('Number'),default=0,blank=True,null=True)
    stime = models.DateTimeField(null=True,blank=True,verbose_name = _('send time'))
    remark = models.TextField(_('remark'),max_length=765, blank=True) 
    TYPE_CHOICES = ((0, _('录入')),(1, _('领取')),)
    type = models.PositiveSmallIntegerField(_('type'),choices=TYPE_CHOICES,blank=True,null=True,default=0)
    document = models.ForeignKey("Material",verbose_name = _('document'),\
                related_name="supplyrecords",null=True,blank=True)
    regist = models.CharField(_('Name'),max_length=120)
    STATUS_CHOICES = ((0, _('有效')),(1, _('无效')),)
    status = models.PositiveSmallIntegerField(_('status'),choices=STATUS_CHOICES,default=0)
    
    def __unicode__(self):
        try:
            return self.supply.name
        except:
            return ''

    class Meta:
        verbose_name = _('supply record')
        verbose_name_plural = _('supply records')
        db_table = 'oa_supply_record'
        ordering = ['-stime']
        
    def get_parent(self):
        if self.parent_id == 0:
            return self
        else:
            return self.parent
    
    def save(self, *args, **kwargs):
        if not self.stime:
            self.stime = datetime.datetime.now()
        super(SupplyRecord, self).save(*args, **kwargs)
   
   
class SupplyReback(BaseModel, ActiveMixin, SoftDeleteMixin):
    regist = models.CharField(_('Name'),max_length=120)
    back_time = models.DateTimeField(null=True,blank=True,verbose_name = _('back time'))
    record = models.ForeignKey('SupplyRecord',null=True,blank=True,verbose_name = _('record back'),related_name='rebacks')
    remark = models.TextField(_('remark'),max_length=765, blank=True) 
    num = models.IntegerField(_('Number'),default=0,blank=True,null=True)
    
    class Meta:
        verbose_name = _('supply reback')
        verbose_name_plural = _('upply rebacks')
        db_table = 'oa_supply_reback'
        ordering = ('-back_time',)
    
    def save(self, *args, **kwargs):
        self.back_time = datetime.datetime.now()
        super(SupplyReback, self).save(*args, **kwargs)


class DiskCategory(BaseModel, ActiveMixin, SoftDeleteMixin):
    name = models.CharField(_('Name'),max_length=120)
    user = models.ForeignKey(User,verbose_name = _('creator'),null=True,blank=True)
    description = models.TextField(_('Description'),max_length=765, blank=True)
    school = models.ForeignKey(School,verbose_name = _('school'),null=True,blank=True)
    parent = models.ForeignKey('self',null=True,blank=True,verbose_name = _('disk category parent'),default=0)
    TYPE_CHOICES = ((0, u'个人类别'),(1, u'幼儿园类别'),(2, u'集团类别'),)
    type = models.IntegerField(_('type'),default=0,choices=TYPE_CHOICES)
    order = models.IntegerField(_('Number'),default=0,blank=True,null=True)

    @property
    def is_parent(self):
        return self.parent_id == 0

    def __unicode__(self):
        return self.name

    class Meta:
        verbose_name = _('disk category')
        verbose_name_plural = _('disk categorys')
        db_table = 'oa_disk_category'
        ordering = ['order']


class Disk(BaseModel, ActiveMixin, SoftDeleteMixin):
    title = models.CharField(_('Name'),max_length=120)
    creator = models.ForeignKey(User,verbose_name = _('creator'),null=True,blank=True)
    files = models.ManyToManyField(Attachment, related_name='disks')
#    file = models.FileField(upload_to=upload_to_mugshot,\
#                    verbose_name = _('file'),blank=True, null=True)
    category = models.ForeignKey('DiskCategory',verbose_name = _('disk category'), default=0, blank=True, null=True)
    content = models.TextField(_('Content'),max_length=765, blank=True)
    school = models.ForeignKey(School,verbose_name = _('school'),null=True,blank=True)
    parent = models.ForeignKey('self',null=True,blank=True,default=0,verbose_name = _('disk parent'),related_name='subdisks')
    
    def __unicode__(self):
        return self.title
    
    class Meta:
        verbose_name = _('disk')
        verbose_name_plural = _('disks')
        db_table = 'oa_disk'
        ordering = ['-mtime','-ctime']

class Material(BaseModel, ActiveMixin, SoftDeleteMixin):
    title = models.CharField(_('Name'),max_length=120)
    files = models.ManyToManyField(Attachment, related_name='mats')
    school = models.ForeignKey(School,verbose_name = _('school'),null=True,blank=True)
    LEVEL_CHOICES = ((0, u'普通'),(1, u'重要'),(2, u'机密'),)
    level = models.IntegerField(_('level'),default=0,choices=LEVEL_CHOICES)
    TYPE_CHOICES = ((0, u'采购'),(1, u'领取'),)
    type = models.IntegerField(_('type'),default=0,choices=TYPE_CHOICES)
    sender = models.ForeignKey(User,verbose_name = _('sender'))
    content = models.TextField(_('Content'),max_length=765, blank=True)
    send_msg = models.BooleanField(_('send smg'),default=False)
    msg_body = models.TextField(_('msg body'),max_length=765, blank=True)
    is_submit = models.BooleanField(_('is_submit'),default=False)
    STATUS_CHOICES = ((0, u'已发'),(1, u'草稿'),(2, u'作废'),)
    status = models.IntegerField(_('status'),default=0,choices=STATUS_CHOICES)
    remark = models.TextField(_('remark'),max_length=765, blank=True)
    inscribed = models.CharField(_('Name'),max_length=120)
    send_time = models.DateTimeField(null=True,blank=True,verbose_name = _('last send time'))
    is_approvaled = models.BooleanField(_('is_approvaled'),default=False)
    description = models.TextField(_('Description'),max_length=765, blank=True)
    
    def __unicode__(self):
        return self.title

    class Meta:
        verbose_name = _('material')
        verbose_name_plural = _('materials')
        ordering = ['-mtime',]
        db_table = 'oa_material'
    
    def save(self, *args, **kwargs):
        if not self.send_time:
            self.send_time = datetime.datetime.now()
        if not self.send_msg:
            self.msg_body = ''
        if not self.is_submit:
            self.remark = ''
        super(Material, self).save(*args, **kwargs)
        

class MaterialReceiver(BaseModel, ActiveMixin, SoftDeleteMixin):
    user = models.ForeignKey(User, related_name="mat_receiver",verbose_name = _('user'))
    document = models.ForeignKey("Material",verbose_name = _('document'),\
                related_name="receivers",null=True,blank=True)
    send_time = models.DateTimeField(null=True,blank=True,verbose_name = _('last send time'))
    is_read = models.BooleanField(_('is_read'),default=False)
    is_send = models.BooleanField(_('is_send'),default=False)
    
    class Meta:
        verbose_name = _('material receiver')
        verbose_name_plural = _('material receivers')
        ordering = ['-mtime',]
        db_table = 'oa_material_receiver'
        
    
class MaterialApproval(BaseModel, ActiveMixin, SoftDeleteMixin):
    sender = models.ForeignKey(User,verbose_name = _('sender'),related_name="appr_sender")
    document = models.ForeignKey("Material",verbose_name = _('document'),null=True,blank=True)
    approvaler = models.ForeignKey(User,verbose_name = _('approvaler'),related_name="appr_approvaler")
    receiver = models.ForeignKey(User,verbose_name = _('receiver'),related_name="appr_receiver",null=True,blank=True)
    STATUS_CHOICES = ((0, u'待审批'),(1, u'发出'),(2, u'发回'),(3, u'送审'),(4, u'已撤回'),(5, u'作废'),)
    status = models.IntegerField(_('status'),default=0,choices=STATUS_CHOICES)
    send_time = models.DateTimeField(null=True,blank=True,verbose_name = _('last send time'))
    remark = models.TextField(_('remark'),max_length=765, blank=True)
    
    class Meta:
        verbose_name = _('material approval')
        verbose_name_plural = _('material approvals')
        ordering = ['-send_time','-mtime']
        db_table = 'oa_material_approval'

class MaterialApply(BaseModel, SoftDeleteMixin):
    supply = models.ForeignKey("Supply",verbose_name = _('supply'),null=True,blank=True)
    num = models.IntegerField(_('num'),default=0,blank=True,null=True)
    deal = models.IntegerField(_('num'),default=0,blank=True,null=True)
    document = models.ForeignKey("Material",verbose_name = _('document'),null=True,blank=True,related_name='applies')
    regist = models.CharField(_('Name'),max_length=120)
    school = models.ForeignKey(School,verbose_name = _('school'),null=True,blank=True)
    
    class Meta:
        verbose_name = _('material apply')
        verbose_name_plural = _('material applies')
        db_table = 'oa_material_apply'
        ordering = ['-ctime']
    
    def __unicode__(self):
        try:
            return self.supply.name
        except:
            pass
        

class TileRecommend(BaseModel, SoftDeleteMixin):
    tile = models.ForeignKey("Tile",verbose_name = _('tile'))
    stime = models.DateTimeField(null=True,blank=True,verbose_name = _('send time'))
    remark = models.TextField(_('remark'),max_length=765, blank=True) 
    order = models.IntegerField(_('Order'),blank=True,default=0,help_text='数值越大排位越靠前')
    
    class Meta:
        verbose_name = _('tile recommend')
        verbose_name_plural = _('tile Recommends')
        ordering = ['-order','-stime']
        db_table = 'kinger_tile_recommend'
        
    def picture(self):
        try:
            url = helpers.media_path(self.tile.img)
            if url:
                return '<img src='+url +' style="max-height: 100px; max-width:100px;">'
            else:
                return ''
        except:
            return ''
    picture.allow_tags = True
    
#    def tile_id(self):
#        return '<a href="' + str(SITE_INFO.domain) + 'admin/kinger/tile/' + str(self.tile.id) + '" target="_blank">' + str(self.tile.id) + '</a>'
#    tile_id.short_description = '瓦片id'
#    tile_id.admin_order_field = 'tile_id'
#    tile_id.allow_tags = True
    
    def decade_create_time(self):
        return self.stime.strftime('%Y-%m-%d %H:%M:%S')
    decade_create_time.short_description = '创建时间'
    decade_create_time.admin_order_field = 'ctime'
    
    def save(self, *args, **kwargs):
        if not self.stime:
            self.stime = datetime.datetime.now()
        super(TileRecommend, self).save(*args, **kwargs)
    
    
class Announcement(BaseModel, ActiveMixin, SoftDeleteMixin):
    title = models.CharField(_('Name'),max_length=120)
#    LEVEL_CHOICES = ((0, u'普通'),(1, u'重要'),(2, u'机密'),)
#    level = models.IntegerField(_('level'),default=0,choices=LEVEL_CHOICES)
    content = models.TextField(_('Content'),max_length=765, blank=True)
    is_show = models.BooleanField(_('is_show'),default=False)
    description = models.TextField(_('Description'),max_length=765, blank=True)
    
    def __unicode__(self):
        return self.title
    
    class Meta:
        verbose_name = _('announcement')
        verbose_name_plural = _('announcements')
        ordering = ['-ctime',]
    
    def save(self, *args, **kwargs):
        super(Announcement, self).save(*args, **kwargs)
        
        
class Source(BaseModel, ActiveMixin, SoftDeleteMixin):
    title = models.CharField(_('Name'),max_length=120)
    creator = models.ForeignKey(User, related_name="adder",verbose_name = _('creator'),null=True,blank=True)
    group = models.ForeignKey("Group",verbose_name = _('group'))
    tile = models.ForeignKey("Tile",verbose_name = _('tile'))
    img = ThumbnailerImageFields(_('tile.img'),
                blank=True,validators=[validate_max_size],
                upload_to = upload_to_mugshot,help_text='请控制图片尺寸在大小500x300以上'
            )
    
    def __unicode__(self):
        return self.title
    
    class Meta:
        verbose_name = _('Source')
        verbose_name_plural = _('Sources')
        ordering = ['-mtime',]
        db_table = 'growth_source'
    
    def save(self, *args, **kwargs):
        if not self.title:
            self.title = self.tile.title
        if not self.img:
            self.img = self.tile.img
        super(Source, self).save(*args, **kwargs)
    
    
    