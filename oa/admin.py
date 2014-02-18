# -*- coding: utf-8 -*-
from django.contrib import admin
from django.db import models

# from django.utils.translation import ugettext as _
from kinger.models import GroupGrade,WebSite
from kinger.forms import (TileCreationForm)
from oauth2app.models import Client, AccessToken, Code

from django.utils.translation import ugettext, ugettext_lazy as _
from django.contrib.admin import widgets, helpers
from django.contrib.admin.util import unquote

from kinger.widgets import AdminImageWidget,AdminFilesWidget
from kinger import settings
from sms.models import SmsNotifyStatus,SmsReceipt,SmsReceive,SmsSend
from django.contrib.comments import Comment
from django.core.urlresolvers import reverse


admin.site.register(GroupGrade)
admin.site.register(WebSite)





