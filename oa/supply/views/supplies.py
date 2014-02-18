# -*- coding: utf-8 -*-
from django.shortcuts import redirect, render, get_object_or_404
from kinger.models import School,Teacher,SupplyCategory,Provider,Supply,MaterialReceiver,MaterialApproval,\
    Attachment,MaterialApply,SupplyRecord,Material,SupplyReback
from django.contrib.auth.models import User
from django.core.context_processors import csrf
from django.contrib import messages
from django.db.models import Q
from django.utils.translation import ugettext as _
from django.http import HttpResponse
from django.views.decorators.http import require_POST, require_GET
import datetime
from kinger.helpers import ajax_error,ajax_ok
from django.core.exceptions import ObjectDoesNotExist, MultipleObjectsReturned
from userena import signals as userena_signals
from django.core.urlresolvers import reverse
from django.forms.formsets import formset_factory
from oa.decorators import Has_permission
from django.contrib import auth
from django.contrib.auth.views import logout
from oa.helpers import get_schools,is_agency_user,user_manage_school,school_provider,supply_category_group,\
        get_school_with_workgroup,mark_supply_doc_as_read,get_school_realtes
from oa.supply.forms import SupplyCategoryForm,ProviderForm,MaterialForm,SupplyForm
from oa.decorators import Has_permission
try:
    import simplejson as json
except ImportError:
    import json
    

@Has_permission('manage_supply_caregory')
def supply_category(request, template_name="supply/category_form.html"):
    """物资类别设置"""
    schools = get_schools(request.user)
    school_id = int(request.GET.get("sid")) if request.GET.get("sid") else 0
    school = user_manage_school(request.user,school_id)
    extra = int(request.GET.get("extra", 0))
    categorys = []
    category_list = []
    for p in SupplyCategory.objects.filter(school=school,parent_id=0):
        categorys.append(p)
        category_list.append({'name':p.name,'parent':None})
        for s in SupplyCategory.objects.filter(school=school,parent=p):
            categorys.append(s)
            category_list.append({'name':s.name,'parent':s.parent})
    
    if request.method == 'POST':
        extra = request.POST['form-TOTAL_FORMS']
        formset = formset_factory(SupplyCategoryForm, extra=extra)
        form = formset(request.POST,initial=category_list)
        
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
            redirect_url = reverse('oa_supply_category') + "?sid=" + str(school_id)
            return redirect(redirect_url)
    else:
        formset = formset_factory(SupplyCategoryForm,extra=extra)
        form = formset(initial=category_list)

    ctx = {'form':form,'extra':extra,'categorys':categorys,'schools':schools,'school':school}
    return render(request, template_name,ctx)

def get_extra_form(request,template_name="oa/extra_form.html"):
    """公文类别附加表单"""
    order = int(request.POST.get('order'))
    formset = formset_factory(SupplyCategoryForm, extra=order + 1)
    form = formset()
    pid = request.POST.get('parent_id',0)
    parent = None
    if pid:
        parent_list = []
        parent = get_object_or_404(SupplyCategory,id=pid)
        for i in range(order):
            parent_list.append({'name':'','parent':parent})
        form = formset(initial=parent_list)
    
    form = form[order]
    ctx = {'form':form,'order':order,'parent':parent}
    
    data = render(request,template_name,ctx)
    con=data.content
    return ajax_ok('成功',con)

@Has_permission('manage_supply_caregory')
def delete_category(request,cat_id):
    """删除公文类别"""
    sid = request.GET.get('sid','')
    schools = get_schools(request.user)
    category = get_object_or_404(SupplyCategory,id=cat_id,school__in=schools)
    if category.parent_id == 0:
        sub_categories = SupplyCategory.objects.filter(parent=category)
        sub_categories.delete()
    category.delete()
    messages.success(request, u'删除成功')
    return redirect(reverse('oa_supply_category') + "?sid=" + sid) 

@Has_permission('manage_supply_list')
def supply_index(request, template_name="supply/supply_index.html"):
    """物资列表页"""
    schools = get_schools(request.user)
    school_id = request.GET.get("sid",'')
    
#    categorys = SupplyCategory.objects.filter(school=schools[0])
    if school_id:
        school = get_object_or_404(School, pk=school_id)
        supplies = Supply.objects.filter(school=school,parent_id=0)
    else:
        school = None
        supplies = Supply.objects.filter(school__in=schools,parent_id=0)
        
    is_show = int(request.GET.get("is_show",1))
    if is_show != -1:
        supplies = supplies.filter(is_show=is_show)
    cat_id = request.GET.get("cat",'')
    if cat_id:
        category = get_object_or_404(SupplyCategory, pk=cat_id)
        supplies = supplies.filter(category=category)
    else:
        category = None
    query = request.GET.get("q",'')
    if query:
        supplies = supplies.filter(name__contains=query)
    sup_id = request.GET.get("sup",'')
    if sup_id:
        supplies = supplies.filter(id=sup_id)
    
    #启用禁用物资
    if request.method == 'POST':
        try:
            status = int(request.POST.get("attr"))
            supply_pks = request.POST.getlist("supply_pks")
            supplies = supplies.filter(id__in=supply_pks)
            for sup in supplies:
                sup.is_show = status
                sup.save()
            messages.success(request, u"操作成功")
        except:
            messages.success(request, u"操作失败")
        redirect_url = reverse('oa_supply_index') + "?sid=" + school_id + "&cat=" + cat_id + "&is_show=" + str(is_show) + "&q=" + query
        return redirect(redirect_url)
    
    ctx = {'schools':schools,'school':school,'query':query,'sup':sup_id,\
           'supplies':supplies,'category':category,'is_show':is_show}
    return render(request, template_name, ctx)

@Has_permission('manage_supply_list')
def update_supply(request, supply_id, template_name="supply/supply_form.html"):
    """更新物资"""
    schools = get_schools(request.user)
    supply = get_object_or_404(Supply,pk=supply_id,school__in=schools)
    school = supply.school

    if request.method == 'POST':
        form = SupplyForm(request.POST, instance=supply)
        
        if form.is_valid():
            supply = form.save(commit=False)
            supply.save()
            subclass = Supply.objects.filter(parent=supply)
            subclass.update(name=supply.name,category=supply.category)
            messages.success(request, u"已成功更新物资： %s " % supply.name)
            redirect_url = reverse('oa_supply_index') + "?sid=" + str(supply.school.id)
            return redirect(redirect_url)
    else:
        form = SupplyForm(instance=supply)
    ctx = {"form": form, "supply": supply,"school":school,"schools":schools,'sid':school.id}
    return render(request, template_name, ctx)

@Has_permission('manage_supply_provider')
def provider_index(request, template_name="supply/provider_index.html"):
    """供应商列表"""
    schools = get_schools(request.user)
    school_id = int(request.GET.get("sid",0))
    if school_id == 0:
        school = None if is_agency_user(request.user) else schools[0]
    else:
        school = School.objects.get(id=school_id)
        school = school if school in schools else None
        
    query = request.GET.get("n", "")
    qs = Q(school=school) if school else Q(school__in=schools)
    qn = Q(name__contains=query) if query else Q()
    q = qs & qn
    
    providers = Provider.objects.filter(q)
    
    #删除供应商
    if request.method == 'POST':
        try:
            provider_pks = request.POST.getlist("provider_pks")
            providers = providers.filter(id__in=provider_pks)
            for p in providers:
                p.delete()
            messages.success(request, u"操作成功")
        except:
            messages.success(request, u"操作失败")
        redirect_url = reverse('oa_provider_index') + "?sid=" + str(school_id) + "&n=" + query
        return redirect(redirect_url)

    ctx = {'schools':schools,'school':school,'providers':providers,'sid':school_id,'query':query}
    return render(request, template_name, ctx)

@Has_permission('manage_supply_provider')
def create_provider(request,template_name="supply/provider_form.html"):
    """创建供应商"""
    ctx = {}
    school_id = request.GET.get("sid",0)

    if request.method == 'POST':
        school_id = int(request.POST.get("school",0))
        form = ProviderForm(request.POST)

        if form.is_valid():
            provider = form.save(commit=False)
            provider.creator = request.user
            provider.save()
            ctx.update({"school":provider.school})
            if provider.id:
                messages.success(request, u'已成功创建供应商%s ' % provider.name)
                redirect_url = reverse('oa_provider_index') + "?sid=" + str(provider.school.id)
                return redirect(redirect_url)
    else:
        form = ProviderForm()
    try:
        school = School.objects.get(id=school_id)
    except:
        school = None
    
    schools = get_schools(request.user)
    ctx.update({"school":school,"schools":schools})
    ctx.update({'form':form})
    return render(request, template_name, ctx)

@Has_permission('manage_supply_provider')
def update_provider(request, provider_id, template_name="supply/provider_form.html"):
    """更新供应商"""
    schools = get_schools(request.user)
    provider = get_object_or_404(Provider,pk=provider_id,school__in=schools)
    school = provider.school

    if request.method == 'POST':
        form = ProviderForm(request.POST, instance=provider)
        
        if form.is_valid():
            provider = form.save(commit=False)
            provider.save()
            messages.success(request, u"已成功更新供应商： %s " % provider.name)
            redirect_url = reverse('oa_provider_index') + "?sid=" + str(provider.school.id)
            return redirect(redirect_url)
    else:
        form = ProviderForm(instance=provider)
    ctx = {"form": form, "provider": provider,"school":school,"schools":schools,'sid':school.id}
    return render(request, template_name, ctx)


def get_school_provider(request):
    sid = request.GET.get("sid", "")
    return school_provider(sid)

@Has_permission('manage_supply_record')
def record_list(request,template_name="supply/record_list.html"):
    schools = get_schools(request.user)
    sid = int(request.GET.get("sid")) if request.GET.get("sid") else 0
    if sid:
        school = School.objects.get(id=sid)
    else:
        school = schools[0]
    records = SupplyRecord.objects.filter(parent_id=0,school__in=schools)
    query = request.GET.get("q", '')
    st = request.GET.get("st", '')
    et = request.GET.get("et", '')
    status = int(request.GET.get("status", 0))
    page = request.GET.get("page", '')
    tar = request.GET.get("tar", '')
    
    qc = Q(school_id=sid) if sid else Q()
    qs = (Q(stime__startswith=st) | Q(stime__gte=st)) if st else Q()
    qe = (Q(stime__startswith=et) | Q(stime__lte=et)) if et else Q()
    q = qs & qe & qc
    records = records.filter(q)
    qty = ''
    if query: 
        qty = request.GET.get("qty",'')
        if qty:
            sub_records = SupplyRecord.objects.filter(parent_id__gt=0,school__in=schools,supply__name=query)
        else:
            sub_records = SupplyRecord.objects.filter(parent_id__gt=0,school__in=schools,supply__name__contains=query)
        par_record_pks = [s.parent_id for s in sub_records if s.parent_id > 0]
        records = records.filter(id__in=list(set(par_record_pks)))
    
    query_ctx = {"name":query,"ty":qty}
    record_lists = []
    for r in records:
        sr = r.subrecords.filter(status=status)
        if sr.count():
            record_lists.append(r)
            
    ctx = {'records':record_lists,'school':school,'schools':schools,'sid':sid,\
           "query":query,"st":st,"et":et,"status":status,"page":page,"tar":tar,'query_ctx':query_ctx}
    return render(request, template_name,ctx)

def supply_entry(request):
    query = request.GET.get("q", '')
    st = request.GET.get("st", '')
    et = request.GET.get("et", '')
    page = request.GET.get("page", '')
    if request.method == 'POST':
        desc = request.POST.get("applies")
        remark = request.POST.get("remark","")
        doc_id = request.POST.get("doc")
        sid = request.POST.get("sid",'')
        sid = sid if sid else request.user.teacher.school.id
        doc = get_object_or_404(Material,id=doc_id)
#        desc = '{"1":{"pname":"nanshanlining","sname":"","num":"100","app_id":"59","regist":"zhangsan"}}'
        record = json.loads(desc)
        record_p,cr = SupplyRecord.objects.get_or_create(parent_id=0,creator=request.user,school_id=sid,type=doc.type,document=doc)
        #物资录入
        if doc.type == 0:
            for i in record:
                if int(record[i]['num']) > 0:
                    apply = get_object_or_404(MaterialApply,id=record[i]['app_id'],document=doc)
                    supply_p = apply.supply
                    if not supply_p.is_show:
                        supply_p.is_show = True
                        supply_p.save()
                    if record[i]['pname']:
                        provider,created = Provider.objects.get_or_create(name=record[i]['pname'],school_id=sid)
                        if created:
                            provider.creator = request.user
                            provider.save()
                            supply_p.provider = provider
                            supply_p.save()
                    else:
                        provider = None
                    supply_p = apply.supply
                    record_s = SupplyRecord(parent=record_p,creator=request.user,school_id=sid,document=doc,provider=provider,\
                            supply=supply_p,type=doc.type,num=int(record[i]['num']),remark=remark,regist=record[i]['regist'])    
                    record_s.save()
                    
                    supply_p.num = supply_p.num + int(record[i]['num'])
                    apply.deal = apply.deal + int(record[i]['num'])
                    apply.regist = record[i]['regist']
                    apply.save()
                    if record[i]['sname']:
                        supply_p.name = record[i]['sname']
                    supply_p.save()
            messages.success(request, u"录入成功") 
        else:
            #物资领取
            for i in record:
                apply = get_object_or_404(MaterialApply,id=record[i]['app_id'],document=doc)
                supply_p = apply.supply
                if not supply_p.is_show:
                    supply_p.is_show = True
                    supply_p.save()
                    
                record_s = SupplyRecord(parent=record_p,creator=request.user,school_id=sid,document=doc,\
                        supply=supply_p,type=doc.type,num=int(record[i]['num']),remark=remark,regist=record[i]['regist'])    
                record_s.save()
                
                if supply_p.num > int(record[i]['num']):
                    supply_p.num = supply_p.num - int(record[i]['num'])
                    apply.deal = apply.deal + int(record[i]['num'])
                    apply.regist = record[i]['regist']
                    apply.save()
                    supply_p.save()
            messages.success(request, u"领取成功") 
                    

    channel = request.POST.get("channel")
    if channel == 'send':
        redirect_url = reverse('oa_supply_issued_document') + "?tar=" + str(doc.id) + \
        "&q=" + query + "&st=" + st + "&et=" +et + "&page=" + page
    else:
        redirect_url = reverse('oa_supply_having_approvaled') + "?tar=" + str(doc.id) + \
        "&q=" + query + "&st=" + st + "&et=" +et + "&page=" + page
    return redirect(redirect_url)

@Has_permission('manage_supply_record')
def record_detail(request,record_id,template_name="supply/record_detail.html"):
    """物资录入详情"""
    record = get_object_or_404(SupplyRecord,id=record_id)
    doc = record.document
    records = SupplyRecord.objects.filter(parent=record,status=0)
    backs = SupplyReback.objects.filter(record__in=records)
    ctx = {'record':record,'records':records,'backs':backs,'doc':doc}
    return render(request, template_name, ctx)

@Has_permission('manage_supply_record')
def delete_record(request, record_id):
    """delete a record"""
    ty = request.GET.get('ty','')
    schools = get_schools(request.user)
    data = {'status':0}
    if ty == "bach":
        records = SupplyRecord.objects.filter(school__in=schools,parent_id=record_id)
        ids = request.GET.get('ids','')
        if ids:
            pks = ids.split(',')
            records = records.filter(id__in=pks)
        for record in records:
            r = edit_apply(record)
            if r:
                record.status = 1
                record.save()
                data = {'status':1}
    else:
        record = get_object_or_404(SupplyRecord,id=record_id,school__in=schools,parent_id__gt=0)
        r = edit_apply(record)
        if r:
            record.status = 1
            record.save()
            data = {'status':1}
    return HttpResponse(json.dumps(data))

def edit_apply(record):
    try:
        doc = record.document
        num = record.num
        supply = record.supply
        if supply.num < num:
            return False
        apl = get_object_or_404(MaterialApply,supply=supply,document=doc)
        apl.deal = apl.deal - num
        apl.save()
        supply.num = supply.num - num
        supply.save()
        return True
    except:
        return False

def reback_record(request, record_id,template_name="supply/supply_reback.html"):
    ty = request.GET.get('ty','')
    schools = get_schools(request.user)
    if ty == "bach":
        records = SupplyRecord.objects.filter(school__in=schools,parent_id=record_id)
        ids = request.GET.get('ids','')
        if ids:
            pks = ids.split(',')
            records = records.filter(id__in=pks)
    else:
        records = SupplyRecord.objects.filter(id=record_id,school__in=schools,parent_id__gt=0)
    ctx = {"records":records}
    data = render(request,template_name,ctx)
    con=data.content
    return ajax_ok('成功',con)

def reback_supply(request, record_id):
#    try:
    rn = int(request.GET.get('n'))
    schools = get_schools(request.user)
    record = get_object_or_404(SupplyRecord,id=record_id,school__in=schools,parent_id__gt=0)
    reback_old = record.back
    reback_new = reback_old + rn
    if reback_new > record.num:
        data = {'status':''}
    else:
        record.back = reback_new
        record.save()
        data = {'status':1}
#    except:
#        data = {'status':''}
    return HttpResponse(json.dumps(data))

def supply_back(request):
    """"""
    sid = int(request.GET.get("sid",0))
    query = request.GET.get("q", '')
    st = request.GET.get("st", '')
    et = request.GET.get("et", '')
    status = int(request.GET.get("status", 0))
    page = request.GET.get("page", '')

    if request.method == 'POST':
        desc = request.POST.get("desc")
        remark = request.POST.get("remark","")
        record = json.loads(desc)
        par = 0
        msg = u"操作失败"
        for i in record:
            rec = get_object_or_404(SupplyRecord,id=record[i]['app_id'])
            supply_p = rec.supply
            n = rec.back + int(record[i]['num'])
            if n <= rec.num:
                rec.back = rec.back + int(record[i]['num'])
                rec.save()
                r = SupplyReback(regist=record[i]['regist'],remark=remark,record=rec,num=int(record[i]['num']))
                r.save()
                supply_p.num = supply_p.num + int(record[i]['num'])
                supply_p.save()
                if par != rec.parent_id:
                    par = rec.parent_id
                msg = u"退还成功"
        messages.success(request, msg) 
    redirect_url = reverse('oa_supply_record_index') + "?tar=" + str(par) + \
        "&sid=" + str(sid) + "&q=" + query + "&st=" + st + "&et=" +et + "&status=" + str(status) + "&page=" + page
    return redirect(redirect_url)

def school_realtes(request):
    """"""
    return get_school_realtes(request)
