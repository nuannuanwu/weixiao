# -*- coding: utf-8 -*-
from django.shortcuts import redirect, render, get_object_or_404
from kinger.models import Group, School, Student, Teacher,Sms
from manage.forms import StudentForm
from django.core.context_processors import csrf
# from django.contrib.auth.decorators import login_required
# from django.contrib.auth.models import User
from django.contrib import messages
from django.utils.translation import ugettext as _
# from django.views.decorators.csrf import csrf_protect
from django.views.decorators.http import require_POST, require_GET
from django.core.exceptions import ObjectDoesNotExist, MultipleObjectsReturned
from kinger.helpers import get_redir_url
from django.db.models import Q
from django.http import HttpResponse
# from userena import signals as userena_signals
import xlwt
import xlrd
from manage.decorators import school_admin_required
from manage import helpers
from kinger.settings import SEND_ACCOUNT_TIMEDELTA
from django.contrib.sites.models import Site
import datetime


SITE_INFO = Site.objects.get_current()

@school_admin_required
def index(request, template_name="manage/student_index.html"):
    ctx = {}
    query = request.GET.get("q", "")
    c = request.GET.get("c", "")

    if c == "wait":
        q = Q(group__isnull=True)
    elif c == "done":
        q = Q(group__isnull=False)
    else:
        q = Q()

    if query == "":
        n = Q()
    else:
        n = Q(name__contains=query)

    manage_school_pks = [s.id for s in request.user.manageSchools.all()]
    students = Student.objects.filter(school__pk__in=manage_school_pks).filter(n, q
            )

    ctx.update({"students": students, "query": query, "c": c})
    return render(request, template_name, ctx)


@school_admin_required
def view(request, student_id, template_name="manage/student_view.html"):
    student = get_object_or_404(Student, pk=student_id)
    ctx = {"student": student}
    return render(request, template_name, ctx)


@school_admin_required
def delete(request, student_id):
    student = get_object_or_404(Student, pk=student_id)
    student.delete()    
    #messages.success(request, _(" %s deleted" % student.name))
    messages.success(request, u"学生 %s 已删除" % student.name)
    return redirect("manage_student_list")


@school_admin_required
def create(request, template_name="manage/student_create.html"):
    if request.method == "POST":
        form = StudentForm(request.POST, request.FILES, user=request.user)
        if form.is_valid():
            student = helpers.create_student(form, request)
            if student.id:
                messages.success(request, u"学生 %s 成功创建" % student.name)
                return redirect("manage_student_view", student_id=student.id)
    else:
        form = StudentForm(user=request.user)

    ctx = {"form": form}
    ctx.update(csrf(request))
    return render(request, template_name, ctx)


@school_admin_required
def update(request, student_id, template_name="manage/student_update.html"):
    """update a class"""
    student = get_object_or_404(Student, pk=student_id)

    if request.method == 'POST':
        form = StudentForm(request.POST, request.FILES, instance=student, user=request.user)
        if form.is_valid():
            # 保存手机信息
            form.save()
            messages.success(request, u"已成功更新学生： %s " % student.name)

            return redirect("manage_student_view", student_id=student_id)
    else:
        # 表单默认手机
        form = StudentForm(instance=student,  user=request.user)

    ctx = {"form": form, "student": student}
    return render(request, template_name, ctx)


@require_GET
@school_admin_required
def template(request):
    """xls template for import"""
    response = HttpResponse(mimetype="application/ms-excel")
    response['Content-Disposition'] = 'attachment; filename=students-template.xls'

    wb = xlwt.Workbook()
    ws = wb.add_sheet(_("Student List"))

    for idx, col in enumerate([_("School"), _("Class"), _("Name"), _("Mobile")]):
        ws.write(0, idx, col)

    wb.save(response)
    return response


@require_POST
@school_admin_required
def imports(request):
    return helpers.importor_view(request, "student", StudentForm)


@school_admin_required
def send_account(request, student_id):
    student = get_object_or_404(Student, pk=student_id)
    #student.delete()
    now = datetime.datetime.now()
    last_time = now + datetime.timedelta(seconds = -SEND_ACCOUNT_TIMEDELTA)
    
    last_reset = Sms.objects.filter(receiver=student.user,
                                 is_active=True,send_time__gt=last_time,send_time__lte=now).order_by('-send_time')
    if last_reset.count():
        time = str(last_reset[0].send_time)
        messages.success(request, _("尊敬的用户，于"+ time +"时候已经重置密码，请耐心等候！【" + SITE_INFO.name + "】"))
    else:   
        rs = student.resetPasswordAndSendSms(sender=request.user)
        if rs:
            #messages.success(request, rs)
            messages.success(request,rs)
        # Send a signal that the password has changed

    # 获得跳转页面。
    redir = get_redir_url(request)
    return redirect(redir)
