import time
from django.http import HttpResponse
from django.core.cache import cache
from django import get_version as django_version
from django.core.mail import send_mail, mail_admins
from django.core.urlresolvers import resolve
from django.http import Http404
from django.conf import settings
from django.utils.translation import ugettext as _
from django.template import loader, TemplateDoesNotExist
from django.contrib.sites.models import Site
from piston.decorator import decorator


class rc_factory(object):
    """
    Status codes.
    """
    CODES = dict(ALL_OK = ('OK', 200),
                 CREATED = ('Created', 201),
                 ACCEPTED = ('Accepted', 202),
                 DELETED = ('', 204), # 204 says "Don't send a body!"
                 BAD_REQUEST = ('Bad Request', 400),
                 UNAUTHORIZED = ('Unauthorized', 401),
                 FORBIDDEN = ('Forbidden', 403),
                 NOT_FOUND = ('Not Found', 404),
                 DUPLICATE_ENTRY = ('Conflict/Duplicate', 409),
                 NOT_HERE = ('Gone', 410),
                 BAD_RANGE = ('Unsatifiable Range', 416),
                 INTERNAL_ERROR = ('Internal Error', 500),
                 NOT_IMPLEMENTED = ('Not Implemented', 501),
                 THROTTLED = ('Throttled', 503))

    def __getattr__(self, attr):
        """
        Returns a fresh `HttpResponse` when getting
        an "attribute". This is backwards compatible
        with 0.2, which is important.
        """
        try:
            (r, c) = self.CODES.get(attr)
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
            
            
        message = ({"error":c,"error_description":r})
        return HttpResponseWrapper(message, content_type='text/plain', status=c)

rc = rc_factory()
