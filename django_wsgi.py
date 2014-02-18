# -*- coding: utf-8 -*-
# autoreload
import uwsgi
from uwsgidecorators import timer
from django.utils import autoreload
 
@timer(3)
def change_code_gracefull_reload(sig):
    if autoreload.code_changed():
        print "reload it start>>>>>>"
        uwsgi.reload()
        print "reload it edn>>>>>>>>>"

# django uwsgi
import os
import sys

app_root = os.path.dirname(__file__)
# 两者取其一
sys.path.insert(0, os.path.join(app_root, 'system'))
#sys.path.insert(0, os.path.join(app_root, 'system.bundle.zip'))

os.environ['PYTHON_EGG_CACHE'] = '/tmp/.python-eggs'
os.environ['DJANGO_SETTINGS_MODULE'] = 'kinger.settings'
import django.core.handlers.wsgi  
application = django.core.handlers.wsgi.WSGIHandler()  
