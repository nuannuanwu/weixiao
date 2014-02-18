# -*- coding: utf-8 -*-

from django.forms import ModelForm, CharField, PasswordInput
from django import forms
from bootstrap.forms import BootstrapForm, Fieldset, BootstrapMixin
from kinger.models import SupplyCategory,Provider,Supply,DiskCategory,Disk,Material,MaterialApply,Supply,Disk
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


class SupplyCategoryForm(BootstrapMixin, ModelForm):
    class Meta:
        model = SupplyCategory
        fields = ("name","parent")

        layout = (
            Fieldset("",
                 "name","parent"),
            )
    
    def __init__(self, *args, **kwargs):
        super(SupplyCategoryForm, self).__init__(*args, **kwargs)
        instance = getattr(self, 'instance', None)
        self.fields['name'].required = True
    
    def save(self, *args, **kwargs):
        rs = super(SupplyCategoryForm, self).save(*args, **kwargs)
        return rs
    

class DiskCategoryForm(BootstrapMixin, ModelForm):
    class Meta:
        model = DiskCategory
        fields = ("name","parent","order")

        layout = (
            Fieldset("",
                 "name","parent","order"),
            )
    
    def __init__(self, *args, **kwargs):
        super(DiskCategoryForm, self).__init__(*args, **kwargs)
        instance = getattr(self, 'instance', None)
        self.fields['name'].required = True
        self.fields['order'].required = False
    
    def save(self, *args, **kwargs):
        rs = super(DiskCategoryForm, self).save(*args, **kwargs)
        return rs
    

class ProviderForm(BootstrapMixin, ModelForm):
    class Meta:
        model = Provider
        fields = ("name","charger","description","school","mobile","address","remark")

        layout = (
            Fieldset("",
                "name","charger","description","school","mobile","address","remark"),
            )
    
    def __init__(self, *args, **kwargs):
        super(ProviderForm, self).__init__(*args, **kwargs)
        instance = getattr(self, 'instance', None)
        self.fields['name'].required = True

    def save(self, *args, **kwargs):
        rs = super(ProviderForm, self).save(*args, **kwargs)
        return rs


class MaterialForm(BootstrapMixin, ModelForm):
    
    insc = None
    class Meta:
        model = Material
        fields = ("title", "type","level","send_msg","msg_body","is_submit","remark","status","inscribed","send_time","description")

        layout = (
            Fieldset("",
                 "title", "type","level","send_msg","msg_body","is_submit","remark","status","inscribed","send_time","description"),
            )
    
    class Media:
        js = (
              settings.STATIC_URL + 'media/js/tinymce/jscripts/tiny_mce/tiny_mce.js',
              settings.STATIC_URL + 'media/js/textareas.js',
         )
    
    def __init__(self, *args, **kwargs):
        super(MaterialForm, self).__init__(*args, **kwargs)
        instance = getattr(self, 'instance', None)
        self.insc = instance
        self.fields['title'].required = True
        self.fields['level'].required = True
        self.fields['type'].required = True
        self.fields['inscribed'].required = True
        self.fields['send_time'].required = True
        
    def clean(self):
        cleaned_data = self.cleaned_data
        send_msg = cleaned_data.get("send_msg")
        if send_msg and not cleaned_data.get("msg_body"):
            self._errors["msg_body"] = self.error_class(["这个字段是必填项。"])
        return cleaned_data
    

class SupplyForm(BootstrapMixin, ModelForm):
    class Meta:
        model = Supply
        fields = ("name","school","category","num","min","remark","is_show")

        layout = (
            Fieldset("",
                "name","school","category","num","min","remark","is_show"),
            )
    
    def __init__(self, *args, **kwargs):
        super(SupplyForm, self).__init__(*args, **kwargs)
        instance = getattr(self, 'instance', None)
        self.fields['name'].required = True

    def save(self, *args, **kwargs):
        rs = super(SupplyForm, self).save(*args, **kwargs)
        return rs
    

class DiskForm(BootstrapMixin, ModelForm):
    class Meta:
        model = Disk
        fields = ("title","school","category","content")

        layout = (
            Fieldset("",
                "title","school","category","content"),
            )
        
    class Media:
        js = (
              settings.STATIC_URL + 'media/js/tinymce/jscripts/tiny_mce/tiny_mce.js',
              settings.STATIC_URL + 'media/js/textareas.js',
         )
        
    def __init__(self, *args, **kwargs):
        super(DiskForm, self).__init__(*args, **kwargs)
        instance = getattr(self, 'instance', None)
        self.fields['title'].required = True
        self.fields['content'].required = True
        try:
            user = kwargs.pop('user')
        except:
            user = None

    def save(self, *args, **kwargs):
        rs = super(DiskForm, self).save(*args, **kwargs)
        return rs
    