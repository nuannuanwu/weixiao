# -*- coding: utf-8 -*-
from django.shortcuts import redirect, render, get_object_or_404
from kinger.models import Teacher, School, Group
from manage.forms import TeacherForm
from django.core.context_processors import csrf
# from django.contrib.auth.models import User
from django.contrib import messages
from django.db.models import Q
from django.utils.translation import ugettext as _
from django.core.exceptions import ObjectDoesNotExist, MultipleObjectsReturned

from django.http import HttpResponse
from django.views.decorators.http import require_POST, require_GET
import xlwt, xlrd
# from kinger.helpers import get_redir_url
# from django.db.models import Q
# from userena import signals as userena_signals
from manage.decorators import school_admin_required
# from manage.forms import TeacherForm
from manage import helpers


@school_admin_required
def index(request, template_name="manage/teacher_index.html"):

    query = request.GET.get("q", "")
    if query == "":
        n = Q()
    else:
        n = Q(name__contains=query)

    manage_school_pks = [s.id for s in request.user.manageSchools.all()]
    teacher_list = Teacher.objects.filter(school__pk__in=manage_school_pks).filter(n)

    ctx = {}
    ctx.update({"teacher_list": teacher_list, "query": query})

    return render(request, template_name, ctx)


@school_admin_required
def view(request, teacher_id, template_name="manage/teacher_view.html"):
    teacher = get_object_or_404(Teacher, id=teacher_id)
    classes = teacher.groups.all()
    #classes4choose = Group.objects.all()
    manage_school_pks = [s.id for s in request.user.manageSchools.all()]
    classes4choose = Group.objects.filter(
            school__pk__in=manage_school_pks,
            ).exclude(teachers=teacher)

    ctx = {}
    ctx = {"teacher": teacher, 'classes': classes, 'classes4choose': classes4choose}

    return render(request, template_name, ctx)


@school_admin_required
def delete(request, teacher_id):
    """delete a teacher"""
    teacher = get_object_or_404(Teacher, pk=teacher_id)
    teacher.delete()
    messages.success(request, _('Teacher deleted'))
    return redirect("manage_teacher_list")


@school_admin_required
def create(request, template_name="manage/teacher_create.html"):
    if request.method == 'POST':
        form = TeacherForm(request.POST, request.FILES)
        if form.is_valid():
            #新建用户
            teacher = helpers.create_teacher(form, request)
            if teacher.id:
                messages.success(request, u"教师 %s 已成功创建" % teacher.name)
                return redirect("manage_teacher_view", teacher_id=teacher.id)
    else:
        form = TeacherForm()
    ctx = {'form': form}
    ctx.update(csrf(request))
    return render(request, template_name, ctx)


@school_admin_required
def update(request, teacher_id, template_name="manage/teacher_update.html"):
    """update a class"""
    teacher = get_object_or_404(Teacher, pk=teacher_id)
    if request.method == 'POST':
        form = TeacherForm(request.POST, request.FILES, instance=teacher)
        if form.is_valid():
            teacher = form.save()
            messages.success(request, u"教师 %s 已更新" % teacher.name)
            return redirect("manage_teacher_view", teacher_id=teacher.id)
    else:
        # 表单默认手机
        mobile = teacher.getMobile()
        form = TeacherForm(instance=teacher, initial={'mobile': mobile})

    ctx = {"form": form, "teacher": teacher}
    return render(request, template_name, ctx)


@require_GET
@school_admin_required
def template(request):
    """xls template for import"""
    response = HttpResponse(mimetype="application/ms-excel")
    response['Content-Disposition'] = 'attachment; filename=teachers-template.xls'

    wb = xlwt.Workbook()
    ws = wb.add_sheet(_("Teacher List"))

    for idx, col in enumerate([_("School"), _("Class"), _("Name"), _("Mobile")]):
        ws.write(0, idx, col)

    wb.save(response)
    return response


@require_POST
@school_admin_required
# @transaction.commit_manually
def imports(request):
    """import teachers thought xls"""
    return helpers.importor_view(request, "teacher", TeacherForm)
