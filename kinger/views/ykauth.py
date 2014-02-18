# -*- coding: utf-8 -*-
from django.shortcuts import redirect, render, get_object_or_404
from django.http import HttpResponse


def index(request, template_name="oa/teacher_list.html"):
    
    try:
        content = open("YKAuth.txt", "r")
        text = content.read()
        content.close()
    except:
        text = ''
 
    return HttpResponse(text)


