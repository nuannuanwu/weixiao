# -*- coding: utf-8 -*-
#from django.http import HttpResponse
from django.conf import settings
from django.utils.translation import ugettext as _
from django.shortcuts import redirect, render, get_object_or_404
from django.core.exceptions import ObjectDoesNotExist
from kinger.helpers import get_redir_url,media_path,unread_count,get_month_theme,add_daily_record_visitor
# from django.shortcuts import render_to_response,render
# from django.template import RequestContext
from django.dispatch import receiver
from django.contrib import messages
from django.contrib.comments import Comment
from django.contrib.comments.views.moderation import perform_delete
from django.contrib.comments.signals import comment_was_posted
from django.contrib import comments
from django.contrib.auth.decorators import login_required, permission_required
from kinger.helpers import get_redir_url,media_path,unread_count,ajax_ok,get_channel,get_month_theme

from kinger.models import Tile, TileTag, TileType, Student,Sms, VerifySms,NewTileCategory,Mentor,\
Cookbook,CookbookType,Access_log,Comment_relation,Activity,TileVisitor,DailyRecordVisitor,\
CookbookRead,Tile,TileRecommend,WebSite,Album,Photo,Part,Link,Teacher,Student,CookbookSet
from django.db.models import Q
from django.contrib.contenttypes.models import ContentType
from kinger import helpers
import calendar
import datetime
import time
from django.http import Http404
from django.http import HttpResponse

from kinger import helpers
from django.contrib.auth.models import User
from django.core.cache import cache
from kinger.settings import STATIC_URL,CTX_CONFIG
from django.core.paginator import Paginator
from django.core.urlresolvers import reverse
from kinger.forms import MobileForm, PwdResetForm, PwdMobileForm
from kinger.profiles.models import Profile
from notifications import notify
from django.contrib.auth import views as auth_views
from django.contrib.sites.models import get_current_site
from django.db import connection
from django.http import Http404
from django.contrib.auth import REDIRECT_FIELD_NAME
from django.contrib.sites.models import Site
try:
    import simplejson as json
except ImportError:
    import json
from oa.helpers import get_parent_domain
from django.contrib.auth import authenticate, login, logout, REDIRECT_FIELD_NAME
from userena.forms import (SignupForm, SignupFormOnlyEmail, AuthenticationForm,
                           ChangeEmailForm, EditProfileForm)
from manage.decorators import profile
import random,urllib2
from django.db.models import Max

import logging
import subprocess
logger = logging.getLogger(__name__)

@login_required
def test(request):
#    rasterize = settings.STATIC_ROOT + '/phantomjs/js/rasterize.js',
#    conf = settings.STATIC_ROOT + '/phantomjs/js/config.json',
#    url = " http://test.weixiao178.com "
#    print rasterize[0],'rasterize----------------'
#    file_path = settings.FILE_PATH + '/phantomjs/test_img.pdf'
#    print file_path,'file_path----------------------------'
#    print "phantomjs --config=" + conf[0] + " " + rasterize[0] + url
#    p = subprocess.call("phantomjs --config=" + conf[0] + " " + rasterize[0] + url + file_path + " A4 2", shell=True)
#    return HttpResponse("rasterize")

    opener1 = urllib2.build_opener()
 
    site = opener1.open('http://weixiao178.com')
    
    data = site.read()
    print data
    file_path = settings.FILE_PATH + '/htmls/file.html'
    file = open(file_path,"wb") #open file in binary mode
    file.writelines(data)
    file.close()
    return HttpResponse(data)
