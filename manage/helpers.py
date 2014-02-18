# -*- coding: utf-8 -*-
from django.db import transaction
from userena import signals as userena_signals

from django.shortcuts import redirect
from kinger.models import Teacher,Group,Student,School
from manage.forms import TeacherForm
from django.core.context_processors import csrf
# from django.contrib.auth.models import User
from django.contrib import messages
from django.utils.translation import ugettext as _
from django.core.exceptions import ObjectDoesNotExist, MultipleObjectsReturned
# import xlwt
import xlrd
# from django.db.models import Q
# from userena import signals as userena_signals
# from manage.forms import TeacherForm


# it can be implemented in form's save method
#@transaction.commit_on_success
def _create_role(form, request, school=None):
    """
    .. 由于私有方法不显示成文档, 所以文档在 ``create_teacher`` 方法中
    """
    mobile = form.cleaned_data['mobile']
    name = form.cleaned_data['name']
    user = School.userObjects.create_user(password=mobile)

    user.first_name = name
    user.save()

    form.user = user
    role = form.save(commit=False)
    role.user = user
    role.creator = request.user
    role.school = school or request.user.manageSchools.latest("id")
    role.save()

    form.save(commit=False)
    # Send the signup complete signal
    userena_signals.signup_complete.send(sender=Student, user=role.user)
    return role


def create_teacher(form, request, school=None):
    """
    | 调用私有方法 ``_create_role``, 该方法有数据会滚作用. 即当其中一条数据操作出错时，回滚其它数据库操作.
    | 创建一个老师. 因为有其它的关联关系要处理，
    | 并且在 ``api``, ``manage`` 模块都有用到，所以独立成一个 ``helper``

    **args/kwargs**

    * *form:* 老师或者学生的 *form*
    * *request:* 当次访问的 ``request``对象
    * *school:* 角色所在学校
    """
    return _create_role(form, request, school)


def create_student(form, request, school=None):
    """
    对 ``_create_role`` 的代理，固定了角色.
    """
    return _create_role(form, request, school)


def list_form_errors(name, form, trans=None):
    """
    单行列出 ``form`` 的错误信息. 目前用于 ``import`` helper

    **args/kwargs**

    * *name:*  该条错误信息的标题
    * *form:*  校验出错的 form
    * *trans:*  字段对应的中文翻译.
    """
    trans = {} if not isinstance(trans, dict) else trans
    errors = u"错误提示: %s, " % trans.get(name, name)
    for k, v in form.errors.items():
        errors += "%s, %s " % (trans.get(k, k), v[0])
    return errors


def importor_view(request, role, form_klass):
    """
    | 批量导入老师/学生通用的导入方法.
    | 以固定的格式获取数据: 学校名称(school), 班级名称(class_name), 姓名(name), 手机(mobile)

    **args/kwargs**

    * *request:*  当次访问的 ``request`` 对象.
    * *role:*  导入的角色(老师 - *teacher* /学生 - *student*)
    * *form_klass:*  创建角色的 ``form`` 类.
    """

    # 获得导入数据(文件)
    redirect_url = "manage_%s_list" % role
    roles_xls = request.FILES.get("%ss" % role)
    role_klass = {"student": Student, "teacher": Teacher}.get(role)
    if not roles_xls:
        messages.error(request, _("Files Missing"))
        return redirect(redirect_url)

    ctx = {}
    try:
        wb = xlrd.open_workbook(file_contents=roles_xls.read())
        s = wb.sheet_by_index(0)
    except xlrd.biffh.XLRDError:
        messages.error(request, _("Unsupported format, or corrupt file"))
        return redirect(redirect_url)

    classes = {}        # 班级数据缓存, 避免多次查询数据库获得班级数据.
    exist_stus = []     # 已导入记录， 避免重复导入.
    imported_num = 0    # 导入个数，提示用
    schools = {}        # 学校数据缓存, 与 ``classes`` 类似
    not_exist_classes = set()   # 记录记录错误的班级明, 错误提示用
    try:
        trans_map = {
            "school": s.cell(0, 0).value,
            "group": s.cell(0, 1).value,
            "name": s.cell(0, 2).value,
            "mobile": s.cell(0, 3).value
        }
    except:
        trans_map = None

    # 第一行为标题，从第二行开始
    for row in range(s.nrows)[1:]:
        try:
            school_name = s.cell(row, 0).value.strip()
            class_name = s.cell(row, 1).value.strip()
            name = s.cell(row, 2).value.strip()
            mobile = s.cell(row, 3).value
            mobile = str(int(s.cell(row, 3).value)).strip()
        except Exception, e:
            print e
            # TODO: more check
            messages.error(request, u"导入的 Excel 文件缺少需要的列, 或者该列数据为空.")
            break
        # 检查执行导入的用户是否有管理导入班级所在学校的操作权限.
        # 即登录用户必须是该学校的管理员.
        try:
            if not schools.get(school_name, None):
                school = request.user.manageSchools.get(name=school_name)
                schools.update({school_name: school})
            school = schools.get(school_name)
        except ObjectDoesNotExist:
            msg = u"你没有权限导入 %s 进 %s." % (role, school_name)
            messages.error(request, msg)
            break

        # 从班级缓存中获取班级对象(queryset) 和 已导入该班级的学生列表
        group, roles = classes.get(class_name, (None, set()))
        if group and name in roles:
            exist_stus.append(name)
            continue

        # 根据导入班级的名称查询班级(如果没有缓存)
        # 同一个学校不能有重复的班级名称
        # 班级信息的记录做出提示，不导入该行数据
        try:
            if class_name:
                group = group or Group.objects.get(name=class_name, school=school)
        except Group.DoesNotExist:
            not_exist_classes.add(class_name)
            continue
        except MultipleObjectsReturned:
            messages.error(request, u"系统错误, 班级名 '%s' 不能相同, 请联系管理员解决这个问题" % class_name)
            continue

        # 检查该行记录是否已经存在于数据库中.
        try:
            role_klass.objects.get(name=name, user__profile__mobile=mobile)
            exist_stus.append(name)
            continue
        except ObjectDoesNotExist:
            pass
        except ValueError:
            mobile = None
        except MultipleObjectsReturned:
            msg = u"系统错误, 重复的 %s: %s, 请联系管理员解决这个问题" % (role, name)
            messages.error(request, msg)
            continue

        # 根据不同角色调用对应的 ``form`` 进行数据校验和保存
        initial_data = {"name": name, "mobile": mobile}
        form = form_klass(initial_data) if role == "teacher" else form_klass(initial_data, user=request.user)
        if not form.is_valid():
            messages.error(request, list_form_errors(name, form, trans_map))
            continue

        role_obj = _create_role(form, request, school)

        imported_num = imported_num + 1
        if group:
            # 添加角色与用户的依赖关系.
            rel = group.students if role == "student" else group.teachers
            rel.add(role_obj)

        # 登记并缓存已导入的记录
        roles.add(name)
        if class_name:
            classes[class_name] = (group, roles)

    if len(exist_stus):
        messages.warning(request, u" %s 已经存在" % ", ".join(exist_stus))
    if len(not_exist_classes):
        messages.error(request, u" %s 不存在" % ", ".join(not_exist_classes))
    if imported_num:
        role_name = {'student':'学生','teacher':'教师'}
        msg = u"成功导入 %(imported_num)s 个  %(role)s" % {'imported_num': imported_num, 'role': role_name.get(role)}
        messages.success(request, msg)
    ctx.update(csrf(request))
    return redirect(redirect_url)

def is_teacher(user):
    """是否为老师用户"""
    try:
        d = isinstance(user.teacher,Teacher)
        if d:
            return True
        else:
            return False
    except Exception:
        return False

def is_student(user):
    """是否为家长用户"""
    try:
        d = isinstance(user.student,Student)
        if d:
            return True
        else:
            return False
    except Exception:
        return False
