# -*- coding: utf-8 -*-
from functools import wraps
from django.contrib.auth.decorators import user_passes_test
from django.contrib import messages
from django.contrib.auth.views import redirect_to_login

def aq_required(view_func):
    """
        检查是否具有访问专家问答权限。以message消息来提示
    """
    @wraps(view_func)
    def check_perms(request, *args, **kwargs):
        user = request.user
        path = request.build_absolute_uri()
        if user.has_perm('aq.can_answer_parent'):       
            return view_func(request, *args, **kwargs)
        elif user.is_authenticated():
            messages.error(request, '你不是运营人员，无权访问专家问答。请用运营人员帐号登录。')           
            return redirect_to_login(path)
        else:
            messages.info(request, '访问专家问答，请用运营人员帐号登录')  
            return redirect_to_login(path)
    return check_perms
