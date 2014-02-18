# -*- coding: utf-8 -*-
from django.template import Library
from django.template.base import TemplateSyntaxError
from django.template import Node
from notifications.models import Notification
from django.http import HttpResponse
from django.contrib.sessions.models import Session
from django.contrib.comments import Comment
from kinger.models import Tile

register = Library()

@register.filter
def notify_info(value,ty="title"):
    """提醒类型描述"""
    result = ''
    
    if ty == "logo":
        if isinstance(value,Tile):
            result = "tile"
        if isinstance(value,Comment):
            result = "comment"
        return result
    
    if ty == "title":
        if isinstance(value,Tile):
            result = "您发布的内容"
        if isinstance(value,Comment):
            result = "您评论的内容"
        return result
    if ty == "content":
        if isinstance(value,Tile):
            result = value.description if value.description else value
        if isinstance(value,Comment):
            result = value.comment if value.comment else value
        return result
    
    
@register.assignment_tag(takes_context=True)
def notifications_unread(context, ty=''):
    if 'user' not in context:
        return ''
    
    user = context['user']
    if user.is_anonymous():
        return ''
    
    new_num = Notification.objects.count_notify_group(user)
    if ty == "normal":
        return new_num
    num = 0 
    try:
        num = context['request'].session["notifications_count_" + str(user.id)]
    except Exception:
        pass
    
    if num:
        if int(num) == int(new_num):
            return ''
        else:
            return new_num
    else:
        return new_num


 


    