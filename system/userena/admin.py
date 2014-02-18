# -*- coding: utf-8 -*-
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User
from django.utils.translation import ugettext as _
from guardian.admin import GuardedModelAdmin

from userena.models import UserenaSignup
from userena.utils import get_profile_model
from kinger.profiles.models import Profile

class UserenaSignupInline(admin.StackedInline):
    model = UserenaSignup
    max_num = 1

class UserProfileInline(admin.StackedInline):
    model = Profile
    max_num = 1

class UserenaAdmin(UserAdmin, GuardedModelAdmin):
    inlines = [UserenaSignupInline,UserProfileInline,]
    list_display = ('username', 'email', 'first_name', 'last_name',
                    'is_staff', 'date_joined')

class ProfileAdmin(admin.ModelAdmin):
    
    list_display = ('user','gender','mobile','is_mentor','is_waiter','chinese_name')
    list_filter = ('is_mentor','is_waiter','gender','birth_date')
    search_fields = ('user__username','mobile')
    raw_id_fields = ('user',)
    def chinese_name(self, obj):
        return obj.realname
    chinese_name.short_description = '中文名'
    
    
admin.site.unregister(User)
admin.site.register(User, UserenaAdmin)
#admin.site.register(get_profile_model())
admin.site.register(Profile, ProfileAdmin)