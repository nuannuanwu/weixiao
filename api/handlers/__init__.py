# -*- coding: utf-8 -*-

"""
| api 所有的 resource handler。

Dispatch
--------
| 当混入了 ``DispatchMixin`` 时，使用 ``get`` 方法代替 ``read``。
| 因为 ``read`` 方法已经被 ``DispatchMixin`` 用作分派路由方法。
| 当然也可以 override 该方法。但当一个 *handler* 里有处理 多个 ``HTTP Verb``的时候
| 则不能强制将方法与对应的 http verb 匹配。因为所有的 ``GET`` 都走 ``read``方法.
| *具体查看 ``DispatchMixin`` 类*

不使用 ``DispatchMixin`` 的时候则按照 ``piston`` 原本的操作进行(``GET``只走``read``方法)

数据集(列表)接口
----------------
有关所有获取数据集(列表)的接口有共用的请求参数, 例如 `comments/show <http://192.168.1.222:8080/v1/comments/show>`_ 接口中的请求参数.

具体实现请查看 :ref:`api.helpers.query_range_filter` 方法

模块方法
--------

"""

from piston.handler import BaseHandler
from api.helpers import rc


class ApiNotFoundHandler(BaseHandler):
    """
    当前缀为 ```api/v1/``` 但又是无效地址的 404 处理句柄.
    将以 404 返回给接口调用方(统一的错误格式)
    """
    allowed_methods = ("GET",)

    def read(self, request):
        return rc.not_found("api not founded")
