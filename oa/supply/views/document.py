# -*- coding: utf-8 -*-
from django.shortcuts import redirect, render, get_object_or_404
from kinger.models import School,Teacher,SupplyCategory,Provider,Supply,Material,MaterialReceiver,MaterialApproval,\
    Attachment,MaterialApply,SupplyRecord,Sms
from django.contrib.auth.models import User
from django.core.context_processors import csrf
from django.contrib import messages
from django.db.models import Q
from django.utils.translation import ugettext as _
from django.http import HttpResponse
from django.views.decorators.http import require_POST, require_GET
import datetime
from django.core.exceptions import ObjectDoesNotExist, MultipleObjectsReturned
from userena import signals as userena_signals
from django.core.urlresolvers import reverse
from django.forms.formsets import formset_factory
from oa.decorators import Has_permission
from django.contrib import auth
from django.contrib.auth.views import logout
from oa.helpers import get_schools,is_agency_user,user_manage_school,school_provider,supply_category_group,\
        get_school_with_workgroup,mark_supply_doc_as_read,get_content_type_by_filename
from oa.supply.forms import SupplyCategoryForm,ProviderForm,MaterialForm,SupplyForm
from django.utils.encoding import smart_str, smart_unicode
from django.utils.http import urlquote
import urllib2
from kinger.helpers import ajax_ok
try:
    import simplejson as json
except ImportError:
    import json

import os, tempfile, zipfile
from django.core.servers.basehttp import FileWrapper  
from StringIO import StringIO  
from zipfile import ZipFile
from oa.decorators import Has_permission

@Has_permission('manage_supply_document')
def my_document(request,template_name="supply/my_document_list.html"):
    """我的物资公文列表页"""

    documents = MaterialReceiver.objects.filter(is_send=True,user=request.user).order_by('-document__ctime')
    query = request.GET.get("q", '')
    st = request.GET.get("st", '')
    et = request.GET.get("et", '')
    ty = int(request.GET.get("ty", -1))
   
    qq = Q(document__title__contains=query) if query else Q()
    qs = (Q(document__ctime__startswith=st) | Q(document__ctime__gte=st)) if st else Q()
    qe = (Q(document__ctime__startswith=et) | Q(document__ctime__lte=et)) if et else Q()
    qt = Q(is_read=ty) if ty != -1 else Q()
    q = qs & qe & qq & qt
    
    documents = documents.filter(q)
    ctx = {'documents':documents,'query':query,'ty':ty}
    return render(request, template_name, ctx)

@Has_permission('manage_supply_document')
def write_document(request,template_name="supply/document_form.html"):
    """撰写公文"""
    ctx = {}
    school = get_schools(request.user)[0]
    teachers = Teacher.objects.filter(school=school)
    categorys = SupplyCategory.objects.filter(school=school)
    schools = get_schools(request.user)
    if request.method == 'POST':
        form = MaterialForm(request.POST)
        receiver_pks = request.POST.getlist("to")
        teacher_list = User.objects.filter(pk__in=receiver_pks)
        approvaler_pk = request.POST.get("approvaler",'')
        sid = request.POST.get('sid','')
        if sid:
            sup_school = get_object_or_404(School,id=sid)
        else:
            sup_school = school
        try:
            approvaler = User.objects.get(pk=approvaler_pk)
        except:
            approvaler = None
        ctx.update({'teacher_list':teacher_list,'approvaler':approvaler})    

        if form.is_valid():
            doc = form.save(commit=False)
            doc.school = school
            doc.sender = request.user
            doc.save()
            print doc.type,'tttttttttttttttttttttttt'
             
            #发布对象
            for t in teacher_list:
                receiver = MaterialReceiver()
                receiver.user = t
                receiver.document = doc
                receiver.save()
                       
            #送审
            approvaler_pk = request.POST.get("approvaler",0)
            if doc.is_submit and approvaler_pk:
                approvaler = User.objects.get(pk=approvaler_pk)
                appr = MaterialApproval()
                appr.sender = doc.sender
                appr.document = doc
                appr.remark = doc.remark
                appr.approvaler = approvaler
                appr.send_time = datetime.datetime.now()
                appr.save()
                doc.remark = ''
                doc.save()
                #发送短信
                if doc.send_msg and doc.msg_body:
                    msg = Sms()
                    msg.sender = doc.sender
                    msg.receiver = approvaler
                    msg.mobile = approvaler.get_profile().mobile
                    msg.type_id = 7
                    msg.content = str(doc.msg_body) + '/' + str(doc.sender.get_profile().chinese_name_or_username()) 
                    msg.save()
                
            desc = request.POST.get("applies")
            apply = json.loads(desc)
            for i in apply:
                supply,created = Supply.objects.get_or_create(name=apply[i]['name'],category_id=apply[i]['cat'],parent_id=0,school=sup_school)
                if created:
                    supply.creator = request.user
                    supply.is_show = False
                    supply.save()
                apl = MaterialApply(supply=supply,document=doc,num=apply[i]['num'],school=sup_school)
                apl.save()
                    
            messages.success(request, u"撰写公文成功") 
            if doc.status == 1:
                return redirect('oa_supply_personal_document')
            else:
                return redirect('oa_supply_issued_document')
    else:
        form = MaterialForm()
    
    ctx.update({'form':form,'teachers':teachers,'schools':schools,'categorys':categorys})
    return render(request, template_name, ctx)

@Has_permission('manage_supply_document')
def issued_document(request,template_name="supply/document_issued.html"):
    """已发公文"""
    documents = Material.objects.filter(sender=request.user,status=0).order_by("-ctime")
    query = request.GET.get("q", '')
    st = request.GET.get("st", '')
    et = request.GET.get("et", '')
    tar = request.GET.get("tar", '')
    page = request.GET.get("page", '')
    qq = Q(title__contains=query) if query else Q()
    qs = (Q(ctime__gte=st) | Q(ctime__startswith=st)) if st else Q()
    qe = (Q(ctime__lte=et) | Q(ctime__startswith=et)) if et else Q()
    q = qs & qe & qq
    documents = documents.filter(q)
    
    ctx = {'documents':documents,'query':query,'st':st,'et':et,'tar':tar,'page':page}
    return render(request, template_name, ctx) 

@Has_permission('manage_supply_document')
def document_detail(request,doc_id,template_name="supply/document_detail.html"):
    """公文详情页"""
    doc = get_object_or_404(Material,id=doc_id)
    receivers = MaterialReceiver.objects.filter(document=doc)
    applies = MaterialApply.objects.filter(document=doc)
    mark_supply_doc_as_read(doc,request.user)
    ctx = {'doc':doc,'receivers':receivers,'applies':applies}
    return render(request, template_name, ctx)

@Has_permission('manage_supply_document')
def need_approval(request,template_name="supply/need_approval_list.html"):
    """需我审批列表"""
#    approvals = MaterialApproval.objects.filter(approvaler=request.user,status=0)
    approvals = MaterialApproval.objects.filter(approvaler=request.user,status=0).order_by('-document__ctime')
    query = request.GET.get("q", '')
    st = request.GET.get("st", '')
    et = request.GET.get("et", '')
    
    qq = Q(document__title__contains=query) if query else Q()
    qs = (Q(document__ctime__startswith=st) | Q(document__ctime__gte=st)) if st else Q()
    qe = (Q(document__ctime__startswith=et) | Q(document__ctime__startswith=et)) if et else Q()
    q = qs & qe & qq
    approvals = approvals.filter(q) 
    ctx = {'approvals':approvals,'query':query,'st':st,'et':et}
    return render(request, template_name, ctx) 

@Has_permission('manage_supply_document')
def approval_document(request,doca_id,template_name="supply/document_approval.html"):
    """审批公文"""
    doca = get_object_or_404(MaterialApproval,id=doca_id)
    document = doca.document
    print document.type,'tttt-----------------------------'
    receivers = MaterialReceiver.objects.filter(document=document)
    user_pks = [u.user_id for u in receivers]
    history = MaterialApproval.objects.filter(document=document).order_by('ctime')
    school = document.school
    categorys = SupplyCategory.objects.filter(school=school)
    teachers = Teacher.objects.filter(school=school)
    applies = MaterialApply.objects.filter(document=document,supply__parent_id=0)
    type = request.GET.get("ty", "")
    school_list = get_schools(request.user)
    if doca.status == 2:
        try:
            doca_l = MaterialApproval.objects.filter(approvaler=doca.approvaler)\
                .exclude(id=doca.id).order_by('-send_time')[0]
        except:
            doca_l = None
    else:
        doca_l = None
    
    if request.method == 'POST':
        form = MaterialForm(request.POST,instance=document)
        
        sid = request.POST.get('sid','')
        if sid:
            sup_school = get_object_or_404(School,id=sid)
        else:
            sup_school = school
            
        if form.is_valid():
            doc = form.save(commit=False)
            doc.save()
             
            #发布对象
            receiver_pks = request.POST.getlist("to")

            teacher_list = User.objects.filter(pk__in=receiver_pks)
            
            try:
                MaterialReceiver.objects.filter(document=doc).delete()
            except:
                pass
            for t in teacher_list:
                receiver = MaterialReceiver()
                receiver.user = t
                receiver.document = doc
                receiver.save()
                       
            approvaler_pks = request.POST.getlist("approvaler")
            ty = int(request.POST.get("commit_type"))
            
            #重置物资申请数据
            desc = request.POST.get("applies")  
            set_material_apply(desc,doc,request.user,sup_school)
            
            #直接发出
            if ty == 1:
                doca.remark = doc.remark
                doca.status = 1
                doca.send_time = datetime.datetime.now()
                doca.save()
                
                doc.is_approvaled = True
                doc.save()
                
                #发送信息
                receivers = MaterialReceiver.objects.filter(document=doc)
                receivers.update(is_send=True,send_time=datetime.datetime.now())
            
            #发回公文
            if ty == 2:
                doca.receiver = doca.sender
                doca.remark = doc.remark
                doca.status = 3
                doca.send_time = datetime.datetime.now()
                doca.save()
                
                doc.remark = ''
                doc.save()
                
                appr = MaterialApproval()
                appr.sender = request.user
                appr.document = doc
                appr.remark = doc.remark
                if doca_l:
                    appr.approvaler = doca_l.sender
                else:
                    appr.approvaler = doca.sender
                appr.send_time = datetime.datetime.now() + datetime.timedelta(seconds = 10)
                appr.status = 2
                appr.save()
                
            #送审公文
            if ty == 3:
                teacher_list = Teacher.objects.filter(user__pk__in=approvaler_pks)
                if doc.is_submit and approvaler_pks:
                    doca.receiver = teacher_list[0].user
                    doca.remark = doc.remark
                    doca.status = 3
                    doca.send_time = datetime.datetime.now()
                    doca.save() 
                    
                    doc.remark = ''
                    doc.save()
                    
                    appr = MaterialApproval()
                    appr.sender = request.user
                    appr.document = doc
                    appr.status = 0
                    appr.remark = doc.remark
                    appr.approvaler = teacher_list[0].user
                    appr.send_time = datetime.datetime.now() + datetime.timedelta(seconds = 10)
                    appr.save()
        
            messages.success(request, u"审批公文成功") 
            return redirect('oa_supply_document_need_approval')

    else:
        form = MaterialForm(instance=document)
    schools = get_school_with_workgroup(request.user)
    ctx = {'doca':doca,'history':history,'doc':document,'form':form,'receivers':receivers,'doca_l':doca_l,\
           'teachers':teachers,'user_pks':user_pks,'type':type,'schools':schools,'categorys':categorys,\
           'applies':applies,'school_list':school_list}
    return render(request, template_name, ctx) 

@Has_permission('manage_supply_document')
def having_approvaled(request,template_name="supply/document_having_approvaled.html"):
    """经我审批"""
    approvals = MaterialApproval.objects.filter(approvaler=request.user,status__in=[1,3]).order_by('-document__ctime','-mtime')
    query = request.GET.get("q", '')
    st = request.GET.get("st", '')
    et = request.GET.get("et", '')
    tar = request.GET.get("tar", '')
    page = request.GET.get("page", '')
    qq = Q(document__title__contains=query) if query else Q()
    qs = (Q(document__ctime__gte=st) | Q(document__ctime__startswith=st)) if st else Q()
    qe = (Q(document__ctime__lte=et) | Q(document__ctime__startswith=et)) if et else Q()
    q = qs & qe & qq
    approvals = approvals.filter(q) 
    qa = approvals.query
    qa.group_by = ['document_id']
    from django.db.models.query import QuerySet
    approvals = QuerySet(query=qa, model=MaterialApproval)
    ctx = {'approvals':approvals,'query':query,'st':st,'et':et,'tar':tar,'page':page}
    return render(request, template_name, ctx) 

@Has_permission('manage_supply_document')
def reback_document(request,template_name="supply/document_reback.html"):
    """发回公文"""
    approvals = MaterialApproval.objects.filter(approvaler=request.user,status=2,receiver_id__isnull=True).order_by('-document__ctime')
    query = request.GET.get("q", '')
    st = request.GET.get("st", '')
    et = request.GET.get("et", '')
    qq = Q(document__title__contains=query) if query else Q()
    qs = (Q(document__ctime__gte=st) | Q(document__ctime__startswith=st)) if st else Q()
    qe = (Q(document__ctime__lte=et) | Q(document__ctime__startswith=et)) if et else Q()
    q = qs & qe & qq
    approvals = approvals.filter(q) 
    ctx = {'approvals':approvals,'query':query,'st':st,'et':et}
    return render(request, template_name, ctx) 

@Has_permission('manage_supply_document')
def edit_reback_document(request,doca_id,template_name="supply/document_reback_form.html"):
    """编辑发回给我的公文"""
    doca = get_object_or_404(MaterialApproval,id=doca_id)
    doc = doca.document
    if request.user != doc.sender:
        return redirect(reverse('oa_supply_approval_document',kwargs={'doca_id':doca.id}) + "?ty=reback")
    
    receivers = MaterialReceiver.objects.filter(document=doc)
    user_pks = [u.user_id for u in receivers]
    history = MaterialApproval.objects.filter(document=doc).exclude(id=doca_id)
    school = doc.school
    categorys = SupplyCategory.objects.filter(school=school)
    teachers = Teacher.objects.filter(school=school)
    applies = MaterialApply.objects.filter(document=doc,supply__parent_id=0)
    form = MaterialForm(instance=doc)
    schools = get_school_with_workgroup(request.user)
    school_list = get_schools(request.user)
    print doc.id,'-----------------------'
    ctx = {'doca':doca,'history':history,'doc':doc,'form':form,'applies':applies,'receivers':receivers,\
           'teachers':teachers,'user_pks':user_pks,'categorys':categorys,'schools':schools,'school_list':school_list}
    return render(request, template_name, ctx)

@Has_permission('manage_supply_document')
def invalid_user_document(request,doc_id):
    """作废公文"""
    Material.objects.filter(id=doc_id).update(status=2)
    MaterialApproval.objects.filter(document_id=doc_id).update(is_delete=True)
    MaterialReceiver.objects.filter(document_id=doc_id).update(is_delete=True,is_send=False)
    return redirect(reverse('oa_supply_reback_document'))

@Has_permission('manage_supply_document')
def resave_document(request,doc_id):
    """另存公文"""
    doc = get_object_or_404(Material,id=doc_id)
    Material.objects.filter(id=doc_id).update(status=2)
    MaterialApproval.objects.filter(document_id=doc_id).update(is_delete=True)
    MaterialReceiver.objects.filter(document_id=doc_id).update(is_delete=True,is_send=False)
    applies = doc.applies.all()
    doc.id = None
    doc.status = 1
    doc.save()
    for a in applies:
        a.id = None
        a.document_id = doc.id
        a.save()
    return redirect(reverse('oa_supply_reback_document'))

@Has_permission('manage_supply_document')
def invalid_document(request,template_name="supply/document_invalid.html"):
    """作废公文"""
    documents = Material.objects.filter(sender=request.user,status=2).order_by('-ctime')
    query = request.GET.get("q", '')
    st = request.GET.get("st", '')
    et = request.GET.get("et", '')
    qq = Q(title__contains=query) if query else Q()
    qs = (Q(ctime__gte=st) | Q(ctime__startswith=st)) if st else Q()
    qe = (Q(ctime__lte=et) | Q(ctime__startswith=et)) if et else Q()
    q = qs & qe & qq
    documents = documents.filter(q)
    ctx = {'documents':documents,'query':query,'st':st,'et':et}
    return render(request, template_name, ctx) 

@Has_permission('manage_supply_document')
def delete_document(request,doc_id):
    """删除公文"""
    doc = get_object_or_404(Material,id=doc_id)
    type = doc.status
    doc.delete()
    messages.success(request, u"删除成功") 
    if type == 2:
        return redirect(reverse('oa_supply_invalid_document'))
    return redirect(reverse('oa_supply_personal_document'))

@Has_permission('manage_supply_document')
def personal_document(request,template_name="supply/document_personal.html"):
    """个人文档"""
    documents = Material.objects.filter(sender=request.user,status=1).order_by('-ctime')
    query = request.GET.get("q", '')
    st = request.GET.get("st", '')
    et = request.GET.get("et", '')
    qq = Q(title__contains=query) if query else Q()
    qs = (Q(ctime__gte=st) | Q(ctime__startswith=st)) if st else Q()
    qe = (Q(ctime__lte=et) | Q(ctime__startswith=et)) if et else Q()
    q = qs & qe & qq
    documents = documents.filter(q)
    ctx = {'documents':documents,'query':query,'st':st,'et':et}
    return render(request, template_name, ctx) 

@Has_permission('manage_supply_document')
def update_document(request,doc_id,template_name="supply/document_form.html"):
    """更新公文"""
    ctx = {}
    doc = get_object_or_404(Material,id=doc_id)
    receivers = MaterialReceiver.objects.filter(document=doc)
    school = doc.school
    categorys = SupplyCategory.objects.filter(school=school)
    teachers = Teacher.objects.filter(school=school)
    applies = MaterialApply.objects.filter(document=doc,supply__parent_id=0)
    print applies,'aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa'
    if request.method == 'POST':
        form = MaterialForm(request.POST,instance=doc)
        print form.errors,'eeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeee'
        if form.is_valid():
            doc = form.save(commit=False)
            doc.save()
             
            sid = request.POST.get('sid','')
            if sid:
                sup_school = get_object_or_404(School,id=sid)
            else:
                sup_school = school
            #发布对象
            receiver_pks = request.POST.getlist("to")
            teacher_list = Teacher.objects.filter(pk__in=receiver_pks)
            try:
                MaterialReceiver.objects.filter(document=doc).delete()
            except:
                pass
            for t in teacher_list:
                receiver = MaterialReceiver()
                receiver.user = t.user
                receiver.document = doc
                if not doc.is_submit and doc.status == 0:
                    receiver.is_send = True
                    receiver.send_time = datetime.datetime.now()
                    doc.is_approvaled = True
                    doc.save()
                receiver.save()
            
            #物资清单
            desc = request.POST.get("applies")  
            set_material_apply(desc,doc,request.user,sup_school)
                  
            #送审
            approvaler_pks = request.POST.get("approvaler")
            print approvaler_pks,'-----------------------------'
            if doc.is_submit and approvaler_pks:
                teacher_list = User.objects.get(pk=approvaler_pks)
                print teacher_list,'teacher_list-----------------------'
                appr = MaterialApproval()
                appr.sender = doc.sender
                appr.document = doc
                appr.remark = doc.remark
                appr.approvaler = teacher_list
                appr.send_time = doc.send_time
                appr.save()
                
                doc.remark = ''
                doc.save()
                
            
        return redirect(reverse('oa_supply_personal_document'))
    else:
        form = MaterialForm(instance=doc)
    
    schools = get_school_with_workgroup(request.user)
    ctx.update({'form':form,'teachers':teachers,'doc':doc,'categorys':categorys,\
                'receivers':receivers,'schools':schools,'applies':applies})
    return render(request, template_name, ctx)

def document_applies(request,template_name="supply/document_applies.html"):
    pk = request.GET.get('pk','')
    did = request.GET.get('did','')
    if pk:
        applies = MaterialApply.objects.filter(id=pk)
    if did:
        applies = MaterialApply.objects.filter(document_id=did)
    try:
        doc = applies[0].document
        school = applies[0].school
        type = applies[0].document.type
    except:
        type = 0
        doc = None
        school = None
    print type,'yyyyyyyyyyyyyyyyyyyyyyyyy'
    data = render(request, template_name, {'applies':applies,'ty':type,'doc':doc,'school':school})
    con=data.content
    return ajax_ok('成功',con)

@Has_permission('manage_supply_document')
def cancel_document(request,doc_id):
    """撤回公文"""
    doc = get_object_or_404(Material,id=doc_id)
    if doc.is_approvaled:
        messages.success(request, u"该公文已被审批") 
    else:
        doca = MaterialApproval.objects.filter(document=doc,sender=request.user,status=0)
        if doca.count():
                doca = doca[0]
                doca.status = 4
                doca.save()
        if request.user == doc.sender:
            doc.status = 2
            doc.save()
        messages.success(request, u"操作成功") 
    return redirect(reverse('oa_supply_issued_document'))

def set_material_apply(desc,doc,user,sup_school):
#    try:
    apply = json.loads(desc)
    applies = MaterialApply.objects.filter(document=doc)
    applies.delete()
    for i in apply:
        supply,created = Supply.objects.get_or_create(name=apply[i]['name'],category_id=apply[i]['cat'],parent_id=0,school=sup_school)
        if created:
            supply.creator = user
            supply.is_show = False
            supply.save()
        apl = MaterialApply(supply=supply,document=doc,num=apply[i]['num'],school=sup_school)
        apl.save()
#    except:
#        pass
 
@Has_permission('manage_supply_document')
def download_document(request,file_id):
    """下载公文附件"""
    file = get_object_or_404(Attachment,id=file_id)
    filename = file.name
    
    if "MSIE" in request.META['HTTP_USER_AGENT']:
        filename=urlquote(filename)
    else:
        filename=smart_str(filename)
    response = HttpResponse(file.file, content_type=get_content_type_by_filename(file.file.name))

    response['Content-Disposition'] = 'attachment; filename=%s' % file.file.name
    return response

@Has_permission('manage_supply_document')
def delete_document_file(request):
    """删除公文附件"""
    file_id = request.POST.get('fid')
    try:
        file = get_object_or_404(Attachment,id=file_id)
        file.delete()
        return HttpResponse(json.dumps({'type':'ok','msg':'删除成功'}))
    except:
        return HttpResponse(json.dumps({'type':'error','msg':'删除失败'}))

@Has_permission('manage_supply_document')
def download_zipfile(request,doc_id):  
    """打包下载公文附件""" 
    doc = get_object_or_404(Material,id=doc_id)
    files = doc.files.all()

    in_memory = StringIO()  
    zip = ZipFile(in_memory, "a")  
    for f in files: 
        
        f_name = f.name + '.' + str(f.file).split('.')[-1]
        opener1 = urllib2.build_opener()
        page1 = opener1.open(f.file.url)
        zip.writestr(f_name,page1.read()) 

    for file in zip.filelist:  
        file.create_system = 0      
          
    zip.close()  
    
    filename = doc.title + '.zip'
    if "MSIE" in request.META['HTTP_USER_AGENT']:
        filename=urlquote(filename)
    else:
        filename=smart_str(filename)
  
    response = HttpResponse(mimetype="application/zip")  
    response["Content-Disposition"] = 'attachment; filename=%s' % filename
      
    in_memory.seek(0)      
    response.write(in_memory.read())
      
    return response  
