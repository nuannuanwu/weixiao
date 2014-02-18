# -*- coding: utf-8 -*-
from django.db import models
from manage.managers import SoftDeleteManager
from django.utils.translation import ugettext_lazy as _
from caching.base import CachingMixin, CachingManager

class ActiveMixin(models.Model):
    """
    对 model 附上是否激活状态的字段
    可用于各个 ``model`` 的 Mixin 类. 实现如下效果:

    * 添加 `is_active` 字段.
    * 添加相应方法
    """
    is_active = models.BooleanField(_('is_active'),default=True,help_text="非启用状态将无法使用部分功能")

    def mark_as_active(self):
        """mark object as active"""
        self.is_active = True

    class Meta:
        abstract = True


class SoftDeleteMixin(models.Model):
    """
    实现軟删除的 Mixin. 只要在需要软删除功能的 `model` 中 Mixin 本类即可.

    * 添加 `is_delete` 字段
    * 更改 `Manager`
    """
    is_delete = models.BooleanField(_('is_delete'),default=False)
    objects = SoftDeleteManager()

    def delete(self, *args, **kwargs):
        """
        可以指定是否进行软删除.

        **kwargs**: 与 `models.Model` 的 `delete` 所接受的参数相同

        * *soft:* 自定义的参数. 为 ``True`` 的时候进行软删除，默认.否则删除数据库记录
        """
        if kwargs.pop("soft", True):
            self.is_delete = True
            self.save()
        else:
            super(SoftDeleteMixin, self).delete(*args, **kwargs)

    class Meta:
        abstract = True
