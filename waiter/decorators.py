# -*- coding: utf-8 -*-
from functools import wraps
from django.contrib.auth.decorators import user_passes_test
from django.contrib import messages
from django.contrib.auth.views import redirect_to_login

def waiter_required(view_func):
    """
        检查是否具有访问客服后台权限。以message消息来提示
    """
    @wraps(view_func)
    def check_perms(request, *args, **kwargs):
        user = request.user
        path = request.build_absolute_uri()
        if user.has_perm('waiter.can_answer_customer'):       
            return view_func(request, *args, **kwargs)
        elif user.is_authenticated():
            messages.error(request, '你不是客服人员，无权访问客服后台。请用客服人员账号登录。')           
            return redirect_to_login(path)
        else:
            messages.info(request, '访问客服后台，请用客服人员账号登录')  
            return redirect_to_login(path)
    return check_perms
