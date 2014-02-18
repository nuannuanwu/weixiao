# -*- coding: utf-8 -*-

from django.forms import ModelForm, CharField, PasswordInput
from django import forms
from bootstrap.forms import BootstrapForm, Fieldset, BootstrapMixin
from kinger.models import Agency,Department,Position,School,Group,Teacher,PostJob,\
            Student,Guardian,BirthControl,Role,WorkGroup,WebSite,Part,Album,\
            PartCategory,Photo,Link,DocumentCategory,Document,StarFigure,MailBox,Registration
from kinger.profiles.models import Profile
from django.utils.translation import ugettext as _
from kinger.validators import validate_mobile_number,validate_telephone_number
from django.contrib.auth.models import User
from userena import settings as userena_settings
from userena.utils import get_profile_model
from userena.contrib.umessages.fields import CommaSeparatedUserField
from userena.contrib.umessages.models import Message, MessageRecipient
import datetime
from kinger import settings
from django.contrib.auth.forms import PasswordChangeForm
from captcha.fields import CaptchaField
from oa import helpers
import re


class AgencyForm(BootstrapMixin, ModelForm):
    class Meta:
        model = Agency
        fields = ("name", "description")

        layout = (
            Fieldset("",
                "name","description"),
            )

    def __init__(self, *args, **kwargs):
        super(AgencyForm, self).__init__(*args, **kwargs)
        
    def save(self, *args, **kwargs):
        rs = super(AgencyForm, self).save(*args, **kwargs)
        return rs
 

class DepartmentForm(BootstrapMixin, ModelForm):
    class Meta:
        model = Department
        fields = ("name","charger","telephone_one","telephone_two","fax","description","school")

        layout = (
            Fieldset("",
                "name","charger","telephone_one","telephone_two","fax","description","school"),
            )
    telephone_one = forms.CharField('telephone_one', help_text=_('validate mobile number required.'), \
        validators=[validate_telephone_number],required=False)
    telephone_two = forms.CharField('telephone_two', help_text=_('validate mobile number required.'), \
        validators=[validate_telephone_number],required=False)
    charger = forms.ModelChoiceField(queryset=Teacher.objects, required=False)

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user') if kwargs else None
        super(DepartmentForm, self).__init__(*args, **kwargs)
        instance = getattr(self, 'instance', None)
        self.fields['name'].required = True

        if user and helpers.get_schools(user):
            manage_school_pks = [_school.id for _school in helpers.get_schools(user)]
            self.fields['charger'].queryset = Teacher.objects.filter(school__pk__in=manage_school_pks)

    def save(self, *args, **kwargs):
        rs = super(DepartmentForm, self).save(*args, **kwargs)
        return rs


class PositionForm(BootstrapMixin, ModelForm):
    class Meta:
        model = Position
        fields = ("name","sort","description","school")

        layout = (
            Fieldset("",
                "name","sort","description","school"),
            )

    def __init__(self, *args, **kwargs):
        super(PositionForm, self).__init__(*args, **kwargs)
        self.fields['name'].required = True

    def save(self, *args, **kwargs):
        rs = super(PositionForm, self).save(*args, **kwargs)
        return rs
    

class SchoolForm(BootstrapMixin, ModelForm):
    class Meta:
        model = School
        fields = ("name","short_name","type","city","area")

        layout = (
            Fieldset("",
                "name","short_name","type","city","area"),
            )

    def __init__(self, *args, **kwargs):
        super(SchoolForm, self).__init__(*args, **kwargs)
        instance = getattr(self, 'instance', None)
        self.fields['name'].required = True

    def save(self, *args, **kwargs):
        rs = super(SchoolForm, self).save(*args, **kwargs)
        return rs


class ClassForm(BootstrapMixin, ModelForm):
    class Meta:
        model = Group
        fields = ("name","type","grade","headteacher","school")

        layout = (
            Fieldset("",
                "name","type","grade","headteacher","school"),
            )

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user') if kwargs else None
        super(ClassForm, self).__init__(*args, **kwargs)
        instance = getattr(self, 'instance', None)

        if user and helpers.get_schools(user):
            manage_school_pks = [_school.id for _school in helpers.get_schools(user) if not _school.parent_id==0]
            print manage_school_pks,'pppppppppppp'
            self.fields['headteacher'].queryset = Teacher.objects.filter(school__pk__in=manage_school_pks)

    def save(self, *args, **kwargs):
        rs = super(ClassForm, self).save(*args, **kwargs)
        return rs
    

#class TeacherUserForm(BootstrapForm):
class TeacherUserForm(BootstrapMixin, ModelForm):
    class Meta:
        model = User
        fields = ("username","password")
        layout = (
            Fieldset("",
                "username","password"),
            )
    username = forms.RegexField(regex=r'^\w+$',
                                max_length=30,
                                widget=forms.TextInput({'class': 'required'}),
                                label=_("Username"),
                                error_messages={'invalid': _('Username must contain only letters, numbers and underscores.')})
    password = forms.CharField(label=_("Password"),
                                   widget=forms.TextInput)
    def __init__(self, *args, **kwargs):
        super(TeacherUserForm, self).__init__(*args, **kwargs)
        instance = getattr(self, 'instance', None)
        if instance:
            self.fields['password'].required = False
        
    def clean_username(self):
        """
        Validate that the username is alphanumeric and is not already in use.
        Also validates that the username is not listed in
        ``USERENA_FORBIDDEN_USERNAMES`` list.

        """
        try:
            User.objects.get(username__iexact=self.cleaned_data['username'])
        except User.DoesNotExist:
            pass
        else:
            if not self.instance:
                raise forms.ValidationError(_('This username is already taken.'))
            else:
                if self.instance.username != self.cleaned_data['username']:
                    raise forms.ValidationError(_('This username is already taken.'))
        if self.cleaned_data['username'].lower() in userena_settings.USERENA_FORBIDDEN_USERNAMES:
            raise forms.ValidationError(_('This username is not allowed.'))
        return self.cleaned_data['username']
    
    def save(self, *args, **kwargs):
        rs = super(TeacherUserForm, self).save(*args, **kwargs)
        return rs
    
    def clean_password(self):
        """
        Validates that the password field is correct.
        """
        password = self.cleaned_data["password"]
        return password


class UserProfileForm(forms.ModelForm):
    """ Base form used for fields that are always required """
    first_name = forms.CharField(label=_(u'First name'),
                                 max_length=30,
                                 required=False)
    last_name = forms.CharField(label=_(u'Last name'),
                                max_length=30,
                                required=False)
    realname = forms.CharField(label=_(u'Real name'),
                                max_length=30,
                                required=True)

    def __init__(self, *args, **kw):
        super(UserProfileForm, self).__init__(*args, **kw)
        instance = getattr(self, 'instance', None)
        new_order = self.fields.keyOrder[:-3]
        new_order.insert(0, 'first_name')
        new_order.insert(1, 'last_name')
        self.fields.keyOrder = new_order

    class Meta:
        model = get_profile_model()
        exclude = ['user','privacy']

    def save(self, force_insert=False, force_update=False, commit=True):
        profile = super(UserProfileForm, self).save(commit=commit)
        user = profile.user
        user.first_name = profile.realname or self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']
        user.save()

        return profile
    

class PostJobForm(BootstrapMixin, ModelForm):
    
    class Meta:
        model = PostJob
        fields = ("school","department","position","status")
        layout = (
            Fieldset("",
                "school","department","position","status"),
            )
    def __init__(self, *args, **kwargs):
        try:
            user = kwargs.pop('user') 
        except:
            user = None
        super(PostJobForm, self).__init__(*args, **kwargs)
        self.fields['school'].required = True
        self.fields['position'].required = False
        self.fields['department'].required = False
        instance = getattr(self, 'instance', None)
        
#         self.fields['department'].queryset = Department.objects.none()
#         self.fields['position'].queryset = Position.objects.none()
        if user:
            if helpers.get_schools(user):
                manage_school_pks = [_school.id for _school in helpers.get_schools(user)]
                self.fields['school'].queryset = School.objects.filter(pk__in=manage_school_pks)
                self.fields['department'].queryset = Department.objects.filter(school_id__in=manage_school_pks)
                self.fields['position'].queryset = Position.objects.filter(school_id__in=manage_school_pks)
#            else:
#                school = user.teacher.school
#                self.fields['school'].queryset = School.objects.filter(id=school.id)
    
    def save(self, *args, **kwargs):
        rs = super(PostJobForm, self).save(*args, **kwargs)
        return rs


class OaStudentForm(BootstrapMixin, ModelForm):
    class Meta:
        model = Student
        fields = ("school", "group", "school_date", "timecard", "status", "birth_date")

        layout = (
            Fieldset("",
                "school", "group", "school_date", "timecard", "status", "birth_date"),
            )
    
    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user') if kwargs else None
        super(OaStudentForm, self).__init__(*args, **kwargs)
        self.fields['school_date'].required = False
        instance = getattr(self, 'instance', None)
         
        if user:
            manage_school_pks = [_school.id for _school in helpers.get_schools(user) if not _school.parent_id==0]
            self.fields['school'].queryset = School.objects.filter(pk__in=manage_school_pks)
            self.fields['group'].queryset = Group.objects.filter(school__pk__in=manage_school_pks).exclude(type=3)

    def clean_name(self):
        return self.cleaned_data['name'].strip()

    def save(self, *args, **kwargs):
        
        rs = super(OaStudentForm, self).save(*args, **kwargs)
        return rs


class GuardianForm(BootstrapMixin, ModelForm):
    
    class Meta:
        model = Guardian
        fields = ("name","relation","mobile","office_phone","other_phone","office_email","other_email","address","unit")
        layout = (
            Fieldset("",
                "name","relation","mobile","office_phone","other_phone","office_email","other_email","address","unit"),
            )
    def __init__(self, *args, **kwargs):
        super(GuardianForm, self).__init__(*args, **kwargs)
        self.empty_permitted = False
        self.fields['name'].required = False
        self.fields['mobile'].required = False
#        self.fields['address'].required = True
        instance = getattr(self, 'instance', None)
    
    def save(self, *args, **kwargs):
        rs = super(GuardianForm, self).save(*args, **kwargs)
        return rs


class RegistGuardianForm(BootstrapMixin, ModelForm):
    
    class Meta:
        model = Guardian
        fields = ("name","relation","mobile","office_phone","other_phone","office_email","other_email","address","unit")
        layout = (
            Fieldset("",
                "name","relation","mobile","office_phone","other_phone","office_email","other_email","address","unit"),
            )
    def __init__(self, *args, **kwargs):
        super(RegistGuardianForm, self).__init__(*args, **kwargs)
        self.empty_permitted = False
        self.fields['name'].required = True
        self.fields['mobile'].required = True
        self.fields['relation'].required = True
        self.fields['unit'].required = True
        instance = getattr(self, 'instance', None)
    
    def save(self, *args, **kwargs):
        rs = super(RegistGuardianForm, self).save(*args, **kwargs)
        return rs


class BirthControlForm(BootstrapMixin, ModelForm):
    
    class Meta:
        model = BirthControl
        fields = ("is_single","childnum","order","overtbirth","is_pay")
        layout = (
            Fieldset("",
                "is_single","childnum","order","overtbirth","is_pay"),
            )
    def __init__(self, *args, **kwargs):
        super(BirthControlForm, self).__init__(*args, **kwargs)
        instance = getattr(self, 'instance', None)
    
    def save(self, *args, **kwargs):
        rs = super(BirthControlForm, self).save(*args, **kwargs)
        return rs
    

class RoleForm(BootstrapMixin, ModelForm):
    
    class Meta:
        model = Role
        fields = ("name","description")
        layout = (
            Fieldset("",
                "name","description"),
            )
    def __init__(self, *args, **kwargs):
        super(RoleForm, self).__init__(*args, **kwargs)
        instance = getattr(self, 'instance', None)
    
    def save(self, *args, **kwargs):
        rs = super(RoleForm, self).save(*args, **kwargs)
        return rs
    

class WorkGroupForm(BootstrapMixin, ModelForm):
    
    class Meta:
        model = WorkGroup
        fields = ("name","description")
        layout = (
            Fieldset("",
                "name","description"),
            )
    def __init__(self, *args, **kwargs):
        super(WorkGroupForm, self).__init__(*args, **kwargs)
        instance = getattr(self, 'instance', None)
    
    def save(self, *args, **kwargs):
        rs = super(WorkGroupForm, self).save(*args, **kwargs)
        return rs


class MessageForm(forms.Form):

    body = forms.CharField(label=_("Message"),
                           widget=forms.Textarea({'class': 'message'}),
                           required=True)
    timing = forms.DateTimeField(required=False)
    toself = forms.BooleanField()
    emergency = forms.BooleanField()
    receivers = []
    
    def __init__(self, *args, **kwargs):
        try:
            self.receivers = kwargs.pop('recipients')
        except:
            self.receivers = []
        super(MessageForm, self).__init__(*args, **kwargs)
        instance = getattr(self, 'instance', None)
        self.fields['emergency'].required = False
        self.fields['toself'].required = False

    def save(self, sender):
        """
        Save the message and send it out into the wide world.

        :param sender:
            The :class:`User` that sends the message.

        :param parent_msg:
            The :class:`Message` that preceded this message in the thread.

        :return: The saved :class:`Message`.

        """
        now = datetime.datetime.now()
        to_user_list = self.receivers
        
        body = self.cleaned_data['body']
        timing = self.cleaned_data['timing']
        toself = self.cleaned_data['toself']
        emergency = self.cleaned_data['emergency']
        type = 1 if emergency else 0
        try:
            timing = timing if timing > now else now
        except:
            timing = now
        if toself and not sender in to_user_list:
            to_user_list.append(sender)
#        if not toself and sender in to_user_list:
#            to_user_list.remove(sender)
        
        msg = Message.objects.send_oa_message(sender,to_user_list,body,timing,type)
 
        return msg


class WebSiteForm(BootstrapMixin, ModelForm):
    
    inst = None
    class Meta:
        model = WebSite
        fields = ("name","domain","logo","telephone","charger","email","status","type")
        layout = (
            Fieldset("",
                  "name","domain","logo","telephone","charger","email","status","type"),
            )
    def __init__(self, *args, **kwargs):
        super(WebSiteForm, self).__init__(*args, **kwargs)
        self.fields['name'].required = True
        self.fields['domain'].required = True
        instance = getattr(self, 'instance', None)
        self.inst = instance
        
    def clean(self):
        cleaned_data = self.cleaned_data
        type = cleaned_data.get("type")
        domain = cleaned_data.get("domain")
        if not self.inst and type == 0:
            match = re.findall(r'[^a-zA-Z0-9]',domain)
            if match or re.findall(r'[0-9]',domain):
                self._errors["domain"] = self.error_class(["请输入正确的域名"])
        
        if not self.inst and type == 1:
            match = re.findall(r'^([^\s]*?.)+[a-zA-Z]{2,6}$',domain)
            l = domain.split('.')
            if len(l) < 2 or len(l[:1] > 4):
                self._errors["msg_body"] = self.error_class(["请输入正确的域名"])
            else:
                for d in l:
                    match = re.findall(r'[^a-zA-Z0-9]',d)
                    if match:
                        self._errors["domain"] = self.error_class(["请输入正确的域名"])
                        break
        return cleaned_data
    
    def save(self, *args, **kwargs):
        rs = super(WebSiteForm, self).save(*args, **kwargs)
        return rs
     
     
class PartForm(BootstrapMixin, ModelForm):
        
    class Meta:
        model = Part
        fields = ("title", "content", "type","creator",'video', "attachment","video_type","url","is_show")

        layout = (
            Fieldset("",
                 "title", "content", "type","creator",'video', "attachment","video_type","url","is_show"),
            )
        
    class Media:
        js = (
              settings.STATIC_URL + 'media/js/tinymce/jscripts/tiny_mce/tiny_mce.js',
              settings.STATIC_URL + 'media/js/textareas.js',
         )
    
    def __init__(self, *args, **kwargs):
        try:
            category = kwargs.pop('category')
        except:
            category = None
        try:
            user = kwargs.pop('user')
        except:
            user = None
        super(PartForm, self).__init__(*args, **kwargs)
        instance = getattr(self, 'instance', None)
        self.fields['video_type'].required = False
        
        if user:
            manage_school_pks = [_school.id for _school in helpers.get_schools(user)]
            self.fields['creator'].queryset = Teacher.objects.filter(school__pk__in=manage_school_pks)
        if instance and instance.id:
            self.fields['video'].widget.template_with_initial = u'%(input)s'
            self.fields['attachment'].widget.template_with_initial = u'%(input)s'
            
        if category and category.id == 12:
            self.fields['content'].required = False
        else:
            self.fields['content'].required = True
            
        self.fields['creator'].required = False
        self.fields['type'].required = False
         
        if category and category.id == 4:
            self.fields['title'].required = True
#            self.fields['creator'].required = True
        
        if category and category.id == 19:
            self.fields['title'].required = True
#            self.fields['creator'].required = True
    
    def save(self, *args, **kwargs):
        rs = super(PartForm, self).save(*args, **kwargs)
        return rs
  

class AlbumForm(BootstrapMixin, ModelForm):
    """"""
    class Meta:
        model = Album
        fields = ('name', 'description',)

        layout = (
            Fieldset("",
                'name', 'description'),
            )

    def __init__(self, *args, **kwargs):
        super(AlbumForm, self).__init__(*args, **kwargs)
        instance = getattr(self, 'instance', None)
            

class PhotoForm(BootstrapMixin, ModelForm):

    class Meta:
        model = Photo
        fields = ("description", "img")

        layout = (
            Fieldset("",
                 "description", "img"),
            )
    
    def __init__(self, *args, **kwargs):
        super(PhotoForm, self).__init__(*args, **kwargs)
        instance = getattr(self, 'instance', None)
#         self.fields['img'].required = True
#        self.fields['description'].required = True

class LinkForm(BootstrapMixin, ModelForm):

    class Meta:
        model = Link
        fields = ("title", "url")

        layout = (
            Fieldset("",
                 "title", "url"),
            )
    
    def __init__(self, *args, **kwargs):
        super(LinkForm, self).__init__(*args, **kwargs)
        instance = getattr(self, 'instance', None)
        self.fields['title'].required = True
        self.fields['url'].required = True
        


class DocumentCategoryForm(BootstrapMixin, ModelForm):

    class Meta:
        model = DocumentCategory
        fields = ("name","parent")

        layout = (
            Fieldset("",
                 "name","parent"),
            )
    
    def __init__(self, *args, **kwargs):
        super(DocumentCategoryForm, self).__init__(*args, **kwargs)
        instance = getattr(self, 'instance', None)
        self.fields['name'].required = True
    
    def save(self, *args, **kwargs):
        rs = super(DocumentCategoryForm, self).save(*args, **kwargs)
        return rs
    

class DocumentForm(BootstrapMixin, ModelForm):
    
    insc = None
    class Meta:
        model = Document
        fields = ("title", "category","level","content","send_msg","msg_body","is_submit","remark","status","inscribed","send_time")

        layout = (
            Fieldset("",
                 "title", "category","level","content","send_msg","msg_body","is_submit","remark","status","inscribed","send_time"),
            )
    
    class Media:
        js = (
              settings.STATIC_URL + 'media/js/tinymce/jscripts/tiny_mce/tiny_mce.js',
              settings.STATIC_URL + 'media/js/textareas.js',
         )
    
    def __init__(self, *args, **kwargs):
        super(DocumentForm, self).__init__(*args, **kwargs)
        instance = getattr(self, 'instance', None)
        self.insc = instance
        self.fields['title'].required = True
        self.fields['content'].required = True
        self.fields['level'].required = True
        self.fields['category'].required = True
        self.fields['inscribed'].required = True
        self.fields['send_time'].required = True
        
    def clean(self):
        cleaned_data = self.cleaned_data
#        is_submit = cleaned_data.get("is_submit")
#        if self.insc.id and is_submit and not cleaned_data.get("remark"):
#            self._errors["remark"] = self.error_class(["这个字段是必填项。"])
            
        send_msg = cleaned_data.get("send_msg")
        if send_msg and not cleaned_data.get("msg_body"):
            self._errors["msg_body"] = self.error_class(["这个字段是必填项。"])
        return cleaned_data
        
        
class StarFigureForm(BootstrapMixin, ModelForm):
        
    class Meta:
        model = StarFigure
        fields = ("content", "is_show")

        layout = (
            Fieldset("",
                 "content", "is_show"),
            )
        
    class Media:
        js = (
              settings.STATIC_URL + 'media/js/tinymce/jscripts/tiny_mce/tiny_mce.js',
              settings.STATIC_URL + 'media/js/textareas.js',
         )
    
    def __init__(self, *args, **kwargs):
        super(StarFigureForm, self).__init__(*args, **kwargs)
        instance = getattr(self, 'instance', None)
        
    def save(self, *args, **kwargs):
        rs = super(StarFigureForm, self).save(*args, **kwargs)
        return rs
    
    
class MailBoxForm(BootstrapMixin, ModelForm):
        
    captcha = CaptchaField()
    class Meta:
        model = MailBox
        fields = ("title", "body", "name", "email", "phone", "address")

        layout = (
            Fieldset("",
                 "title", "body", "name", "email", "phone", "address"),
            )
        
    def __init__(self, *args, **kwargs):
        super(MailBoxForm, self).__init__(*args, **kwargs)
        instance = getattr(self, 'instance', None)
        self.fields['title'].required = False
        self.fields['body'].required = True
        self.fields['name'].required = True
        self.fields['email'].required = True
        self.fields['phone'].required = True
#        self.fields['captcha'].error_messages = {'required': '请填写验证码','invalid': '验证码错误'}
        
    def save(self, *args, **kwargs):
        rs = super(MailBoxForm, self).save(*args, **kwargs)
        return rs

   
class RegistrationForm(BootstrapMixin, ModelForm):

    captcha = CaptchaField(error_messages={
            'required': '请输入验证码',
            'invalid': '验证码错误'
        })
    class Meta:
        model = Registration
        fields = ("group","name","gender","hometown","nation","address","birth_date",\
                  "credential","drug_allergy","nursery_time","examination","disease_history",\
                  "charger","description","signature","status","send_msg","msg_body")

        layout = (
            Fieldset("",
                 "group","name","gender","hometown","nation","address","birth_date",\
                  "credential","drug_allergy","nursery_time","examination","disease_history",\
                  "charger","description","signature","status","send_msg","msg_body"),
            )
    
    def __init__(self, *args, **kwargs):
        super(RegistrationForm, self).__init__(*args, **kwargs)
        instance = getattr(self, 'instance', None)
        try:
            if instance.id:
                del self.fields['captcha']
        except:
            pass
        self.fields['group'].required = False
        self.fields['name'].required = True
        self.fields['gender'].required = True
        self.fields['hometown'].required = True
        self.fields['nation'].required = True
        self.fields['address'].required = True
        self.fields['birth_date'].required = True
        
    def save(self, *args, **kwargs):
        rs = super(RegistrationForm, self).save(*args, **kwargs)
        return rs
    

class PasswordForm(PasswordChangeForm,BootstrapMixin):

    def __init__(self, *args, **kwargs):
        self.base_fields['old_password'].required = True
        self.base_fields['new_password1'].required = True
        self.base_fields['new_password2'].required = True
        super(PasswordForm, self).__init__(*args, **kwargs)

    def save(self, *args, **kwargs):
        rs = super(PasswordForm, self).save(*args, **kwargs)
        return rs