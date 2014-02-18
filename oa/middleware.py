from django.http import HttpResponsePermanentRedirect
from django.core.cache import cache
#from django.conf import settings
#from django.core import urlresolvers
import socket

class SubdomainMiddleware(object):
    def process_request(self, request):
        domain_parts = request.get_host().split('.')
        if len(domain_parts) == 3 and (domain_parts[1] == 'jytn365' or domain_parts[1] == 'local'):
            request.path_info = '/%s%s' % (domain_parts[0], request.path)
        return None