"""
A set of request processors that return dictionaries to be merged into a
template context. Each function takes the request object as its only parameter
and returns a dictionary to add to the context.

These are referenced from the setting TEMPLATE_CONTEXT_PROCESSORS and used by
RequestContext.
"""

from django.conf import settings
from django.middleware.csrf import get_token
from django.utils.functional import lazy
from django.contrib.sites.models import Site

def ctx_config(request):
    context_extras = {}
    context_extras = settings.CTX_CONFIG
    try:
        sid = settings.SITE_ID
        current_site = Site.objects.get(pk=sid)
        context_extras['KINGER_TITLE'] = current_site.name
        context_extras['SITE_DOMAIN '] = current_site.domain
    except:
        pass
    return context_extras
