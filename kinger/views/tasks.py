# -*- coding: utf-8 -*-
#from django.http import HttpResponse
from django.conf import settings
from django.utils.translation import ugettext as _
from django.shortcuts import redirect, render, get_object_or_404
from django.core.exceptions import ObjectDoesNotExist
from kinger.helpers import get_redir_url,media_path,unread_count
# from django.shortcuts import render_to_response,render
# from django.template import RequestContext
from django.dispatch import receiver
from django.contrib import messages
from django.contrib.comments import Comment
from django.contrib.comments.views.moderation import perform_delete
from django.contrib.comments.signals import comment_was_posted
from django.contrib import comments
from django.contrib.auth.decorators import login_required, permission_required
# from django.views.decorators.http import require_POST, require_GET

from kinger.models import Tile, TileTag, TileType, Student,Sms, VerifySms,TileCategory,Mentor,\
Cookbook,CookbookType,Access_log,Comment_relation,Activity,TileVisitor,DailyRecordVisitor,\
CookbookRead
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

import random
from django.db.models import Max

