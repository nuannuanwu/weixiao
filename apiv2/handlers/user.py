# -*- coding: utf-8 -*-
"""
**account/** 系列接口模块
"""

from piston.handler import BaseHandler
from django.contrib.auth.models import User
from api.helpers import rc, DispatchMixin
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth.forms import PasswordChangeForm
from userena import signals as userena_signals
from userena.forms import EditProfileForm
import api.handlers.group
from kinger.models import Device,Access_log
from api.helpers import media_path

import logging
# Get an instance of a logger
logger = logging.getLogger(__name__)


class UserHandler(BaseHandler):
    '''
    | 用户帐号资源. 在这里定义的所有输出字段可用于其它关联的资源.
    | 比如一个包含用户数据的 *comments* 资源，用户数据部分会按本资源定义的字段显示
    '''
    model = User
    fields = ("uid", "name", "username", "last_login", "gender", "avatar", "avatar_large", "mobile", "about_me")

    allowed_methods = ("GET", )

    @classmethod
    def uid(cls, model, request):
        return model.id

    @classmethod
    def name(cls, model, request):
        try:
            return model.get_profile().chinese_name_or_username()
        except Exception:
            return model.username

    @classmethod
    def gender(cls, model, request):
        try:
            return model.get_profile().gender
        except Exception:
            return ""

    @classmethod
    def avatar(cls, model, request):
        try:
            url = model.get_profile().mugshot
            url = media_path(url, "avatar")
            return url
        except Exception:
            return ""

    @classmethod
    def avatar_large(cls, model, request):
        try:
            url = model.get_profile().mugshot
            url = media_path(url, "avatar_large")
            return url
        except Exception:
            return ""

    @classmethod
    def mobile(cls, model, request):
        try:
            return model.get_profile().mobile
        except:
            return ""

    @classmethod
    def about_me(cls, model, request):
        try:
            return model.get_profile().about_me
        except Exception:
            return ""

    def read(self, request):
        '''
        列出用户详细信息

        ``GET`` `users/show/ <http://192.168.1.222:8080/v1/users/show>`_

        :param uid:
            用户帐号 id.
        '''
        user_id = request.GET.get("uid")
        try:
            user = User.objects.get(pk=user_id) if user_id else request.user
        except User.DoesNotExist:
            return rc.NOT_HERE
        return user


class AccountHandler(DispatchMixin, UserHandler):
    allowed_methods = ("GET", "POST")
    csrf_exempt = True
    
    @DispatchMixin.get_required
    def access_log(self, request):
        '''
        增加 用户用户登录日志

        ``GET`` `account/access_log/ <http://192.168.1.222:8080/v1/account/access_log/>`_
        '''
        if request.user.is_authenticated():
            #用户登录日志
            log = Access_log()
            log.type = 3
            log.user = request.user
            log.url = request.get_full_path()
            log.save()
            return {"uid": request.user.id}

    @DispatchMixin.get_required
    def get_uid(self, request):
        '''
        获取登录用户的帐号 id.

        ``GET`` `account/get_uid/ <http://192.168.1.222:8080/v1/account/get_uid>`_
        '''
        return {"uid": request.user.id}

    @DispatchMixin.get_required
    def identity(self, request):
        '''
        获取登录用户的身份: 家长/教师

        ``GET``  `account/profile/identity/ <http://192.168.1.222:8080/v1/account/profile/identity>`_

        '''
        try:
            request.user.teacher
            return {"identity": "teacher"}
        except ObjectDoesNotExist:
            pass

        try:
            request.user.student
            return {"identity": "student"}
        except ObjectDoesNotExist:
            pass

        return rc.NOT_FOUND

    @DispatchMixin.post_required
    def change_password(self, request):
        '''
        更改用户密码接口.

        ``POST`` `account/change_passwrod/ <http://192.168.1.222:8080/v1/account/change_password>`_

        :param old_password:
            旧密码

        :param new_password:
            新密码
        '''
        user = request.user
        old_password = request.POST.get("old_password")
        new_password = request.POST.get("new_password")

        data = {
            "old_password": old_password,
            "new_password1": new_password,
            "new_password2": new_password,
        }

        form = PasswordChangeForm(user=user, data=data)
        if form.is_valid():
            form.save()
            # Send a signal that the password has changed
            userena_signals.password_complete.send(sender=None,
                                                   user=user)
            return rc.accepted({"result": True})
        # return form.error_messages
        return rc.BAD_REQUEST

    @DispatchMixin.post_required
    def change_avatar(self, request):
        '''
        更改用户头像

        ``POST`` `account/change_avatar/ <http://192.168.1.222:8080/v1/account/change_avatar>`_

        :param avatar:
            二进制图片数据.
        '''
        user = request.user
        profile = user.get_profile()

        user_initial = {'first_name': user.first_name,
                        'last_name': user.last_name}

        params = request.POST.copy()
        params.update({"privacy": profile.privacy})

        files = {'mugshot': request.FILES['avatar']}
        form = EditProfileForm(params, files, instance=profile,
                                 initial=user_initial)

        if form.is_valid():
            profile = form.save()
            return user

        return rc.BAD_REQUEST


class DeviceHandler(BaseHandler):
    model = Device

    def read(self, request):
        try:
            return request.user.device.get()
        except ObjectDoesNotExist:
            return rc.NOT_HERE

    def create(self, request):
        '''
        记录设备的唯一标识

        ``POST`` `account/set_device_token/ <http://192.168.1.222:8080/v1/account/set_device_token>`_

        :param token:
            设备令牌.
        '''
        token = request.POST.get("device_token")
        unset = request.POST.get("unset","")
        
        if unset:
            try:
                device = Device.objects.get(token=token,user=request.user)
                device.delete()
            except ObjectDoesNotExist:
                return rc.NOT_HERE
        else:
            device,create = Device.objects.get_or_create(user=request.user,defaults={"token":token})
            if not create:
                device.token = token
                device.save()

        return rc.accepted({"result": True})
