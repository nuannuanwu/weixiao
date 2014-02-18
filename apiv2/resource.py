# -*- coding: utf-8 -*-

import sys
from piston.resource import Resource
from piston.utils import FormValidationError, HttpStatusCode
from django.http import Http404
from django.views.debug import ExceptionReporter
from piston.utils import format_error
from django.conf import settings
from api.helpers import rc


class KingerResource(Resource):
    """
    | 重写 ``piston.resource.Resource`` 类。
    | 当程序出错，返回 500 的时候。以固定的错误格式 json 方式返回给接口调用方.
    """
    def error_handler(self, e, request, meth, em_format):
        """
        params: e, request, meth, em_format
        """
        if settings.DEBUG:
            raise
        for error in [FormValidationError, TypeError, Http404, HttpStatusCode]:
            if isinstance(e, error):
                return super(KingerResource, self).error_handler(e, request, meth, em_format)

        # copy from suer class, checkout super
        exc_type, exc_value, tb = sys.exc_info()
        rep = ExceptionReporter(request, exc_type, exc_value, tb.tb_next)
        if self.email_errors:
            self.email_exception(rep)
        if self.display_errors:
            # e = format_error('\n'.join(rep.format_exception()))
            # 使用我们自己重写的 ``rc`` 类.
            return rc.internal_error(e)
        else:
            raise
