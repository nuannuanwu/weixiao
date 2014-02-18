#-*- coding: utf-8 -*-
from django.conf.urls.defaults import patterns, url

urlpatterns = patterns('kinger.apps.oauth2.views',
        (r'^missing_redirect_uri/?$',   'missing_redirect_uri'),
        (r'^authorize/?$',              'authorize'),
        (r'^access_token/?$',           'access_token'),
)
