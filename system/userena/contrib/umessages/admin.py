# -*- coding: utf-8 -*-
from django import forms
from django.utils.translation import gettext_lazy as _
from django.contrib import admin
from django.contrib.auth.models import User, Group

from userena.contrib.umessages.models import Message, MessageContact, MessageRecipient

class MessageRecipientInline(admin.TabularInline):
    """ Inline message recipients """
    model = MessageRecipient

class MessageAdmin(admin.ModelAdmin):
    """ Admin message class with inline recipients """
    inlines = [
        MessageRecipientInline,
    ]

    fieldsets = (
        (None, {
            'fields': (
                'sender', 'body',
            ),
            'classes': ('monospace' ),
        }),
        (_('Date/time'), {
            'fields': (
                'sender_deleted_at',
            ),
            'classes': ('collapse', 'wide'),
        }),
    )
    list_display = ('sender', 'body', 'sent_at','message_type','recipient_count')
    list_filter = ('sent_at', 'sender','type')
    search_fields = ('body',)
    
    def recipient_count(self, obj):
        count = MessageRecipient.objects.filter(message=obj).count() 
        return count
    recipient_count.short_description = '接收人数'
    recipient_count.allow_tags = True
    
    def message_type(self,obj):
        if not obj.type:
            type_name = ''
        else:
            type_name = "紧急" if obj.type == 1 else "普通"
        return type_name
    message_type.short_description = "消息类型"
    message_type.allow_tags = True
            

admin.site.register(Message, MessageAdmin)
admin.site.register(MessageContact)
