# -*- coding: utf-8 -*-
#from django.http import HttpResponse
from django.shortcuts import render,redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils.translation import ugettext as _

from manage.decorators import school_admin_required
from kinger import helpers

from django.core.urlresolvers import reverse
from kinger.models import Cookbook
from django.db.models import Q

@school_admin_required
def index(request, template_name="index.html"):
    # 初始化数据
    user = request.user
    schools = user.manageSchools.all()

    if schools.count() > 0:
        school = schools[0]
    else:
        messages.error(request,'你没有可管理的学校')
        return redirect('/')
    groups = school.group_set.all()
    group_num = groups.count()

    student_num = school.student_set.all().count()

    teacher_num = school.teacher_set.all().count()

    try:
        cookbook_last = Cookbook.objects.filter(Q(school=school) | Q(group__school=school)).latest('mtime')        
    except Exception, e:
        cookbook_last = None
    

    ctx = {
        'group_num':group_num,
        'student_num':student_num,
        'teacher_num':teacher_num,
        'cookbook_last_modify':cookbook_last.mtime if cookbook_last else cookbook_last
    }
    return render(request, template_name, ctx)
