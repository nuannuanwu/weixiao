# -*- coding: utf-8 -*-
from django.shortcuts import render_to_response, redirect, render, get_object_or_404
from kinger.models import Teacher,School,Group,Student,Sms
from django.core.context_processors import csrf
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib import messages
from django.utils.translation import ugettext as _
from django.core.exceptions import ObjectDoesNotExist
import datetime
from kinger.settings import SEND_ACCOUNT_TIMEDELTA
from django.db.models import Q
from manage.decorators import school_admin_required


def index(request):  
    url = 'baidu.com'
    view_name = "hello"

    #return HttpResponse("Hello, world! - Django")

    return render_to_response('school_index.html',{'name':u'欢迎','url':url,'view_name':view_name})

def view(request):  
    return HttpResponse("这是学校详情页面")

def delete(request):  
    return HttpResponse("删除学校")

def create(request):  
    return HttpResponse("添加学校")

@school_admin_required
def send_account(request, template_name="manage/school_send_account.html"):  
    """群发帐号"""
    role = int(request.GET.get('role', 0))

    ctx = {}
    manage_school_pks = [s.pk for s in request.user.manageSchools.all()]

    q = Q(school__pk__in=manage_school_pks)
    query = request.GET.get('q','')
    if query:
        q = q & Q(name__contains=query)

    # 家长
    if role == 0:
        if request.method == 'POST':
            class_list = request.POST.getlist('class_list')

            student_list = Student.objects.filter(group__in=class_list).order_by("-ctime")
            now = datetime.datetime.now()
            last_time = now + datetime.timedelta(seconds = -SEND_ACCOUNT_TIMEDELTA)

            total_num = student_list.count()
            send_num = 0
            unsend_num = 0
            for student in student_list:
                last_reset = Sms.objects.filter(type_id=100, receiver=student.user,
                                             is_active=True,send_time__gt=last_time,send_time__lte=now).order_by('-send_time')
                if not last_reset.count():
                    rs = student.resetPasswordAndSendSms(sender=request.user)
                    if rs:
                        send_num += 1
                    else:
                        unsend_num += 1

            # 获得cl ，向属于cl的学生发送 帐号信息
            messages.success(request, '学生账号密码成功发送' + str(send_num) + '个,' + str(total_num-send_num-unsend_num) + '个近期已发过。 发送失败' + str(unsend_num) + '个。')
       
        class_list = Group.objects.filter(q)
        ctx['class_list'] = class_list

    # 老师
    else:
        if request.method == 'POST':        
            teacher_list = request.POST.getlist('teacher_list')
            total_num = len(teacher_list)
            send_num = 0
            unsend_num = 0

            tl = Teacher.objects.filter(pk__in=teacher_list)

            for t in tl:                
                now = datetime.datetime.now()

                sms = Sms.objects.filter(type_id=100, is_active=True,receiver=t.user)
                if sms.count() > 0:
                    s = sms.latest('send_time')
                    time = s.send_time
                    seconds = (now - time).seconds

                    if seconds > SEND_ACCOUNT_TIMEDELTA:
                        rs = t.resetPasswordAndSendSms(sender=request.user)
                        if rs:
                            send_num += 1
                        else:
                            unsend_num += 1
                else:
                    rs = t.resetPasswordAndSendSms(sender=request.user)
                    if rs:
                        send_num += 1
                    else:
                        unsend_num += 1

            messages.success(request,'教师账号密码成功发送' + str(send_num) + '个，' + str(total_num - send_num - unsend_num) + '个近期已发过，请耐心等候。 发送失败' + str(unsend_num) + '个。')
        
        teacher_list = Teacher.objects.filter(q)
        ctx['teacher_list'] = teacher_list       

    ctx.update({
        'role':role,
        'query':query
    })

    #ctx = {}
    #school = request.user.manageSchools.all()[0]

    #if request.method == 'POST':
        #cl = []
        #cl = request.POST.getlist('class_list[]')

        #student_list = Student.objects.filter(group__in=cl).order_by("-ctime")[:20]

        #for student in student_list:
            #student.resetPasswordAndSendSms(sender=request.user)
            #print student.id
        # 获得cl ，向属于cl的学生发送 帐号信息
        #messages.success(request, _("resend user account successfully"))
    #else:
        # 获取班级列表
        #print "=="

    #class_list = Group.objects.order_by("-ctime")[:20]
    #ctx['class_list'] = class_list
    #return render(request, template_name, ctx)
    # ctx = {}
    # class_list = {}
    # school = request.user.manageSchools.all()[0]
    # if request.method == 'POST':
    #     cl = []
    #     cl = request.POST.getlist('class_list[]')
    #     role = int(request.POST.get("role", 0))
    #     query = request.POST.get("query", "")
    #     if role == 0:
    #         class_list = Group.objects.order_by("-ctime")
    #         student_list = Student.objects.filter(group__in=cl).order_by("-ctime")
    #         now = datetime.datetime.now()
    #         last_time = now + datetime.timedelta(seconds = -SEND_ACCOUNT_TIMEDELTA)
    #         send_num = 0
    #         for student in student_list:
    #             last_reset = Sms.objects.filter(receiver=student.user,
    #                                          is_active=True,mtime__gt=last_time,mtime__lte=now).order_by('-mtime')
    #             if not last_reset.count():
    #                 student.resetPasswordAndSendSms(sender=request.user)
    #                 send_num += 1
    #             #print student.id
    #         # 获得cl ，向属于cl的学生发送 帐号信息
    #         if send_num:
    #             print send_num,"qqqqq"
    #             messages.success(request, _("resend user account successfully"))
    #     else:
    #         class_list = Teacher.objects.order_by("-ctime")
    # else:
    #     # 获取班级列表
    #     role = int(request.GET.get("role", 0))
    #     if role == 0:
    #         class_list = Group.objects.order_by("-ctime")
    #     else:
    #         class_list = Teacher.objects.order_by("-ctime")
    #     query = request.GET.get("q","")
        
    # #print "query:",query
    # if query:
    #     class_list = class_list.filter(name__contains=query)
    # ctx.update({"class_list": class_list[:20], "query": query, "role":role})
    return render(request, template_name, ctx)

