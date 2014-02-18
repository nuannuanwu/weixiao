# -*- coding: utf-8 -*-

from django.forms import ModelForm, CharField, PasswordInput
from django import forms
from bootstrap.forms import BootstrapForm, Fieldset, BootstrapMixin
from kinger.models import Student, Teacher, Group,EventType,ChangeUsername,Schedule
from kinger.profiles.models import Profile
from django.utils.translation import ugettext as _
from kinger.validators import validate_mobile_number
from django.contrib.auth.models import User
from userena import settings as userena_settings
from kinger import helpers


class StudentForm(BootstrapMixin, ModelForm):
    class Meta:
        model = Student
        fields = ("name", "description", "group", "mobile", "gender", "birth_date")

        layout = (
            Fieldset("",
                "name", "mobile", "description", "group", "gender", "birth_date"),
            )
    avatar = forms.ImageField(required=False)
#    mobile = forms.CharField('mobile', help_text=_('validate mobile number required.'), \
#        validators=[validate_mobile_number])
    mobile = forms.CharField('mobile',required=False)
    group = forms.ModelChoiceField(queryset=Group.objects, required=False)

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user') if kwargs else None
        super(StudentForm, self).__init__(*args, **kwargs)
        instance = getattr(self, 'instance', None)
        if instance and instance.id:
            mobile = instance.getMobile()
            if mobile:
                self.fields['mobile'].widget.attrs['readonly'] = True
            self.fields['mobile'].initial = mobile
            self.fields['avatar'].initial = instance.getAvatar()
            # 设置模板
            self.fields['avatar'].widget.template_with_initial = u'%(input)s'

        if user:
            manage_school_pks = [_school.id for _school in user.manageSchools.all()]
            self.fields['group'].queryset = Group.objects.filter(school__pk__in=manage_school_pks)

    def clean_name(self):
        return self.cleaned_data['name'].strip()

    def clean_birth_date(self):
        birth_date = self.cleaned_data['birth_date']
        return helpers.clean_birthday_rang(birth_date)

    def save(self, *args, **kwargs):
        rs = super(StudentForm, self).save(*args, **kwargs)
        self.after_save()
        return rs

    def after_save(self):
        instance = getattr(self, 'instance', None)
        if instance and instance.id:
            try:
                profile = instance.user.get_profile()
                profile.mobile = self.cleaned_data['mobile']
                profile.mugshot = self.cleaned_data['avatar']
                profile.save()
            except Student.DoesNotExist:
                pass


class TeacherForm(BootstrapMixin, ModelForm):
    class Meta:
        model = Teacher
        fields = ('name', 'appellation', 'description', "mobile")

        layout = (
            Fieldset("",
                'name', 'appellation', 'description', "mobile"),
            )

    avatar = forms.ImageField(required=False)

#    mobile = forms.CharField('mobile', help_text=_('validate mobile number required.'), \
#        validators=[validate_mobile_number])
    mobile = forms.CharField('mobile',required=False)

    def __init__(self, *args, **kwargs):
        super(TeacherForm, self).__init__(*args, **kwargs)
        instance = getattr(self, 'instance', None)
        if instance and instance.id:
            mobile = instance.getMobile()
            if mobile:
                self.fields['mobile'].widget.attrs['readonly'] = True
            self.fields['mobile'].initial = mobile
            self.fields['avatar'].initial = instance.getAvatar()
            # 设置模板
            self.fields['avatar'].widget.template_with_initial = u'%(input)s'

    def clean_name(self):
        return self.cleaned_data['name'].strip()

    def save(self, *args, **kwargs):
        rs = super(TeacherForm, self).save(*args, **kwargs)
        self.after_save()
        return rs

    def after_save(self):
        instance = getattr(self, 'instance', None)
        if instance and instance.id:
            try:
                profile = instance.user.get_profile()
                profile.mobile = self.cleaned_data['mobile']
                profile.mugshot = self.cleaned_data['avatar']
                profile.save()
            except Teacher.DoesNotExist:
                pass


class ClassForm(BootstrapMixin, ModelForm):
    """class save form"""
    class Meta:
        model = Group
        fields = ('name', 'description', 'logo', 'grade', 'year', 'sn')

        layout = (
            Fieldset("",
                'name', 'description', 'logo', 'grade', 'year', 'sn'),
            )

    def __init__(self, *args, **kwargs):
        super(ClassForm, self).__init__(*args, **kwargs)
        instance = getattr(self, 'instance', None)
        if instance and instance.id:
            # 设置模板
            self.fields['logo'].widget.template_with_initial = u'%(input)s'

    def clean_name(self):
        return self.cleaned_data['name'].strip()
    
class ScheduleForm(BootstrapMixin, ModelForm):
    """class save form"""
    class Meta:
        model = Schedule
        fields = ('user', 'group', 'src')

        layout = (
            Fieldset("",
                'user', 'group', 'src'),
            )

    def __init__(self, *args, **kwargs):
        super(ScheduleForm, self).__init__(*args, **kwargs)
        instance = getattr(self, 'instance', None)
        if instance and instance.id:
            # 设置模板
            self.fields['src'].widget.template_with_initial = u'%(input)s'



class ChangeUsernameForm(BootstrapForm):
    username = forms.RegexField(regex=r'^\w+$',
                                max_length=30,
                                widget=forms.TextInput({'class': 'required'}),
                                label=_("Username"),
                                error_messages={'invalid': _('Username must contain only letters, numbers and underscores.')})

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
            raise forms.ValidationError(_('This username is already taken.'))
        if self.cleaned_data['username'].lower() in userena_settings.USERENA_FORBIDDEN_USERNAMES:
            raise forms.ValidationError(_('This username is not allowed.'))
        return self.cleaned_data['username']

    def save(self, user):
        user.username = self.cleaned_data['username']
        change = ChangeUsername(user_id = user.id,name = self.cleaned_data['username'])
        change.save()
        # import datetime
        # user.get_profile().update_username_at = datetime.date.today()
        user.save()

class SchoolEventSettingsForm(forms.Form): 
    id = forms.CharField() 
    def __init__(self, *args, **kwargs): 
        #mdfields = copy.deepcopy(kwargs['mdfields']) 
        #del kwargs['mdfields'] 
        super(SchoolEventSettingsForm, self).__init__(*args, **kwargs) 
        mdfields = EventType.objects.all()
        mdfields = None
        if mdfields is not None: 
            for f in mdfields: 
                self.fields['name'] = forms.TextField()

class UploadImageFile(forms.Form):
    image = forms.ImageField(required=False)

    def save(self, *args, **kwargs):
        rs = super(UploadImageFile, self).save(*args, **kwargs)
        self.after_save()
        return rs