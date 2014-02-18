# -*- coding: utf-8 -*-
from django.shortcuts import redirect, render, get_object_or_404
from kinger.models import Teacher, School, Group, Student,Sms,BirthControl,Guardian,GroupTeacher
from oa.forms import TeacherUserForm,UserProfileForm,OaStudentForm,GuardianForm,BirthControlForm
from django.forms.formsets import formset_factory
from django.core.context_processors import csrf
from django.contrib.auth.models import User
from django.contrib import messages
from django.db.models import Q
from django.utils.translation import ugettext as _
from django.core.exceptions import ObjectDoesNotExist, MultipleObjectsReturned
from django.http import HttpResponse
from django.views.decorators.http import require_POST, require_GET
from django.core.cache import cache
import xlwt, xlrd
from oa import helpers
import datetime
from kinger.settings import SEND_ACCOUNT_TIMEDELTA
from django.contrib.auth.forms import SetPasswordForm
from manage.forms import StudentForm
from oa.decorators import Has_permission
from kinger.helpers import ajax_error,ajax_ok


@Has_permission('manage_student')
def index(request, template_name="oa/student_list.html"):
    """学籍管理列表"""
    s = int(request.GET.get("s", 0))
    g = int(request.GET.get("g", 0))
    t = int(request.GET.get("t", -1))
    n = request.GET.get("n", "")
    p = request.GET.get("p", "")
    a = request.GET.get("a", "")
     
    qs = Q(school_id=s) if s else Q()
    qg = Q(group_id=g) if g else Q()
    qt = Q(status=t) if t == 0 or t == 1 else Q()
    qn = Q(name__contains=n) if n else Q()
    qp = Q(user__profile__mobile=p) if p else Q()
    qa = Q(user__username__contains=a) if a else Q()
    q = qs & qt & qn & qg & qp & qa
    path = request.get_full_path()
    if request.method == 'POST':
        operate = int(request.POST.get('operate'))
        student_pks = request.POST.getlist('start_pks')
        student_list = Student.objects.filter(pk__in=student_pks)
        if operate == 0 or operate == 1:
           student_list.update(status=operate)
           messages.success(request, u"操作成功")
    
        if operate == 2:
            student_list.delete()
            messages.success(request, u"操作成功")
        return redirect(path)
        
 
    schools = helpers.get_schools(request.user)
    schools = [sc for sc in schools if not sc.parent_id==0]
    students = Student.objects.filter(school__in=schools).filter(q)
    groups = Group.objects.filter(school__in=schools).exclude(type=3)
    if s != 0:
        groups = Group.objects.filter(school_id=s)
    
    states = ((0, _('在园')),(1, _('离园')),)
    
    count = students.count()
    ctx = {}
    ctx.update({"students": students,"schools":schools,"groups": groups,"s":s,"t":t,"n":n,'g':g,'states':states,'count':count})
 
    return render(request, template_name, ctx)
 

@Has_permission('manage_student')
def create(request, template_name="oa/student_form.html"):
    """添加学籍"""
    extra = int(request.GET.get("extra", 1))
    if request.method == 'POST':
        form1 = TeacherUserForm(request.POST)
        is_auto = request.POST.get('signup')
        is_valid = form1.is_valid()
        form1_error_list = form1.errors.items()
        if is_auto == "auto":
            form1_error_list = []
            is_valid = True
        form2 = UserProfileForm(request.POST, request.FILES)
        form3 = OaStudentForm(request.POST,user=request.user)
        extra = request.POST['form-TOTAL_FORMS']
        formset = formset_factory(GuardianForm, extra=extra)
        form4 = formset(request.POST)
        form5 = BirthControlForm(request.POST)
        print form2.errors,'22222222'
        print form3.errors,'3333333'
        print form4.errors,'444444444'
        print form5.errors,'55555555'
        
        form4_error_list = []
        for fo in form4:
            form4_error_list = form4_error_list + fo.errors.items()
        
        error_list = form1_error_list + form2.errors.items() + form3.errors.items() + form4_error_list + form5.errors.items()
        if request.is_ajax():
            return helpers.ajax_validate_form_error_list(error_list)
        
        if is_valid and form2.is_valid() and form3.is_valid() and form4.is_valid() and form5.is_valid():
            student = helpers.create_student(form1, request)
            if student.id:
                form2 = UserProfileForm(request.POST, request.FILES, instance=student.user.get_profile())
                form2.save()
                form3 = OaStudentForm(request.POST,instance=student,user=None)
                form3.save()
                for f in form4:
                    guardian = f.save(commit=False)
                    if guardian.name == "empty_name" and guardian.mobile == "13900000000" and guardian.address == "empty_address":
                        pass
                    else:
                        if guardian.name:
                            guardian.student = student
                            guardian.save()
                birthcontrol = form5.save(commit=False)
                birthcontrol.student = student
                birthcontrol.save()
                
                profile = student.user.profile
                if not profile.mobile:
                    try:
                        mobile = Guardian.objects.filter(student=student)[0].mobile
                        profile.mobile = mobile
                        profile.save()
                    except:
                        pass
                messages.success(request, u"学生 %s 已成功创建" % student.name)
                return redirect("oa_student_list")
    else:
        form1 = TeacherUserForm()
        form2 = UserProfileForm()
        form3 = OaStudentForm(user=request.user)
        form4 = formset_factory(GuardianForm, extra=extra)
        form5 = BirthControlForm()
    ctx = {'form1': form1,'form2': form2,'form3': form3,'form4':form4,'form5':form5,'extra':extra}
    ctx.update(csrf(request))
    return render(request, template_name, ctx)

@Has_permission('manage_student')
def update(request, student_id, template_name="oa/student_form.html"):
    """更新学籍"""
    extra = int(request.GET.get("extra", 0))
    schools = helpers.get_schools(request.user)
    schools = [s for s in schools if not s.parent_id==0]
    student = get_object_or_404(Student, pk=student_id,school__in=schools)
    school = student.school
    guardians = student.guardians.all()
    guardian_list = []
    for g in guardians:
        guardian_list.append({'name':g.name,'relation':g.relation,'mobile':g.mobile,'office_phone':g.office_phone,\
                              'other_phone':g.other_phone,'office_email':g.office_email,'other_email':g.other_email,'address':g.address})
    if not guardians.count():
        extra = 1
    if request.method == 'POST':
        password = student.user.password
        form1 = TeacherUserForm(request.POST,instance=student.user)
        form2 = UserProfileForm(request.POST, request.FILES, instance=student.user.get_profile())
        form3 = OaStudentForm(request.POST,user=request.user,instance=student)
        extra = request.POST['form-TOTAL_FORMS']
        formset = formset_factory(GuardianForm, extra=extra)
        form4 = formset(request.POST,initial=guardian_list)
        form5 = BirthControlForm(request.POST,instance=student.birth)
        
        form4_error_list = []
        for fo in form4:
            form4_error_list = form4_error_list + fo.errors.items()
        error_list = form2.errors.items() + form2.errors.items() + form3.errors.items() + form4_error_list + form5.errors.items()
#        if request.is_ajax():
#            return helpers.ajax_validate_form_error_list(error_list)
        
        if form1.is_valid() and form2.is_valid() and form3.is_valid() and form4.is_valid():
            username = form1.clean_username()
            if username:
                student.user.username = username
                student.user.password = password
                student.user.save()
            form2.save()
            form3 = OaStudentForm(request.POST,instance=student,user=request.user)
            student = form3.save(commit=False)
            realname = request.POST['realname']
            if realname:
                student.name = realname
            student.save()
            guardians.delete()
            for f in form4:
                guardian = f.save(commit=False)
                if guardian.name == "empty_name" and guardian.mobile == "13900000000" and guardian.address == "empty_address":
                    pass
                else:
                    if guardian.name:
                        guardian.student = student
                        guardian.save()
            form5.save()

            messages.success(request, u"学生 %s 已成功修改" % student.name)
            return redirect("oa_student_list")
    else:
        form1 = TeacherUserForm(instance=student.user)
        form2 = UserProfileForm(instance=student.user.get_profile())
        form3 = OaStudentForm(instance=student,user=request.user)
        formset = formset_factory(GuardianForm,extra=extra)
        form4 = formset(initial=guardian_list)
        try:
            birth = student.birth
        except:
            birth = BirthControl()
            birth.student = student
            birth.save()
        form5 = BirthControlForm(instance=birth)
#     print form3['group'],form3['school']
    ctx = {'form1': form1,'form2': form2,'form3': form3,'form4':form4,'form5':form5,'extra':extra,'student':student}
    ctx.update(csrf(request))
    return render(request, template_name, ctx)

@Has_permission('manage_student')
def get_extra_form(request,template_name="oa/extra_guardian_form.html"):
    order = int(request.POST.get('order'))
    ctx = {'order':order - 1}
    data = render(request,template_name,ctx)
    con=data.content
    return ajax_ok('成功',con)

def get_school_class(request):
    return helpers.school_class(request)

@Has_permission('manage_send_student_account')
def send_account(request, template_name="oa/student_send_account.html"):  
    """群发家长帐号"""
    ctx = {}
    schools = helpers.get_schools(request.user)
    q = Q(school__in=schools)
    query = request.GET.get('q','')
    school_id = int(request.GET.get('s',0))
    if school_id:
        q = Q(school_id=school_id)
    if query:
        q = q & Q(name__contains=query)

    if request.method == 'POST':
        class_list = request.POST.getlist('class_list')
        
        now = datetime.datetime.now()
        last_time = now + datetime.timedelta(seconds = -SEND_ACCOUNT_TIMEDELTA)
        
        groups =  Group.objects.filter(pk__in=class_list)
        groups.update(send_time=now)
        
        student_list = Student.objects.filter(group__in=class_list).order_by("-ctime")
        is_export = request.POST.get('export')
        if is_export == 'export':
            response = HttpResponse(mimetype="application/ms-excel")
            response['Content-Disposition'] = 'attachment; filename=account_send.xls'
        
            wb = xlwt.Workbook()
            ws = wb.add_sheet(_("Student List"))
        
            for idx, col in enumerate([ _("Name"),_("Username"), _("Password")]):
                ws.write(0, idx, col)
            row = 0
            for s in student_list:
                row += 1 
                new_password = User.objects.make_random_password(length=6,allowed_chars='0123456789')
                data = {'new_password1': new_password, 'new_password2': new_password}
                form = SetPasswordForm(user=s.user, data=data)
        
                if form.is_valid():
                    form.save()
                    col = 0
                    for c in [s.name,s.user.username,new_password]:   
                        ws.write(row,col,c)
                        col += 1
        
            wb.save(response)
            return response

        total_num = student_list.count()
        send_num = 0
        unsend_num = 0
        for student in student_list:
            last_reset = Sms.objects.filter(type_id=100, receiver=student.user,
                                         is_active=True,send_time__gt=last_time,send_time__lte=now).order_by('-send_time')
            if not last_reset.count():
                rs = student.resetPasswordAndSendSms(sender=request.user)
                student.send_time = now
                student.save()
                if rs:
                    send_num += 1
                else:
                    unsend_num += 1
        # 获得cl ，向属于cl的学生发送 帐号信息
        messages.success(request, '家长账号密码成功发送' + str(send_num) + '个,' + str(total_num-send_num-unsend_num) + '个近期已发过。 发送失败' + str(unsend_num) + '个。')
    
    class_list = Group.objects.filter(q).exclude(type=3)
    ctx['class_list'] = class_list
    ctx.update({'query':query,'s':school_id,'schools':schools})
    return render(request, template_name, ctx)


@Has_permission('manage_send_student_account')
def group_send_account(request, group_id, template_name="oa/student_group_send_account.html"):  
    """单独发送家长账号"""
    ctx = {}
    group = get_object_or_404(Group, pk=group_id)
    students = Student.objects.filter(group=group).order_by("-ctime")
    query = request.GET.get('q','')
    status = request.GET.get('s','')
    q = Q()
    if status == 'y':
        q = Q(send_time__isnull=False)
    if status == 'n':
        q = Q(send_time__isnull=True)
    if query:
        q = q & Q(name__contains=query)
    students = students.filter(q)
        
    if request.method == 'POST':
        student_list = request.POST.getlist('student_list')
        
        now = datetime.datetime.now()
        last_time = now + datetime.timedelta(seconds = -SEND_ACCOUNT_TIMEDELTA)
        
        student_list =  Student.objects.filter(pk__in=student_list).order_by("-ctime")
        
        is_export = request.POST.get('export')
        if is_export == 'export':
            response = HttpResponse(mimetype="application/ms-excel")
            response['Content-Disposition'] = 'attachment; filename=account_send.xls'
        
            wb = xlwt.Workbook()
            ws = wb.add_sheet(_("Student List"))
        
            for idx, col in enumerate([ _("Name"),_("Username"), _("Password")]):
                ws.write(0, idx, col)
            row = 0
            for s in student_list:
                row += 1 
                new_password = User.objects.make_random_password(length=6,allowed_chars='0123456789')
                data = {'new_password1': new_password, 'new_password2': new_password}
                form = SetPasswordForm(user=s.user, data=data)
        
                if form.is_valid():
                    form.save()
                    col = 0
                    for c in [s.name,s.user.username,new_password]:   
                        ws.write(row,col,c)
                        col += 1
        
            wb.save(response)
            return response
        
        total_num = student_list.count()
        send_num = 0
        unsend_num = 0
        for student in student_list:
            last_reset = Sms.objects.filter(type_id=100, receiver=student.user,
                                         is_active=True,send_time__gt=last_time,send_time__lte=now).order_by('-send_time')
            if not last_reset.count():
                rs = student.resetPasswordAndSendSms(sender=request.user)
                if rs:
                    student.send_time = now
                    student.save()
                    send_num += 1
                else:
                    unsend_num += 1
        # 获得cl ，向属于cl的学生发送 帐号信息
        messages.success(request, '家长账号密码成功发送' + str(send_num) + '个,' + str(total_num-send_num-unsend_num) + '个近期已发过。 发送失败' + str(unsend_num) + '个。')
   
    ctx['students'] = students
    ctx.update({'students':students,'group':group})
    return render(request, template_name, ctx)

@Has_permission('manage_student')
def template(request):
    """xls template for import"""
    response = HttpResponse(mimetype="application/ms-excel")
    response['Content-Disposition'] = 'attachment; filename=students-template.xls'

    wb = xlwt.Workbook()
    ws = wb.add_sheet(_("Teacher List"))

    for idx, col in enumerate([ _("Class"),_("Name"), _("Mobile")]):
        ws.write(0, idx, col)

    wb.save(response)
    return response

@Has_permission('manage_student')
def batch_import(request, template_name="oa/student_import.html"):
    schools = helpers.get_schools(request.user)
    return render(request, template_name, {'schools':schools})

@Has_permission('manage_student')
def import_view(request):
    """
    """
    # 获得导入数据(文件)
    schools = helpers.get_schools(request.user)
    template_name="oa/student_import.html"
    roles_xls = request.FILES.get('students')
    try:
        school_id = request.POST['school']
        school = get_object_or_404(School, pk=school_id)
    except:
        school = schools[0]
    
    imported_num = 0
    cache_key = "import_student_" + str(school.id) + '_' + str(request.user.id)
    if request.method == 'POST':
        data = cache.get(cache_key)
        if not data:
            messages.error(request, "您还没有上传文件")
            return render(request, template_name, {'schools':schools,'school':school,'file_error':"您还没有上传文件"})
        
        for d in data:
            try:
                student = Student.objects.get(name=d['name'], user__profile__mobile=d['mobile'],group_id=d['group'])
                continue
            except:
                student = helpers.create_student(None, request, school,group_id=d['group'],name=d['name'],batch=True)
                if d['mobile']:
                    profile = student.user.profile
                    profile.mobile = d['mobile']
                    profile.save()
                imported_num = imported_num + 1
                print imported_num,datetime.datetime.now(),'---------------------------------'
        
    if imported_num:
        msg = u"成功导入 %(imported_num)s 个  %(role)s" % {'imported_num': imported_num, 'role': '学生'}
        print msg,'mmmmmmmmmmmmmmmm'
        cache.delete(cache_key)
        messages.success(request, msg)
    return render(request, template_name, {'schools':schools,'school':school})


def check_import(request, template_name="oa/student_import.html"):
    schools = helpers.get_schools(request.user)
    roles_xls = request.FILES.get('students')
    error_list = []
    num = 0
    
    try:
        school_id = request.POST['school']
        school = get_object_or_404(School, pk=school_id)
    except:
        school = schools[0]
    
    if not roles_xls:
        messages.error(request, _("Files Missing"))
        return render(request, template_name, {'schools':schools,'school':school})
    try:
        wb = xlrd.open_workbook(file_contents=roles_xls.read())
        s = wb.sheet_by_index(0)
    except xlrd.biffh.XLRDError:
        messages.error(request, _("Unsupported format, or corrupt file"))
        return render(request, template_name, {'schools':schools,'school':school})
 
    try:
        trans_map = {
            "group": s.cell(0, 0).value,
            "name": s.cell(0, 1).value,
            "mobile": s.cell(0, 2).value
        }
    except:
        trans_map = None
    xls_cache = []  
    for row in range(s.nrows)[1:]:
        num = num + 1
        try:
            mobile = str(int(s.cell(row, 2).value)).strip()
        except:
            mobile = ''
        try:
            class_name = s.cell(row, 0).value.strip()
            name = s.cell(row, 1).value.strip()
        except Exception, e:
            print e
            messages.error(request, u"导入的 Excel 文件缺少需要的列, 或者该列数据为空.")
            return redirect('oa_student_batch_import')
        
       
        try:
            group = Group.objects.get(name=class_name, school=school)
        except:
            error_list.append({'name':name,'mobile':mobile,'row':row,'group':class_name,'msg':'班级名称错误'})
            continue
        
        if mobile:
            try:
                student = Student.objects.get(name=name, user__profile__mobile=mobile,group=group)
                error_list.append({'name':name,'mobile':mobile,'row':row,'group':class_name,'msg':"该学生已存在"})
                continue
            except:
                pass
        
        initial_data = {"name": name, "mobile": mobile,'group':group.id}
        form = StudentForm(initial_data)
        if not form.is_valid():
            error_list.append({'name':name,'mobile':mobile,'row':row,'group':class_name,'msg':form.errors})
            continue
            
       
        xls_cache.append({'name':name,'mobile':mobile,'group':group.id})
        
    cache_key = "import_student_" + str(school.id) + '_' + str(request.user.id)
#     data = cache.get(cache_key)
    rs = cache.set(cache_key, xls_cache)
    
    data = cache.get(cache_key)
    ctx = {'schools':schools,'errors':error_list,'school':school,\
            'num':num,'error_num':len(error_list),'filename':str(roles_xls),'checked':True}
    return render(request, template_name, ctx)


    
