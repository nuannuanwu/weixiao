# -*- coding: utf-8 -*-
from django.http import HttpResponse, HttpResponseNotFound
from django.shortcuts import render_to_response, redirect, render, get_object_or_404
from api.helpers import rc
from kinger import helpers
from django.conf import settings

from django.core.urlresolvers import resolve, reverse
import sys, socket   
import oss.oss_api
import oss.oss_util
try:
    import sae.storage
except:
    pass
def test(request):
    try:
        sae_storage = sae.storage.Client(accesskey='jyoz12zlo0', secretkey='53l04k34jz54m0xw4mjy2l4yiillzmwwxjkzli3l', prefix='jytn365')
        obj_list = [s['name'] for s in sae_storage.list("base")]
        return HttpResponse(obj_list)
    except:
        return HttpResponse('')
    
def sae_test(request):
    oss_storage = oss.oss_api.OssAPI(settings.OSS_HOST,settings.OSS_ACCESS_KEY_ID,settings.OSS_SECRET_ACCESS_KEY)
    oss_storage.put_object_from_string("zhuyuan-test",'test_file',"aaaaaaaaaaaaaa")
    return HttpResponse('')
  

