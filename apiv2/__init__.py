# -*- coding: utf-8 -*-

"""
| api of kinger project
| 本 api 使用了 ``django-piston`` REST 框架. 具体使用方法请查阅 `相关文档 <http://django-piston-sheepdog.readthedocs.org/en/latest/index.html>`_
| 根据需求，我们对它做了一些 hack. 当然主要是耦合性很高的 hack. 写了一些附加类(``Mixin``), 对其进行了扩展.

.. note:: 我们使用了 `SheepDogInc <https://github.com/SheepDogInc/django-piston>`_ 提供的非官方版本, 

.. note:: 但是也有要修改原来代码的地方，目前只修改了一个地方.
这里列出修改过的具体内容, 非常少:

* ``system/piston/emitters.py: 91``::

    def construct(self, request):
        ...

* ``system/piston/emitters.py:244``::

    # Overriding normal field which has a "resource method"
    # so you can alter the contents of certain fields without
    # using different names.
    ret[maybe_field] = _any(met_fields[maybe_field](data, request))

* ``system/piston/emitters.py:253``::

    if handler_f:
        ret[maybe_field] = _any(handler_f(data, request))

以上修改主要为了在自定义输出字段中加入 ``request`` 变量以满足特殊需求, 如::

    @classmethod
    def liked(cls, model, request):
        try:
            model.likes.get(user=request.user)
            return True
        except ObjectDoesNotExist:
            return False

"""
