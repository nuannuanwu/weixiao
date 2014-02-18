# -*- coding: utf-8 -*-
from django.shortcuts import redirect, render, get_object_or_404
from kinger.models import Teacher, School, Group, PostJob,Sms,Role
from oa.forms import TeacherUserForm,UserProfileForm,PostJobForm
from django.contrib.auth.models import User
from django.core.context_processors import csrf
from django.contrib import messages
from django.db.models import Q
from django.utils.translation import ugettext as _
from django.core.exceptions import ObjectDoesNotExist, MultipleObjectsReturned
from django.http import HttpResponse
from django.views.decorators.http import require_POST, require_GET
import xlwt, xlrd
from django.http import HttpResponse
from django.core.cache import cache
from oa import helpers
import datetime
from kinger.settings import SEND_ACCOUNT_TIMEDELTA
from django.core.exceptions import ObjectDoesNotExist, MultipleObjectsReturned
from manage.forms import TeacherForm
from kinger.helpers import ajax_error,ajax_ok
from oa import helpers
from oa.decorators import Has_permission
try:
    import simplejson as json
except ImportError:
    import json


@Has_permission('manage_teacher')
def index(request, template_name="oa/teacher_list.html"):
   
    s = int(request.GET.get("s", 0))
    t = int(request.GET.get("t", -1))
    n = request.GET.get("n", "")
    p = request.GET.get("p", "")
    a = request.GET.get("a", "")
    
    qs = Q(school_id=s) if s else Q()
    qt = Q(postjob__status=t) if t == 0 or t == 1 else Q()
    qn = Q(name__contains=n) if n else Q()
    qp = Q(user__profile__mobile=p) if p else Q()
    qa = Q(user__username__contains=a) if a else Q()
    q = qs & qt & qn & qp & qa

    if request.method == 'POST':
        operate = int(request.POST.get('operate'))
        teacher_pks = request.POST.getlist('start_pks')
        print teacher_pks,'pppppppppppp'
        teacher_list = Teacher.objects.filter(pk__in=teacher_pks)
        print teacher_list,'llllllllllllllll'
        postjob_list = PostJob.objects.filter(teacher_id__in=teacher_pks)
        print operate,'ooooooooooooooooooo'
        if operate == 0 or operate == 1:
           postjob_list.update(status=operate)
           messages.success(request, u"操作成功")
        if operate == 2:
            teacher_list.update(is_delete=True)
            messages.success(request, u"操作成功")
        if operate == 3:
            for t in teacher_list:
                t.school.admins.add(t.user)
                print t.school.admins.all(),'33333333333333333333333'
            messages.success(request, u"操作成功")
        if operate == 4:
            for t in teacher_list:
                t.school.admins.remove(t.user)
                print t.school.admins.all(),'44444444444444444444'
            messages.success(request, u"操作成功")
        return redirect(request.get_full_path())
        
    schools = helpers.get_schools(request.user)
    teachers = Teacher.objects.filter(school__in=schools).filter(q)
    teachers = teachers.filter(is_delete=False)
    states = ((0, _('在职')),(1, _('离职')),)
    
    count = teachers.count()
    ctx = {}
    ctx.update({"teachers": teachers,"schools":schools,"s":s,"t":t,"n":n,"states":states,'count':count})

    return render(request, template_name, ctx)

@Has_permission('manage_teacher')
def delete(request, teacher_id):
    """delete a teacher"""
    schools = helpers.get_schools(request.user)
    teacher = get_object_or_404(Teacher, pk=teacher_id, school__in=schools)
    teacher.delete()
    messages.success(request, _('Teacher deleted'))
    return redirect("manage_teacher_list")

@Has_permission('manage_teacher')
def create(request, template_name="oa/teacher_form.html"):

    roles = Role.objects.all()
    if request.method == 'POST':
        form1 = TeacherUserForm(request.POST)
        is_auto = request.POST.get('signup')
        is_valid = form1.is_valid()
        form1_error_list = form1.errors.items()
        if is_auto == "auto":
            form1_error_list = []
            is_valid = True
        print is_valid,'v11111111111'
        form2 = UserProfileForm(request.POST, request.FILES)
        print form2.errors,'2222222'
        form3 = PostJobForm(request.POST,user=request.user)
        print form3.errors,'3333333'
        
        error_list = form1_error_list + form2.errors.items() + form3.errors.items()
        if request.is_ajax():
            return helpers.ajax_validate_form_error_list(error_list)
        
        if is_valid and form2.is_valid() and form3.is_valid():
            #新建用户
            teacher = helpers.create_teacher(form1, request)
            print teacher,'vvvvvvvv'
            
            role_pks = request.POST.getlist('role_list')
            role_list = [r for r in Role.objects.filter(pk__in=role_pks)]
            if teacher.id:
                for role in role_list:
                    teacher.user.roles.add(role)
                form2 = UserProfileForm(request.POST, request.FILES, instance=teacher.user.get_profile())
                form2.save()
                form3 = PostJobForm(request.POST,user=request.user)
                postjob = form3.save(commit=False)
                postjob.teacher = teacher
                postjob.save()
                messages.success(request, u"教师 %s 已成功创建" % teacher.name)
                return redirect("oa_teacher_list")
    else:
        form1 = TeacherUserForm()
        form2 = UserProfileForm()
        form3 = PostJobForm(user=request.user)
#         form4 = TeachernameForm()
    ctx = {'form1': form1,'form2': form2,'form3': form3,'roles':roles}
    ctx.update(csrf(request))
    return render(request, template_name, ctx)

@Has_permission('manage_teacher')
def update(request, teacher_id, template_name="oa/teacher_form.html"):
    """update a teacher"""
    schools = helpers.get_schools(request.user)
    teacher = get_object_or_404(Teacher, pk=teacher_id, school__in=schools)
    
    roles = Role.objects.all()
    role_pks = [r.id for r in teacher.user.roles.all()]
    user_role_pks = ','.join([str(r.pk) for r in teacher.user.roles.all()])
    school = teacher.school
    try:
        postjob = teacher.postjob
    except:
        postjob = PostJob(teacher=teacher,school=school)
        postjob.save()
    if request.method == 'POST':
        password = teacher.user.password
        form1 = TeacherUserForm(request.POST,instance=teacher.user)

        form2 = UserProfileForm(request.POST, request.FILES,instance=teacher.user.get_profile())
        form3 = PostJobForm(request.POST,instance=teacher.postjob)
        
        error_list = form1.errors.items() + form2.errors.items() + form3.errors.items()
        if request.is_ajax():
            return helpers.ajax_validate_form_error_list(error_list)
        
        print form1.errors,'11111111'
        print form2.errors,'22222222'
        print form3.errors,'33333333'
        if form1.is_valid() and form2.is_valid() and form3.is_valid():
            username = form1.clean_username()
            if username:
                teacher.user.username = username
                teacher.user.password = password
                teacher.user.save()
            profile = form2.save(commit=False)
            realname = request.POST['realname']
            if realname:
                teacher.name = realname
                teacher.save()
            form3.save()
            
            role_pks = request.POST.getlist('role_list')
            role_list = [r for r in Role.objects.filter(pk__in=role_pks)]
            teacher.user.roles = role_list
            
            messages.success(request, u"教师 %s 已成功修改" % teacher.name)
            return redirect("oa_teacher_list")
    else:
        form1 = TeacherUserForm(instance=teacher.user)
        form2 = UserProfileForm(instance=teacher.user.get_profile())
        form3 = PostJobForm(instance=teacher.postjob,user=request.user)
    ctx = {'form1': form1,'form2': form2,'form3': form3,'teacher':teacher,\
           'user_role_pks':user_role_pks,'roles':roles,'role_pks':role_pks}
    ctx.update(csrf(request))
    return render(request, template_name, ctx)

@Has_permission('manage_teacher')
def get_school_agency(request):
    sid = request.GET.get("sid", "")
    return helpers.school_agency(sid)

@Has_permission('manage_teacher')
def get_pre_username(request):
    return helpers.pre_username()

@Has_permission('manage_send_teacher_account')
def send_account(request, template_name="oa/teacher_send_account.html"):  
    """群发教师帐号"""
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
        teacher_list = request.POST.getlist('teacher_list')
        total_num = len(teacher_list)
        send_num = 0
        unsend_num = 0

        tl = Teacher.objects.filter(pk__in=teacher_list)

        for t in tl:                
            now = datetime.datetime.now()
            t.send_time = now
            t.save()
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
        messages.success(request,'职员账号密码成功发送' + str(send_num) + '个，' + str(total_num - send_num - unsend_num) + '个近期已发过，请耐心等候。 发送失败' + str(unsend_num) + '个。')
    
    teacher_list = Teacher.objects.filter(q).filter(is_delete=False)
    ctx['teacher_list'] = teacher_list       
    ctx.update({'query':query,'s':school_id,'schools':schools})
    return render(request, template_name, ctx)

@Has_permission('manage_teacher')
def template(request):
    """xls template for import"""
    response = HttpResponse(mimetype="application/ms-excel")
    response['Content-Disposition'] = 'attachment; filename=staffs-template.xls'

    wb = xlwt.Workbook()
    ws = wb.add_sheet(_("Teacher List"))

    for idx, col in enumerate([ _("Name"), _("Mobile")]):
        ws.write(0, idx, col)

    wb.save(response)
    return response

@Has_permission('manage_teacher')
def batch_import(request, template_name="oa/teacher_import.html"):
    schools = helpers.get_schools(request.user)
    return render(request, template_name, {'schools':schools})

@Has_permission('manage_teacher')
def import_view(request):
    """
    """
    # 获得导入数据(文件)
    schools = helpers.get_schools(request.user)
    template_name="oa/teacher_import.html"
    roles_xls = request.FILES.get('teachers')
    
    try:
        school_id = request.POST['school']
        school = get_object_or_404(School, pk=school_id)
    except:
        school = schools[0]

    imported_num = 0
    cache_key = "import_teacher_" + str(school.id) + '_' + str(request.user.id)
    if request.method == 'POST':
        data = cache.get(cache_key)
        if not data:
            messages.error(request, "您还没有上传文件")
            return render(request, template_name, {'schools':schools,'school':school,'file_error':"您还没有上传文件"})
        
        for d in data:
            try:
                teacher = Teacher.objects.get(name=d['name'],school=school)
                continue
            except:
                teacher = helpers.create_teacher(None, request, school,batch=True)
                teacher.name = d['name']
                teacher.save()
                profile = teacher.user.profile
                profile.mobile = d['mobile']
                profile.save()
                imported_num = imported_num + 1
        
    if imported_num:
        msg = u"成功导入 %(imported_num)s 个  %(role)s" % {'imported_num': imported_num, 'role': '职员'}
        cache.delete(cache_key)
        messages.success(request, msg)
    return render(request, template_name, {'schools':schools,'school':school})


def check_import(request, template_name="oa/teacher_import.html"):
    schools = helpers.get_schools(request.user)
    
    roles_xls = request.FILES.get('teachers')
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
            "name": s.cell(0, 0).value,
            "mobile": s.cell(0, 1).value
        }
    except:
        trans_map = None
    xls_cache = []  
    for row in range(s.nrows)[1:]:
        num = num + 1
        
        try:
            mobile = mobile = str(int(s.cell(row, 1).value)).strip()
        except:
            mobile = ''
        try:
            name = s.cell(row, 0).value.strip()
        except Exception, e:
            print e
            messages.error(request, u"导入的 Excel 文件缺少需要的列, 或者该列数据为空.")
            return redirect('oa_teacher_batch_import')
          
        try:
            teacher = Teacher.objects.get(name=name, user__profile__mobile=mobile,school=school)
            if teacher and teacher.user.profile.mobile:
                error_list.append({'name':name,'mobile':mobile,'row':row,'msg':"姓名和手机已存在"})
            continue
        except:
            pass
        
        initial_data = {"name": name, "mobile": mobile}
        form = TeacherForm(initial_data)
        if not form.is_valid():
            error_list.append({'name':name,'mobile':mobile,'row':row,'msg':form.errors})
            continue
        print name,mobile
        xls_cache.append({'name':name,'mobile':mobile})
    cache_key = "import_teacher_" + str(school.id) + '_' + str(request.user.id)
    rs = cache.set(cache_key, xls_cache)
    
    data = cache.get(cache_key)
    ctx = {'schools':schools,'errors':error_list,'school':school,\
            'num':num,'error_num':len(error_list),'filename':str(roles_xls),'checked':True}
    return render(request, template_name, ctx)
    


    
@Has_permission('manage_teacher')
def user_role(request, template_name="oa/teacher_user_role.html"):
    """ 分配用户角色 """

    uid = request.POST.get('user_id')
    if not uid:
        return ajax_error('失败')
    uid = int(uid)
    try:
        user = User.objects.get(pk=uid)
    except Exception, e:
        return ajax_error('失败')
    
    tid = int(request.POST.get('teacher_id'))
    try:
        teacher = Teacher.objects.get(pk=tid)
        user_roles = [r for r in teacher.user.roles.all()]
        user_role_pks = ','.join([str(r.pk) for r in teacher.user.roles.all()])
    except:
        user_roles = []
        user_role_pks = ''
 
    schools = helpers.get_schools(request.user)
    q = request.POST.get("q", "")
    s = int(request.POST.get("s", 0))
    roles = Role.objects.filter(school__in=schools)
    if s:
        roles = roles.filter(school_id=s)
    if q:
        roles = roles.filter(name__contains=q)
        
    ctx = {'roles':roles,'query':q,'schools':schools,'s':s,'user':user,\
           'user_roles':user_roles,'user_role_pks':user_role_pks}
    data = render(request,template_name,ctx)
    con=data.content
    return ajax_ok('成功',con)

def change_status(request):
    tid = int(request.POST.get('tid'))
    p = PostJob.objects.get(teacher_id=tid)
    s = p.status
    if s == 0:
        p.status = 1
        p.save()
    if s == 1:
        p.status = 0
        p.save()
    data = json.dumps({'status':p.status})
    return HttpResponse(data)
        
    
    
    
    
    