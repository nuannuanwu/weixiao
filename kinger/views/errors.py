# -*- coding: utf-8 -*-
from django.http import HttpResponse, HttpResponseNotFound
from django.shortcuts import render_to_response, redirect, render, get_object_or_404
from api.helpers import rc

from django.core.urlresolvers import resolve, reverse

def handler404(request):
    print 'handler404  ========='
    return render(request,'404.html',status=404)

def handler500(request):
    print 'handler500  ========='

    resolver_match = resolve(request.path)
    app_name = resolver_match.app_name   

    if app_name == 'api':
        return HttpResponse('500', status=500)
    return render(request,'500.html', status=500)