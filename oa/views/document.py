# -*- coding: utf-8 -*-
from django.shortcuts import render_to_response, redirect, render, get_object_or_404
from django.http import Http404
from django.http import HttpResponse
from django.contrib.auth.models import User
from kinger.models import School,DocumentCategory,Attachment,Document,Teacher,DocumentReceiver,\
            DocumentApproval,Group,GroupGrade,Position,PostJob,Department,WorkGroup,Sms,Material
from oa.forms import AlbumForm,PhotoForm,PartForm,LinkForm,DocumentCategoryForm,DocumentForm
from django.contrib import messages
from django.core.urlresolvers import reverse
from django.forms.formsets import formset_factory
from kinger.helpers import ajax_error,ajax_ok
from django.utils.encoding import smart_str, smart_unicode
from django.utils.http import urlquote
from oa import helpers
from oa.helpers import get_schools,get_category_group,mark_as_read,get_school_with_workgroup,get_content_type_by_filename
import urllib2
from django.db.models import Q
from django.db.models.query import QuerySet
import datetime
try:
    import simplejson as json
except ImportError:
    import json
import os, tempfile, zipfile  
from django.http import HttpResponse  
from django.core.servers.basehttp import FileWrapper  
from StringIO import StringIO  
from zipfile import ZipFile
from oa.decorators import Has_permission


@Has_permission('manage_document_type')
def category(request, template_name="oa/document_category_form.html"):
    """公文类别设置"""
    school = get_schools(request.user)[0]
    extra = int(request.GET.get("extra", 0))
    categorys = []
    category_list = []
    for p in DocumentCategory.objects.filter(school=school,parent_id=0):
        categorys.append(p)
        category_list.append({'name':p.name,'parent':None})
        for s in DocumentCategory.objects.filter(school=school,parent=p):
            categorys.append(s)
            category_list.append({'name':s.name,'parent':s.parent})
    
    if request.method == 'POST':
        extra = request.POST['form-TOTAL_FORMS']
        formset = formset_factory(DocumentCategoryForm, extra=extra)
        form = formset(request.POST,initial=category_list)
        
        if request.is_ajax():
            error_list = []
            for fo in for4:
                error_list = error_list + fo.errors.items()
            return helpers.ajax_validate_form_error_list(error_list)
        
        if form.is_valid():
            i = 0
            for f in form:
                try:
                    cat = categorys[i]
                    cat.name = f['name'].value()
                    cat.save()
                except:
                    cat = f.save(commit=False)
                    if not f['parent'].value():
                        cat.parent_id = 0
                    cat.school = school
                    cat.save()
                i += 1
            messages.success(request, u'操作成功')
            return redirect('oa_document_category') 
    else:
        formset = formset_factory(DocumentCategoryForm,extra=extra)
        form = formset(initial=category_list)

    ctx = {'form':form,'extra':extra,'categorys':categorys}
    return render(request, template_name, ctx)

@Has_permission('manage_document_type')
def delete_category(request,cat_id):
    """删除公文类别"""
    school = get_schools(request.user)[0]
    category = get_object_or_404(DocumentCategory,id=cat_id,school=school)
    if category.parent_id == 0:
        sub_categories = DocumentCategory.objects.filter(parent=category)
        sub_categories.delete()
    category.delete()
    messages.success(request, u'删除成功')
    return redirect('oa_document_category')

@Has_permission('manage_document')
def get_extra_form(request,template_name="oa/extra_form.html"):
    """公文类别附加表单"""
    order = int(request.POST.get('order'))
    formset = formset_factory(DocumentCategoryForm, extra=order + 1)
    form = formset()
    pid = request.POST.get('parent_id',0)
    parent = None
    if pid:
        parent_list = []
        parent = get_object_or_404(DocumentCategory,id=pid)
        for i in range(order):
            parent_list.append({'name':'','parent':parent})
        form = formset(initial=parent_list)
    
    form = form[order]
    ctx = {'form':form,'order':order,'parent':parent}
    
    data = render(request,template_name,ctx)
    con=data.content
    return ajax_ok('成功',con)

@Has_permission('manage_document')
def write_document(request,template_name="oa/document_form.html"):
    """撰写公文"""
    ctx = {}
    school = get_schools(request.user)[0]
    category_group = get_category_group(school)
    teachers = Teacher.objects.filter(school=school)
    
    if request.method == 'POST':
        form = DocumentForm(request.POST)
        receiver_pks = request.POST.getlist("to")
        teacher_list = User.objects.filter(pk__in=receiver_pks)
        approvaler_pk = request.POST.get("approvaler",'')
        try:
            approvaler = User.objects.get(pk=approvaler_pk)
        except:
            approvaler = None
        category_pk = int(request.POST.get("category",0))
        ctx.update({'teacher_list':teacher_list,'approvaler':approvaler,'category_pk':category_pk})    
        
        if request.is_ajax():
            return helpers.ajax_validate_form(form)
        
        if form.is_valid():
            doc = form.save(commit=False)
            doc.school = school
            doc.sender = request.user
            doc.save()
             
            #发布对象
            for t in teacher_list:
                receiver = DocumentReceiver()
                receiver.user = t
                receiver.document = doc
                if not doc.is_submit and doc.status == 0:
                    receiver.is_send = True
                    receiver.send_time = datetime.datetime.now()
                    doc.is_approvaled = True
                    doc.save()
                if doc.send_msg and doc.status == 0 and doc.msg_body:
                    msg = Sms()
                    msg.sender = doc.sender
                    msg.receiver = t
                    msg.mobile = t.get_profile().mobile
                    msg.type_id = 7
                    msg.content = str(doc.msg_body) + '/' + str(doc.sender.get_profile().chinese_name_or_username()) 
                    msg.save()
                receiver.save()
                       
            #送审
            approvaler_pk = request.POST.get("approvaler",0)
            if doc.is_submit and approvaler_pk:
                approvaler = User.objects.get(pk=approvaler_pk)
                appr = DocumentApproval()
                appr.sender = doc.sender
                appr.document = doc
                appr.remark = doc.remark
                appr.approvaler = approvaler
                appr.send_time = datetime.datetime.now()
                appr.save()
#                doc.send_time = datetime.datetime.now()
                doc.remark = ''
                doc.save()
                
            #附件
            for f in request.FILES.getlist('files'):
                atta = Attachment()
                atta.name = f.name
                atta.file = f
                atta.save()
                doc.files.add(atta)
            
            messages.success(request, u"撰写公文成功") 
            if doc.status == 1:
                return redirect('oa_personal_document')
            else:
                return redirect('oa_issued_document')
    else:
        form = DocumentForm()
    
    schools = get_school_with_workgroup(request.user)
    ctx.update({'form':form,'teachers':teachers,'category_group':category_group,'schools':schools})
    return render(request, template_name, ctx)

@Has_permission('manage_document')
def my_document(request,template_name="oa/my_document_list.html"):
    """我的公文列表页"""
#    documents = DocumentReceiver.objects.filter(is_send=True,user=request.user).order_by('-mtime')
    documents = DocumentReceiver.objects.filter(is_send=True,user=request.user).order_by('-document__ctime')
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
    ctx = {'documents':documents,'query':query,'st':st,'et':et,'ty':ty}
    return render(request, template_name, ctx)
  
@Has_permission('manage_document')  
def document_detail(request,doc_id,template_name="oa/document_detail.html"):
    """公文详情页"""
    doc = get_object_or_404(Document,id=doc_id)
    files = doc.files.all()
    receivers = DocumentReceiver.objects.filter(document=doc)
    mark_as_read(doc,request.user)
    ctx = {'doc':doc,'files':files,'receivers':receivers}
    return render(request, template_name, ctx)
    
@Has_permission('manage_document')
def download_document(request,file_id):
    """下载公文附件"""
    file = get_object_or_404(Attachment,id=file_id)
    filename = file.name
    
    if "MSIE" in request.META['HTTP_USER_AGENT']:
        filename=urlquote(filename)
    else:
        filename=smart_str(filename)
    response = HttpResponse(file.file, content_type=get_content_type_by_filename(file.file.name))

    response['Content-Disposition'] = 'attachment; filename=%s' % filename
    return response

@Has_permission('manage_document')
def delete_document_file(request):
    """删除公文附件"""
    file_id = request.POST.get('fid')
    try:
        file = get_object_or_404(Attachment,id=file_id)
        file.delete()
        return HttpResponse(json.dumps({'type':'ok','msg':'删除成功'}))
    except:
        return HttpResponse(json.dumps({'type':'error','msg':'删除失败'}))

@Has_permission('manage_document')  
def download_zipfile(request,doc_id):  
    """打包下载公文附件""" 
    doc = get_object_or_404(Document,id=doc_id)
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

@Has_permission('manage_document')
def need_approval(request,template_name="oa/need_approval_list.html"):
    """需我审批列表"""
#    approvals = DocumentApproval.objects.filter(approvaler=request.user,status=0)
    approvals = DocumentApproval.objects.filter(approvaler=request.user,status=0).order_by('-document__ctime')
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
    
@Has_permission('manage_document')
def approval_document(request,doca_id,template_name="oa/document_approval.html"):
    """审批公文"""
    doca = get_object_or_404(DocumentApproval,id=doca_id)
    document = doca.document
    files = document.files.all()
    receivers = DocumentReceiver.objects.filter(document=document)
    user_pks = [u.user_id for u in receivers]
    history = DocumentApproval.objects.filter(document=document).order_by('ctime')
    school = document.school
    category_group = get_category_group(school)
    teachers = Teacher.objects.filter(school=school)
    type = request.GET.get("ty", "")
    if doca.status == 2:
        try:
            doca_l = DocumentApproval.objects.filter(approvaler=doca.approvaler)\
                .exclude(id=doca.id).order_by('-send_time')[0]
        except:
            doca_l = None
    else:
        doca_l = None
    
    if request.method == 'POST':
        form = DocumentForm(request.POST,instance=document)
        
        if request.is_ajax():
            return helpers.ajax_validate_form(form)
        
        if form.is_valid():
            doc = form.save(commit=False)
            doc.save()
             
            #发布对象
            receiver_pks = request.POST.getlist("to")

            teacher_list = User.objects.filter(pk__in=receiver_pks)
#             exist_user_pks = [u.user.id for u in DocumentReceiver.objects.filter(document=doc)]
#             teacher_list = teacher_list.exclude(user_id__in=exist_user_pks)
            try:
                DocumentReceiver.objects.filter(document=doc).delete()
            except:
                pass
            for t in teacher_list:
                receiver = DocumentReceiver()
                receiver.user = t
                receiver.document = doc
                receiver.save()
                       
            approvaler_pks = request.POST.getlist("approvaler")
            ty = int(request.POST.get("commit_type"))
            
            #直接发出
            if ty == 1:
                doca.remark = doc.remark
                doca.status = 1
                doca.send_time = datetime.datetime.now()
                doca.save()
                
                doc.is_approvaled = True
                doc.save()
                
                #发送信息
                receivers = DocumentReceiver.objects.filter(document=doc)
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
                
                appr = DocumentApproval()
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
                    
                    appr = DocumentApproval()
                    appr.sender = request.user
                    appr.document = doc
                    appr.status = 0
                    appr.remark = doc.remark
                    appr.approvaler = teacher_list[0].user
                    appr.send_time = datetime.datetime.now() + datetime.timedelta(seconds = 10)
                    appr.save()
            #附件
            for f in request.FILES.getlist('files'):
                atta = Attachment()
                atta.name = f.name.split('.')[0]
                atta.file = f
                atta.save()
                doc.files.add(atta)
        
            messages.success(request, u"审批公文成功") 
            return redirect('oa_approvaled_document')

    else:
        form = DocumentForm(instance=document)
    schools = get_school_with_workgroup(request.user)
    ctx = {'doca':doca,'history':history,'doc':document,'form':form,'files':files,'receivers':receivers,'doca_l':doca_l,\
           'teachers':teachers,'user_pks':user_pks,'category_group':category_group,'type':type,'schools':schools}
    return render(request, template_name, ctx) 

@Has_permission('manage_document')
def having_approvaled(request,template_name="oa/document_having_approvaled.html"):
    """经我审批"""
#    approvals = DocumentApproval.objects.filter(approvaler=request.user,status__in=[1,3])
    approvals = DocumentApproval.objects.filter(approvaler=request.user,status__in=[1,3]).order_by('-document__ctime','-mtime')
    query = request.GET.get("q", '')
    st = request.GET.get("st", '')
    et = request.GET.get("et", '')
    qq = Q(document__title__contains=query) if query else Q()
    qs = (Q(document__ctime__gte=st) | Q(document__ctime__startswith=st)) if st else Q()
    qe = (Q(document__ctime__lte=et) | Q(document__ctime__startswith=et)) if et else Q()
    q = qs & qe & qq
    approvals = approvals.filter(q) 
    qa = approvals.query
    qa.group_by = ['document_id']
    from django.db.models.query import QuerySet
    approvals = QuerySet(query=qa, model=DocumentApproval)
    ctx = {'approvals':approvals,'query':query,'st':st,'et':et}
    return render(request, template_name, ctx) 

@Has_permission('manage_document')
def issued_document(request,template_name="oa/document_issued.html"):
    """已发公文"""
    documents = Document.objects.filter(sender=request.user,status=0).order_by("-ctime")
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

@Has_permission('manage_document')
def cancel_document(request,doc_id):
    """撤回公文"""
    doc = get_object_or_404(Document,id=doc_id)
    if doc.is_approvaled:
        messages.success(request, u"该公文已被审批") 
    else:
        doca = DocumentApproval.objects.filter(document=doc,sender=request.user,status=0)
        if doca.count():
                doca = doca[0]
                doca.status = 4
                doca.save()
        if request.user == doc.sender:
            doc.status = 2
            doc.save()
        messages.success(request, u"操作成功") 
    return redirect(reverse('oa_issued_document'))

@Has_permission('manage_document')
def reback_document(request,template_name="oa/document_reback.html"):
    """发回公文"""
#    approvals = DocumentApproval.objects.filter(approvaler=request.user,status=2,receiver_id__isnull=True)
    approvals = DocumentApproval.objects.filter(approvaler=request.user,status=2,receiver_id__isnull=True).order_by('-document__ctime')
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

@Has_permission('manage_document')
def invalid_document(request,template_name="oa/document_invalid.html"):
    """作废公文"""
    documents = Document.objects.filter(sender=request.user,status=2).order_by('-ctime')
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

@Has_permission('manage_document')
def personal_document(request,template_name="oa/document_personal.html"):
    """个人文档"""
    documents = Document.objects.filter(sender=request.user,status=1).order_by('-ctime')
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

@Has_permission('manage_document')
def delete_document(request,doc_id):
    """删除公文"""
    doc = get_object_or_404(Document,id=doc_id)
    type = doc.status
    doc.delete()
    messages.success(request, u"删除成功") 
    if type == 2:
        return redirect(reverse('oa_invalid_document'))
    return redirect(reverse('oa_personal_document'))

@Has_permission('manage_document')
def update_document(request,doc_id,template_name="oa/document_form.html"):
    """更新公文"""
    ctx = {}
    doc = get_object_or_404(Document,id=doc_id)
    files = doc.files.all()
    category_group = get_category_group(doc.school)
    receivers = DocumentReceiver.objects.filter(document=doc)
    teachers = Teacher.objects.filter(school=doc.school)
    if request.method == 'POST':
        form = DocumentForm(request.POST,instance=doc)
        
        if request.is_ajax():
            return helpers.ajax_validate_form(form)
        
        if form.is_valid():
            doc = form.save(commit=False)
            doc.save()
             
            #发布对象
            receiver_pks = request.POST.getlist("to")
            teacher_list = Teacher.objects.filter(pk__in=receiver_pks)
            try:
                DocumentReceiver.objects.filter(document=doc).delete()
            except:
                pass
            for t in teacher_list:
                receiver = DocumentReceiver()
                receiver.user = t.user
                receiver.document = doc
                if not doc.is_submit and doc.status == 0:
                    receiver.is_send = True
                    receiver.send_time = datetime.datetime.now()
                    doc.is_approvaled = True
                    doc.save()
                receiver.save()
                       
            #送审
            approvaler_pks = request.POST.getlist("approver")
            if doc.is_submit and approvaler_pks:
                teacher_list = Teacher.objects.filter(pk__in=approvaler_pks)
                appr = DocumentApproval()
                appr.sender = doc.sender
                appr.document = doc
                appr.remark = doc.remark
                appr.approvaler = teacher_list[0].user
                appr.send_time = doc.send_time
                appr.save()
                
                doc.remark = ''
                doc.save()
                
            #附件
            for f in request.FILES.getlist('files'):
                atta = Attachment()
                atta.name = f.name.split('.')[0]
                atta.file = f
                atta.save()
                doc.files.add(atta)
        return redirect(reverse('oa_personal_document'))
    else:
        form = DocumentForm(instance=doc)
    
    schools = get_school_with_workgroup(request.user)
    ctx.update({'form':form,'teachers':teachers,'doc':doc,'category_group':category_group,\
                'receivers':receivers,'schools':schools,'files':files})
    return render(request, template_name, ctx)

@Has_permission('manage_document')
def edit_reback_document(request,doca_id,template_name="oa/document_reback_form.html"):
    """编辑发回给我的公文"""
    doca = get_object_or_404(DocumentApproval,id=doca_id)
    doc = doca.document
    if request.user != doc.sender:
        return redirect(reverse('oa_approval_document',kwargs={'doca_id':doca.id}) + "?ty=reback")
    
    files = doc.files.all()
    receivers = DocumentReceiver.objects.filter(document=doc)
    user_pks = [u.user_id for u in receivers]
    history = DocumentApproval.objects.filter(document=doc).exclude(id=doca_id)
    school = doc.school
    category_group = get_category_group(school)
    teachers = Teacher.objects.filter(school=school)
    form = DocumentForm(instance=doc)
    schools = get_school_with_workgroup(request.user)
    ctx = {'doca':doca,'history':history,'doc':doc,'form':form,'files':files,'receivers':receivers,\
           'teachers':teachers,'user_pks':user_pks,'category_group':category_group,'schools':schools}
    return render(request, template_name, ctx)

@Has_permission('manage_document')
def invalid_user_document(request,doc_id):
    """作废公文"""
    Document.objects.filter(id=doc_id).update(status=2)
    DocumentApproval.objects.filter(document_id=doc_id).update(is_delete=True)
    DocumentReceiver.objects.filter(document_id=doc_id).update(is_delete=True,is_send=False)
    return redirect(reverse('oa_reback_document'))
    
@Has_permission('manage_document')
def resave_document(request,doc_id):
    """另存公文"""
    Document.objects.filter(id=doc_id).update(status=2)
    DocumentApproval.objects.filter(document_id=doc_id).update(is_delete=True)
    DocumentReceiver.objects.filter(document_id=doc_id).update(is_delete=True,is_send=False)
    doc = get_object_or_404(Document,id=doc_id)
    doc.id = None
    doc.status = 1
    doc.save()
    return redirect(reverse('oa_reback_document'))
   
@Has_permission('manage_document') 
def set_receiver(request, template_name="oa/document_receiver.html"):
    """ 设置接收对象"""
#    schools = get_schools(request.user)
    schools = get_school_with_workgroup(request.user)
    school_id = request.POST.get("sid",0)
    
    data = request.POST.get('data','')
    user_pks = [int(u) for u in data.split(",") if u]
    
    doc_id = int(request.POST.get('doc_id',0))
    ty = request.POST.get('ty','')
    member_pks = []
    if doc_id and doc_id !=0:
        if ty == 'supply':
            doc = get_object_or_404(Material, pk=doc_id)
        else:
            doc = get_object_or_404(Document, pk=doc_id)
        member_pks = [r.user.id for r in doc.receivers.all()]
    
    user_pks = user_pks + member_pks
    
    member_list = [u for u in User.objects.filter(pk__in=user_pks)]
    
    try:
        school = get_object_or_404(School,pk=school_id)
    except:
        school = schools[0]
    teacher_all = Teacher.objects.filter(school=school)
    group_list = Group.objects.filter(school=school)
    teacher_group_list = []
    
    group_grades = GroupGrade.objects.all()
    for grade in group_grades:
        t_list = []
        grade_groups = group_list.filter(grade=grade)
        for g in grade_groups:
            #老师按照班级分组
            teachers = [s.user for s in Teacher.objects.filter(group=g)]
            if teachers:
                t_list.append({'id':g.id,'name':g.name,'members':teachers})
        if t_list:
            teacher_group_list.append({'id':grade.id,'name':grade.name,'groups':t_list})
    
    #老师按照职位分组
    teacher_position_list = []
    positions = Position.objects.filter(school=school)
    for p in positions:
        members = []
        for po in PostJob.objects.filter(position=p):
            try:
                members.append(po.teacher.user)
            except:
                pass
#         members = [po.teacher.user for po in PostJob.objects.filter(position=p)]
        if members:
            teacher_position_list.append({'id':p.id,'name':p.name,'members':members})
    #老师按照部门分组
    teacher_depatrment_list = []
    departments = Department.objects.filter(school=school)
    for d in departments:
        members = []
        for dp in PostJob.objects.filter(department=d):
            try:
                members.append(dp.teacher.user)
            except:
                pass
#         members = [p.teacher.user for p in PostJob.objects.filter(department=d)]
        if members:
            teacher_depatrment_list.append({'id':d.id,'name':d.name,'members':members})
    #老师按照首字母分组
    teacher_word_list = []
    words = [chr(i) for i in range(65,91)]
    for w in words:
        members = [t.user for t in teacher_all.filter(pinyin__istartswith=w)]
        if members:
            teacher_word_list.append({'id':w,'name':w,'members':members})
    #老师按照个人虚拟组分组 
    personal_workgoup_list = []     
    personal_workgroups = WorkGroup.objects.filter(type=1,user=request.user)
    for pw in personal_workgroups:
        members = [m for m in pw.members.all()]
        if members:
            personal_workgoup_list.append({'id':pw.id,'name':pw.name,'members':members})
    #老师按照全局虚拟组分组       
    global_workgroup_list = []
    try:
        if schools[0].parent_id == 0:
            global_workgroups = WorkGroup.objects.filter(school=schools[0],type=0)
        else:
            global_workgroups = WorkGroup.objects.filter(school_id=schools[0].parent_id,type=0)
    except:
        global_workgroups = []
    for gw in global_workgroups:
        members = [m for m in gw.members.all()]
        if members:
            global_workgroup_list.append({'id':gw.id,'name':gw.name,'members':members})
    print user_pks,'uuuuuuuuuuuuuuuuuuuuuuu'
    data = render(request, template_name,\
                  {'teacher_all':teacher_all,\
                   'teacher_group_list':teacher_group_list,\
                   'teacher_position_list':teacher_position_list,\
                   'teacher_depatrment_list':teacher_depatrment_list,\
                   'teacher_word_list':teacher_word_list,\
                   'personal_workgoup_list':personal_workgoup_list,\
                   'global_workgroup_list':global_workgroup_list,\
                   'school':school,'schools':schools,\
                   'member_list':member_list,'user_pks':user_pks})
    con=data.content
    return ajax_ok('成功',con)

@Has_permission('manage_document')
def get_approvalers(request, template_name="oa/document_approvalers.html"):
    """ 设置审批人 """
    schools = get_schools(request.user)
    school_id = int(request.POST.get("sid",0))
    try:
        school = get_object_or_404(School,pk=school_id)
    except:
        school = schools[0]
    teacher_all = Teacher.objects.filter(school=school)
   
    #老师按照职位分组
    teacher_position_list = []
    positions = Position.objects.filter(school=school)
    for p in positions:
        members = []
        for po in PostJob.objects.filter(position=p):
            try:
                members.append(po.teacher.user)
            except:
                pass
#         members = [po.teacher.user for po in PostJob.objects.filter(position=p)]
        if members:
            teacher_position_list.append({'id':p.id,'name':p.name,'members':members})
    
    #老师按照首字母分组
    teacher_word_list = []
    words = [chr(i) for i in range(65,91)]
    for w in words:
        members = [t.user for t in teacher_all.filter(pinyin__istartswith=w)]
        if members:
            teacher_word_list.append({'id':w,'name':w,'members':members})
            
    global_workgroup_list = []
    try:
        if schools[0].parent_id == 0:
            global_workgroups = WorkGroup.objects.filter(school=schools[0],type=0)
        else:
            global_workgroups = WorkGroup.objects.filter(school_id=schools[0].parent_id,type=0)
    except:
        global_workgroups = []
    for gw in global_workgroups:
        members = [m for m in gw.members.all()]
        if members:
            global_workgroup_list.append({'id':gw.id,'name':gw.name,'members':members})
  
    data = render(request, template_name,\
                  {'teacher_all':teacher_all,\
                   'teacher_position_list':teacher_position_list,\
                   'teacher_word_list':teacher_word_list,\
                   'global_workgroup_list':global_workgroup_list,\
                   'school':school,'schools':schools})
    con=data.content
    return ajax_ok('成功',con)

