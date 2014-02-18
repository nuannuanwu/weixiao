# -*- coding: utf-8 -*-
import os
import sys

app_root = os.path.dirname(__file__)
# 两者取其一
sys.path.insert(0, os.path.join(app_root, 'system'))
#sys.path.insert(0, os.path.join(app_root, 'system.bundle.zip'))

import django.core.handlers.wsgi
import sae
os.environ['DJANGO_SETTINGS_MODULE'] = 'kinger.settings'
application = sae.create_wsgi_app(django.core.handlers.wsgi.WSGIHandler())
