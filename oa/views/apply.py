# -*- coding: utf-8 -*-
from django.shortcuts import render_to_response, redirect, render, get_object_or_404
from django.http import Http404
from django.http import HttpResponse
from kinger.models import School,Registration,GroupGrade,Group,Sms
from oa.forms import RegistrationForm
from oa.helpers import get_site,get_schools
from django.contrib import messages
from django.db.models import Q
from django.core.urlresolvers import reverse
from oa.decorators import Has_permission

@Has_permission('manage_apply')
def index(request,template_name="oa/onlineRegistration.html"):  
    """在线报名列表"""
    schools = get_schools(request.user)
    schools = [s for s in schools if not s.parent_id==0]

    regists = Registration.objects.filter(school__in=schools)
    grades = GroupGrade.objects.all()
    sid = int(request.GET.get("school", -1))
    status = int(request.GET.get("status", -1))
    st = request.GET.get("st", '')
    et = request.GET.get("et", '')
    gid = int(request.GET.get("gid",-1))
    sex = int(request.GET.get("sex",-1))
    bs = request.GET.get("bs", '')
    be = request.GET.get("be", '')
    rid = request.GET.get("rid","")
    
    if request.method == 'POST':
        regist_pks = request.POST.getlist("regist_pks")
        attr = int(request.POST.get('attr',-1))
        if attr != -1:
            regs = Registration.objects.filter(id__in=regist_pks)
            regs.update(status=attr)
        return redirect(request.get_full_path())
    
    q_sid = Q(school_id=sid) if sid != -1 else Q()    
    q_status = Q(status=status) if status != -1 else Q()
    q_st = Q(ctime__gte=st) if st else Q()
    q_et = Q(ctime__lte=et) if et else Q()
    q_gid = Q(group__grade_id=gid) if gid != -1 else Q()
    q_sex = Q(gender=sex) if sex != -1 else Q()
    q_bs = Q(birth_date__gte=st) if bs else Q()
    q_be = Q(birth_date__lte=et) if be else Q()
    try:
        q_rid = Q(id=int(rid))
    except:
        q_rid = Q()
    q = q_sid & q_status & q_st & q_et & q_gid & q_sex & q_bs & q_be & q_rid
    
    regists = regists.filter(q)
    ctx = {'regists':regists,'grades':grades,'status':status,\
           'st':st,'et':et,'gid':gid,'sex':sex,'bs':bs,'be':be,\
           'rid':rid,'schools':schools,'sid':q_sid}
    return render(request, template_name, ctx)

@Has_permission('manage_apply')
def regist_detail(request,regist_id,template_name="oa/onlineRegistration_form.html"):
    """在线报名详情及更新"""
    schools = get_schools(request.user)
    regist = get_object_or_404(Registration,id=regist_id,school__in=schools)
    if request.method == 'POST':
        human = True
        form = RegistrationForm(request.POST,instance=regist)
        if form.is_valid():
            r = form.save(commit=False)
            r.save()
            try:
                mobile = r.guardians.exclude(name='').exclude(mobile='').exclude(unit='')[0].mobile
            except:
                mobile = None
            if r.send_msg and r.msg_body and mobile:
                msg = Sms()
                msg.sender_id = request.user.id
                msg.receiver_id = -1
                msg.mobile = mobile
                msg.type_id = 6
                msg.content = r.msg_body + '/' + request.user.teacher.name
                msg.save()
            messages.success(request, '操作成功')
            
            return redirect('oa_regist_apply_list')
    else:
        form = RegistrationForm(instance=regist)
    guardians = regist.guardians.exclude(relation='').exclude(name='').exclude(mobile='').exclude(unit='')
    guardians_count = guardians.count()
    ctx = {'regist':regist,'form':form,'guardians':guardians,'range':range(4),'guardians_count':guardians_count}
    return render(request, template_name, ctx)

