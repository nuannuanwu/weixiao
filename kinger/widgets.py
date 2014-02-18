# -*- coding: utf-8 -*-
#自定义扩展一些widgets

from django.contrib.admin.widgets import AdminFileWidget
from django.utils.safestring import mark_safe

class AdminImageWidget(AdminFileWidget):
    """
    A ImageField Widget for admin that shows a thumbnail.
    """

    def __init__(self, attrs={}):
        super(AdminImageWidget, self).__init__(attrs)

    def render(self, name, value, attrs=None):       
        output = []
        if value and hasattr(value, "url"):
            output.append(('<a target="_blank" href="%s">'
                           '<img src="%s" style="max-height: 100px; max-width:100px;" /></a> '
                           % (value.url, value.url)))
        output.append(super(AdminImageWidget, self).render(name, value, attrs))       
        return mark_safe(u''.join(output))
    
class AdminFilesWidget(AdminFileWidget):
    """
    A FileField Widget for admin.
    """
    
    def __init__(self, attrs={}):
        
        super(AdminFilesWidget, self).__init__(attrs)

    def render(self, name, value, attrs=None):   
        output = []
        if value:
            if hasattr(value, "url"):
                output.append(('<a href="%s">%s</a>'
                           % (value.url, value)))
            else:
                output.append(('%s'
                               % (value)))
        output.append(super(AdminFilesWidget, self).render(name, value, attrs))       
        return mark_safe(u''.join(output))