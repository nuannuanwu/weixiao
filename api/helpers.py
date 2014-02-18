# -*- coding: utf-8 -*-

"""
api helpers
"""
from django.db.models import Q
from django.http import HttpResponse
from functools import wraps
# cache
from django.core.cache import cache

import logging
import re
from easy_thumbnails.models import Thumbnail
from kinger.models import Student, Group, Mentor, Tile,Waiter,Teacher, MessageToClass,GroupTeacher,School
logger = logging.getLogger(__name__)

from kinger.helpers import media_path_sos,media_attr_sos
def media_path(image, size="normal"):
    name = str(image)
    return media_path_sos(name, size)
    """
    将 ImageField 的内容转换成可访问的图片地址.
    加入了缓存机制

    **args/kwargs**

    * *image:*  ImageField 对象
    * *size:*  图片大小，在 setting.py 设置
    """
    # add cache
    cache_key = "storage_image_" + str(image) + '_' + size
    #print cache_key,"**********"
    try:
        url = cache.get(cache_key)
        if url:
            return url
    except Exception:
        pass

    if not image:
         return ''
    try:
        url = image[size].url
        if url:
            cache.set(cache_key, url)
            return url
    except:
        try:
            return image.url
        except:
            return ''

def media_attr(image, size="normal"):
    name = str(image)
    return media_attr_sos(name,size)
    """
    将 ImageField 的内容转换成可访问的图片地址.
    加入了缓存机制

    **args/kwargs**

    * *image:*  ImageField 对象
    * *size:*  图片大小，在 setting.py 设置
    """
    # add cache
    cache_key = "storage_image_attr_" + str(image) + '_' + size
    #print cache_key,"**********"
    try:
        attr = cache.get(cache_key)
        if attr:
            return attr
    except Exception:
        pass
    
    if not image:
        return ''

    try:
        width = image[size].image.size[0]
        height = image[size].image.size[1]
        if height:
            attr = {'width':width,'height':height}
            cache.set(cache_key, attr)
            return attr
    except:
        try:
            Thumbnail.objects.filter(name=image[size]).delete()
        except:
            pass
        
        try:
            width,height = image['large'].image.size
            if width and height:
                attr = {'width':192,'height':height*192/width}
                cache.set(cache_key, attr)
                return attr
        except:
            return ''

def get_agency_teacher_by_group(group):
    schools = []
    school = group.school
    if school.is_delete:
        return []
    if school.parent_id == 0:
        schools.append(school)
        schools = schools + [s for s in School.objects.filter(parent=school,is_delete=False)]
    else:
        agency = school.parent
        schools.append(agency)
        schools = schools + [s for s in School.objects.filter(parent=agency,is_delete=False)]
    
    teachers = [t for t in Teacher.objects.filter(school__in=schools,is_authorize=True)]
    return teachers

def code_to_video(value):
    """
    [[ ]]格式的视频编码转换为<video>标签
    """
    try:
        match = re.findall(r'\[\[(.*?)\]\]',value)
        if match:
            for i in range(len(match)):
                strinfo = re.compile(r'\[\[('+match[i]+')\]\]')
                html = '<video class="html5video" controls="controls" width="550" height="380" poster="http://weixiao178.com/_static/kinger/img/logo.png"><source src="' + match[i] + '" type="video/mp4" /></video>'
                value = strinfo.sub(html,value)
    except:
        pass
    return value

def query_range_filter(params, queryset, resource_name="resources"):
    """
    列表类型记录的过滤.详细查看 API文档中列表类型数据的请求格式定义， 例如
    `api:tiles <http://192.168.1.222:8080/v1/tiles#A.2Bi.2FdsQlPCZXA->`_

    **args**

    * *params:* 请求数据, 为 `request.GET` 或者 `reqeust.POST`
    * *queryset:* 一般的 django Queryset 对象

    **kwargs**

    * *resource_name:* 输出json列表时，列表的 `key` 值.
    """
    since_id = params.get("since_id", 0)
    max_id = params.get("max_id")
    count = int(params.get("count", 50))
    page = int(params.get("page", 1))

    start = count * (page - 1)
    end = start + count
    range_query = Q(pk__gt=since_id, pk__lte=max_id) if max_id else Q(pk__gt=since_id)

    total = queryset.filter(range_query)[start:].count()
    data = queryset.filter(range_query)[start:end]
    return {"total_number": total, resource_name: data}


class DispatchMixin(object):
    """
    | 由于 Piston 给每个 HTTP 方法 限定了一个函数. 所以这里做了在该方法中做了分派.
    | 具体功能查看各个方法的用法.
    """

    # 声明为一个抽象类
    __abstract__ = True

    def read(self, request, method="get"):
        """
        | GET 的分派函数，Piston 会在接受到所有的 `GET` 请求时调用这个函数.
        在定义 url 访问规则的时候要声明要调用哪些方法, 如下::

             url(r'^tiles/create/$', "tiles_actions", {"method": "post"})

        **kwargs**

        * *method:* 指定要调用的方法
        """
        func = getattr(self, method.lower())
        if not func and not callable(func):
            return rc.NOT_IMPLEMENTED
        return func(request)

    def create(self, request, method="post"):
        """
        | POST request Dispatch
        | Piston 规定这个方法对应 `POST` 请求
        | 其它与 `read` 方法一样.
        """
        func = getattr(self, method.lower())
        if not func and not callable(func):
            return rc.NOT_IMPLEMENTED
        return func(request)

    @classmethod
    def _check_method(cls, func, method):
        """
        check request method if is allowed. *私有方法*.

        **args**

        * *func:*  被装饰的方法
        * *method:*  HTTP verb: "post"/"get"
        """
        @wraps(func)
        def _check(self, request, *args, **kwargs):
            if request.method != method.upper():
                    msg = "require %s method to access api: %s !" % \
                    (method.upper(), request.path)
                    return rc.not_allowed(msg)
            return func(self, request, *args, **kwargs)

        return _check

    @classmethod
    def post_required(cls, func):
        """
        | api request POST to access
        | 限定被装饰的方法只能执行 `post` 请求.
        `这是一个装饰方法`, 如下调用::

            @Dispatch.post_required
            def post(request):
                ...

        | 这个方法调用 ``_check_method`` 方法，也是一个装饰器. 该方法检查是否允许执行某种(请看参数说明) HTTP verb 请求.
        如果该 verb 不被允许。将按照统一的错误信息以 json 方式返回. 类似于::

            {
                error_description: "require POST method to access api: /api/v1/messages/create/ !",
                error: "Method not allowed"
            }

        状态码为: ``405 METHOD NOT ALLOWED``
        """
        return cls._check_method(func, "post")

    @classmethod
    def get_required(cls, func):
        """
        | api request POST to access
        | 与 ``post_required`` 相同.
        """
        return cls._check_method(func, "get")


class rc_factory(object):
    """
    | rewrite piston.utils.rc
    | 重写 ``piston.utils.rc`` 类. 主要实现在返回各个状态码时，可以
      附加自定义内容，并以 json 格式返回.
    只要在 `Handler` 然会对应的状态方法即可, 基本用法::

        return rc.ACCEPTED

    | 在页面上看到的输出内容为 "Accept". 并且状态码为 202
    如果需要自己定义输出, 只要将大写改为小写::

        return rc.accepted({"status": True})

    这个将会返回 json 格式的内容.

    .. warning:: rc.DELETED 不能定义返回内容。它强制规定返回内容为空.
    """

    CODES = dict(ALL_OK = ('OK', 200),
                 CREATED = ('Created', 201),
                 ACCEPTED = ('Accepted', 202),
                 DELETED = ('', 204),  # 204 says "Don't send a body!"
                 BAD_REQUEST = ('Bad Request', 400),
                 UNAUTHORIZED = ('Unauthorized', 401),
                 FORBIDDEN = ('Forbidden', 403),
                 NOT_FOUND = ('Not Found', 404),
                 DUPLICATE_ENTRY = ('Conflict/Duplicate', 409),
                 NOT_HERE = ('Gone', 410),
                 BAD_RANGE = ('Unsatifiable Range', 416),
                 INTERNAL_ERROR = ('Internal Error', 500),
                 NOT_IMPLEMENTED = ('Not Implemented', 501),
                 THROTTLED = ('Throttled', 503),
                 NOT_ALLOWED = ('Method not allowed', 405)
                 )

    def __getattr__(self, attr):
        """
        Returns a fresh `HttpResponse` when getting
        an "attribute". This is backwards compatible
        with 0.2, which is important.
        """
        try:
            (info, code) = self.CODES.get(attr.upper())
        except TypeError:
            raise AttributeError(attr)

        class HttpResponseWrapper(HttpResponse):
            """
            Wrap HttpResponse and make sure that the internal _is_string
            flag is updated when the _set_content method (via the content
            property) is called
            """
            def _set_content(self, content):
                """
                Set the _container and _is_string properties based on the
                type of the value parameter. This logic is in the construtor
                for HttpResponse, but doesn't get repeated when setting
                HttpResponse.content although this bug report (feature request)
                suggests that it should: http://code.djangoproject.com/ticket/9403
                """
                if not isinstance(content, basestring) and hasattr(content, '__iter__'):
                    self._container = content
                    self._is_string = False
                else:
                    self._container = [content]
                    self._is_string = True

            content = property(HttpResponse._get_content, _set_content)

        def info_builder(summary="", desc=""):
            """
            当状态代码大于 400, 即发生错误，将按统一的格式返回错误信息.

            **kwargs**

            * *summary:*  HTTP 状态代码默认的内容
            * *desc:*  自定义内容.可以是文本或者 dict 对象
            """
            if code >= 400:
                return {"error": summary, "error_description": desc}
            return summary if not desc else desc

        def resp(content=""):
            content = info_builder(info, content)
            return HttpResponseWrapper(content, content_type='application/json', status=code)

        # 当调用状态方法名为小写的时候返回 `resp` 函数。
        # 可自定义附加的输出内容
        if not attr.isupper():
            return resp

        return HttpResponseWrapper(info_builder(info), content_type='application/json', status=code)


# 工厂方法，给全局调用
rc = rc_factory()
