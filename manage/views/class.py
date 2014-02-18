# -*- coding: utf-8 -*-
from django.shortcuts import redirect, render, get_object_or_404
from kinger.models import Group, School, Student, Teacher
from manage.forms import ClassForm
from django.core.context_processors import csrf
from django.contrib.auth.models import User
from django.db.models import Q
from django.contrib import messages
from django.utils.translation import ugettext as _
from django.views.decorators.csrf import csrf_protect
from django.views.decorators.http import require_POST
from kinger.helpers import get_redir_url
from manage.decorators import school_admin_required
import datetime

@school_admin_required
def index(request, template_name="manage/class_index.html"):
    ctx = {}
    #Q(question__startswith='Who') | Q(question__startswith='What')
    query = request.GET.get("q", "")
    c = request.GET.get("c", "")
    if query == "":
        n = Q()
    else:
        n = Q(name__contains=query)
    if c:
        n = n | Q(year=c)
    # TODO: should list all classes in additional to different school.
    manage_school_pks = [s.id for s in request.user.manageSchools.all()]    
    classes = Group.objects.filter(school__pk__in=manage_school_pks).filter(n)
    
    year = datetime.datetime.now().year
    years = [str(x) for x in range(year - 10,year + 10)]
    ctx.update({"classes": classes, "query": query, "c": c, "years":years})
    
    return render(request, template_name, ctx)


@school_admin_required
@csrf_protect
def create(request,template_name="manage/class_create.html"):

    if request.method == 'POST':
        form = ClassForm(request.POST,request.FILES)
        if form.is_valid():
            group = form.save(commit=False)
            group.creator = request.user
            group.school = request.user.manageSchools.latest("id")
            group.save()
            if group.id:
                messages.success(request, u'已成功创建班级 %s ' % group.name)
                return redirect("manage_class_list")
    else:
        form = ClassForm()

    ctx = {'form':form}
    return render(request, template_name, ctx)


@school_admin_required
def view(request, class_id, template_name="manage/class_view.html"):
    """docstring for view"""
    group = get_object_or_404(Group, pk=class_id)
    students = group.students.all()
    teachers = group.teachers.all()
    role = int(request.GET.get("role", 0))
    manage_school_pks = [s.id for s in request.user.manageSchools.all()]
    if role == 0:
        unmatchs = Student.objects.filter(school__pk__in=manage_school_pks).filter(group__isnull=True)
    else:
        unmatchs = Teacher.objects.filter(school__pk__in=manage_school_pks).exclude(groups=group)
    ctx = {"class": group,
            "users": unmatchs,
            "students": students,
            "teachers": teachers,
            "role": role,
            }
    return render(request, template_name, ctx)

@school_admin_required
def delete(request,class_id):
    """delete a class"""
    group = get_object_or_404(Group, pk=class_id)
    group.delete()
    #messages.success(request, _(' %s was deleted successfully' % group.name ))
    messages.success(request, u'班级 %s 已删除' % group.name)
    return redirect("manage_class_list")


@school_admin_required
@csrf_protect
def update(request, class_id, template_name="manage/class_update.html"):
    """update a class"""
    group = get_object_or_404(Group, pk=class_id)
    if request.method == 'POST':
        form = ClassForm(request.POST, request.FILES, instance=group)
        if form.is_valid():
            form.save()
            messages.success(request, u'班级 %s 已更新' % group.name)
            return redirect("manage_class_list")
    else:
        form = ClassForm(instance=group)

    ctx = {"form": form, "class": group}
    return render(request, template_name, ctx)


@school_admin_required
@require_POST
def add_student(request):
    """docstring for add_user"""
    pk = request.POST.get("student_id")
    if not pk:
        messages.error(request, _("Student does not exist"))
        return redirect(get_redir_url(request))
    student = get_object_or_404(Student, pk=pk)

    try:
        class_id = request.POST.get("class_id")
        if not class_id:
            raise Group.DoesNotExist
        group = Group.objects.get(pk=class_id)
    except Group.DoesNotExist:
        messages.error(request, _("Group does not exist"))
        return redirect(get_redir_url(request))

    student.group = group
    student.save()

    msg = u" %s 加入了 %s" % (student.name, group.name)
    messages.success(request, msg)
    return redirect(get_redir_url(request))


@school_admin_required
@require_POST
def add_teacher(request):
    """docstring for add_teacher"""
    teacher_id = request.POST.get("teacher_id")
    if not teacher_id:
        messages.error(request, _("Teacher does not exist"))
        return redirect(get_redir_url(request))
    teacher = get_object_or_404(Teacher, pk=teacher_id)

    try:
        class_id = request.POST.get("class_id")
        if not class_id:
            raise Group.DoesNotExist
        group = Group.objects.get(pk=class_id)
    except Group.DoesNotExist:
        messages.error(request, _("Group does not exist"))
        return redirect(get_redir_url(request))

    group.teachers.add(teacher)

    notice = u" %s 加入了 %s " % (teacher.name, group.name)
    messages.success(request, notice)
    return redirect(get_redir_url(request))


@school_admin_required
def remove_student(request, class_id, student_id):
    """docstring for remove_rel"""
    group = get_object_or_404(Group, pk=class_id)
    student = get_object_or_404(Student, pk=student_id)

    student.group = None
    student.save()

    notice = u"学生 %s 已从班级 %s 移除" % (student.name, group.name)
    messages.success(request, notice)

    return redirect("manage_class_view", class_id=class_id)


@school_admin_required
def remove_teacher(request, class_id, teacher_id):

    group = get_object_or_404(Group, pk=class_id)
    teacher = get_object_or_404(Teacher, pk=teacher_id)

    group.teachers.remove(teacher)
    # 获得跳转页面。
    redir = get_redir_url(request)
    notice = u"教师 %s 已从 %s 移除" % (teacher.name, group.name)
    messages.success(request, notice)
    return redirect(redir)

