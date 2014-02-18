# -*- coding: utf-8 -*-
from django.contrib import admin
from django.db import transaction
# from django.utils.translation import ugettext as _
from kinger.models import School,Group,Teacher,Student,EventSetting,Agency
from manage.forms import SchoolEventSettingsForm
from django import forms
from oauth2app.models import Client, AccessToken, Code
from django.contrib.auth.models import User
from django.template.response import TemplateResponse
from django.utils.html import escape
from django.shortcuts import get_object_or_404
from django.utils.decorators import method_decorator
from django.utils.safestring import mark_safe
from django.utils.translation import ugettext, ugettext_lazy as _
from django.views.decorators.csrf import csrf_protect
from django.views.decorators.debug import sensitive_post_parameters
from django.contrib.admin.util import unquote
from kinger.widgets import AdminImageWidget
from django.db import models
from django.forms.formsets import all_valid
from django.contrib.admin import helpers
from django.utils.encoding import force_unicode
from django.core.urlresolvers import reverse

csrf_protect_m = method_decorator(csrf_protect)

from kinger.admin import BackendRoleAdmin


class EventSettingInline(admin.TabularInline):
    """ Inline message recipients """
    model = EventSetting
    classes = ('grp-collapse grp-closed',)


class SchoolAdmin(BackendRoleAdmin):
    inlines = [EventSettingInline,]
    list_display = ('name', 'city', 'area','creator','school_info')
    list_filter = ('city', 'area','creator')
    search_fields = ('name',)
    ordering = ('name',)
    filter_horizontal = ('admins',)
    
    fieldsets = (
        (None, {'fields': ('creator','is_active','admins','name',('city', 'area'),'description')}),
        (_('Other info'), {'classes': ('grp-collapse grp-closed',),'fields': ('sys','type','is_delete',)}),
    )
    
    def school_info(self, obj):
        url = reverse('admin_school_tiles_info') + '?sid=' + str(obj.id)
        return '<a href='+ url +' target="_blank">查看</a>'
    school_info.short_description = '更多信息'
    school_info.allow_tags = True

class GroupAdmin(BackendRoleAdmin):
    list_display = ('name', 'school','creator','grade','type','group_tiles')
    list_filter = ('school','creator')
    search_fields = ('name',)
    ordering = ('name',)
    filter_horizontal = ('teachers',)
    #search_fields = ('first_name', 'last_name')
    #date_hierarchy = 'creator'
    #fields = ('is_active','admins','name',('city', 'area'),'description')
    fieldsets = (
        (None, {'fields': ('is_active','school','name','grade','type','teachers','logo','announcement','description')}),
        (_('Other info'), {'classes': ('grp-collapse grp-closed',),'fields': ('creator','is_delete',)}),
    )

    formfield_overrides = {
        models.ImageField: {'widget': AdminImageWidget},
    }
    
    def group_tiles(self, obj):
        url = reverse('admin_get_tile_image') + '?gid=' + str(obj.id)
        return '<a href='+ url +' target="_blank">查看</a>'
    group_tiles.short_description = '瓦片信息'
    group_tiles.allow_tags = True

class StudentAdmin(BackendRoleAdmin):
    list_display = ('name', 'group', 'school', 'gender','sn','user')
    list_filter = ('school','group','gender','is_active')
    search_fields = ('name','user__username','group__name','school__name')
    ordering = ('name',)
    raw_id_fields = ('user',)
    change_form_template='admin/includes/user_change_form.html' 
    #search_fields = ('first_name', 'last_name')
    #date_hierarchy = 'creator'
    #fields = ('is_active','admins','name',('city', 'area'),'description')
    fieldsets = (
        (None, {'fields': ('is_active','school','group','user','name','sn',('gender', 'birth_date'),'description')}),
        (_('Other info'), {'classes': ('grp-collapse grp-closed',),'fields': ('creator','is_delete',)}),
    )

class TeacherAdmin(BackendRoleAdmin):
    list_display = ('name','user','school','appellation','description')
    search_fields = ('name','user__username','school__name','appellation','description')
    change_form_template='admin/includes/user_change_form.html' 
    ordering = ('name',)
    raw_id_fields = ('user','school')
    
  
class AgencyAdminForm(forms.ModelForm):
    class Meta:
        model = Agency

    def __init__(self, *args, **kwargs):
        super(AgencyAdminForm, self).__init__(*args, **kwargs)
        admin_pks = []
        agencies = Agency.objects.all()
        for a in agencies:
            admin_pks += [u.id for u in a.admins.all()]
        self.fields['admins'].queryset = User.objects.exclude(id__in=admin_pks)
              
class AgencyAdmin(BackendRoleAdmin):
    form = AgencyAdminForm
    filter_horizontal = ['admins']
    
    def save_model(self, request, obj, form, change):
        obj.creator = request.user
        admin_pks = form['admins'].value()
        obj.save()
        obj.customSave(admin_pks)
    list_display = ('name','description')
    list_filter = ('name',)
    search_fields = ('name',)
    exclude = ('school','status','is_active','is_delete')
    
admin.site.register(School, SchoolAdmin)
admin.site.register(Agency,AgencyAdmin)

#FIXME: raise AlreadyRegistered

admin.site.register(Group,GroupAdmin)
admin.site.register(Teacher,TeacherAdmin)
admin.site.register(Student,StudentAdmin)

from guardian.admin import GuardedModelAdmin
