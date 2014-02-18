# -*- coding: utf-8 -*-
from django.shortcuts import redirect, render, get_object_or_404
from kinger.models import DiskCategory,Disk,Attachment,School,Tile,Group
from django.contrib.auth.models import User
from django.core.context_processors import csrf
from django.contrib import messages
from django.db.models import Q
from django.utils.translation import ugettext as _
from django.http import HttpResponse
from django.views.decorators.http import require_POST, require_GET
import datetime,os
from kinger.settings import FILE_PATH
from django.core.exceptions import ObjectDoesNotExist, MultipleObjectsReturned
from userena import signals as userena_signals
from django.core.urlresolvers import reverse
from django.forms.formsets import formset_factory
from oa.decorators import Has_permission
from django.contrib import auth
from django.contrib.auth.views import logout
from oa.helpers import get_schools,is_agency_user,user_manage_school,disk_category_group
from oa.supply.forms import DiskCategoryForm,DiskForm
from kinger.helpers import ajax_ok
from oss_extra.storage import AliyunStorage
from django.contrib.sites.models import Site
from celery.task.http import URL
try:
    import simplejson as json
except ImportError:
    import json
from oa.decorators import Has_permission

def oa_index(request,template_name="growth/oa_index.html"):
    grows = range(50)
    ctx = {"grows":grows}
    return render(request, template_name, ctx)

def growth_index(request,template_name="growth/growth_index.html"):
    grows = range(50)
    ctx = {"grows":grows}
    return render(request, template_name, ctx)

def source_list(request,group_id,template_name="growth/source_list.html"):
    print group_id,'(?P<group_id>\d+)/'
    group = get_object_or_404(Group,pk=group_id)
    tiles = Tile.objects.filter(group=group,is_tips=0,is_public=0,new_type_id=1)
    try:
        tiles = tiles[0:10]
    except:
        pass
    ctx = {"tiles":tiles}
    data = render(request, template_name,ctx)
    con=data.content
    return ajax_ok('成功',con)
