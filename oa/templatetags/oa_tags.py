# -*- coding: utf-8 -*-
from django.db.models import get_model
from django.template import Library, Node, TemplateSyntaxError, Variable, resolve_variable,defaultfilters
from django.utils.translation import pgettext, ungettext, ugettext as _
from django.core.urlresolvers import resolve, reverse, get_script_prefix
from django.core.exceptions import ObjectDoesNotExist
from django import template
from kinger import settings
from django.contrib.auth.models import User
from kinger.models import GroupTeacher,DocumentCategory,Attachment,Document,Teacher,Agency,\
        DocumentReceiver,DocumentApproval,Album,Photo,WebSite,Access,Role,WebSiteAccess,MaterialApproval,Material,\
        MaterialReceiver,SupplyRecord,SupplyReback,Disk,SupplyCategory,Supply
import re
from oa.helpers import is_student,is_teacher,get_schools,user_access_list,get_user_name
from django.shortcuts import get_object_or_404
from django.core.urlresolvers import reverse
import sys
import re
from datetime import datetime
from itertools import groupby, cycle as itertools_cycle

from django.template.base import (Node, NodeList, Template, Library,
    TemplateSyntaxError, VariableDoesNotExist, InvalidTemplateLibrary,
    BLOCK_TAG_START, BLOCK_TAG_END, VARIABLE_TAG_START, VARIABLE_TAG_END,
    SINGLE_BRACE_START, SINGLE_BRACE_END, COMMENT_TAG_START, COMMENT_TAG_END,
    VARIABLE_ATTRIBUTE_SEPARATOR, get_library, token_kwargs, kwarg_re)
from django.template.smartif import IfParser, Literal
from django.template.defaultfilters import date
from django.utils.encoding import smart_str, smart_unicode
from django.utils.safestring import mark_safe
from django.utils import timezone

from oa import helpers
register = Library()


def silence_without_field(fn):
    def wrapped(field, attr):
        if not field:
            return ""
        return fn(field, attr)
    return wrapped


def _process_field_attributes(field, attr, process):

    # split attribute name and value from 'attr:value' string
    params = attr.split(':', 1)
    attribute = params[0]
    value = params[1] if len(params) == 2 else ''

    # decorate field.as_widget method with updated attributes
    old_as_widget = field.as_widget

    def as_widget(self, widget=None, attrs=None, only_initial=False):
        attrs = attrs or {}
        process(widget or self.field.widget, attrs, attribute, value)
        return old_as_widget(widget, attrs, only_initial)

    bound_method = type(old_as_widget)
    try:
        field.as_widget = bound_method(as_widget, field, field.__class__)
    except TypeError:  # python 3
        field.as_widget = bound_method(as_widget, field)
    return field


@register.filter("attr")
@silence_without_field
def set_attr(field, attr):

    def process(widget, attrs, attribute, value):
        attrs[attribute] = value

    return _process_field_attributes(field, attr, process)


@register.filter("add_error_attr")
@silence_without_field
def add_error_attr(field, attr):
    if hasattr(field, 'errors') and field.errors:
        return set_attr(field, attr)
    return field


@register.filter("append_attr")
@silence_without_field
def append_attr(field, attr):
    def process(widget, attrs, attribute, value):
        if attrs.get(attribute):
            attrs[attribute] += ' ' + value
        elif widget.attrs.get(attribute):
            attrs[attribute] = widget.attrs[attribute] + ' ' + value
        else:
            attrs[attribute] = value
    return _process_field_attributes(field, attr, process)


@register.filter("add_class")
@silence_without_field
def add_class(field, css_class):
    return append_attr(field, 'class:' + css_class)


@register.filter("add_error_class")
@silence_without_field
def add_error_class(field, css_class):
    if hasattr(field, 'errors') and field.errors:
        return add_class(field, css_class)
    return field


@register.filter("set_data")
@silence_without_field
def set_data(field, data):
    return set_attr(field, 'data-' + data)


@register.filter(name='field_type')
def field_type(field):
    """
    Template filter that returns field class name (in lower case).
    E.g. if field is CharField then {{ field|field_type }} will
    return 'charfield'.
    """
    if hasattr(field, 'field') and field.field:
        return field.field.__class__.__name__.lower()
    return ''


@register.filter(name='widget_type')
def widget_type(field):
    """
    Template filter that returns field widget class name (in lower case).
    E.g. if field's widget is TextInput then {{ field|widget_type }} will
    return 'textinput'.
    """
    if hasattr(field, 'field') and hasattr(field.field, 'widget') and field.field.widget:
        return field.field.widget.__class__.__name__.lower()
    return ''


# ======================== render_field tag ==============================

ATTRIBUTE_RE = re.compile(r"""
    (?P<attr>
        [\w_-]+
    )
    (?P<sign>
        \+?=
    )
    (?P<value>
    ['"]? # start quote
        [^"']*
    ['"]? # end quote
    )
""", re.VERBOSE | re.UNICODE)

@register.tag
def render_field(parser, token):
    """
    Render a form field using given attribute-value pairs

    Takes form field as first argument and list of attribute-value pairs for
    all other arguments.  Attribute-value pairs should be in the form of
    attribute=value or attribute="a value" for assignment and attribute+=value
    or attribute+="value" for appending.
    """
    error_msg = '%r tag requires a form field followed by a list of attributes and values in the form attr="value"' % token.split_contents()[0]
    try:
        bits = token.split_contents()
        tag_name = bits[0]
        form_field = bits[1]
        attr_list = bits[2:]
    except ValueError:
        raise TemplateSyntaxError(error_msg)

    form_field = parser.compile_filter(form_field)

    set_attrs = []
    append_attrs = []
    for pair in attr_list:
        match = ATTRIBUTE_RE.match(pair)
        if not match:
            raise TemplateSyntaxError(error_msg + ": %s" % pair)
        dct = match.groupdict()
        attr, sign, value = dct['attr'], dct['sign'], parser.compile_filter(dct['value'])
        if sign == "=":
            set_attrs.append((attr, value))
        else:
            append_attrs.append((attr, value))

    return FieldAttributeNode(form_field, set_attrs, append_attrs)


class FieldAttributeNode(Node):
    def __init__(self, field, set_attrs, append_attrs):
        self.field = field
        self.set_attrs = set_attrs
        self.append_attrs = append_attrs

    def render(self, context):
        bounded_field = self.field.resolve(context)
        field = getattr(bounded_field, 'field', None)
        if (getattr(bounded_field, 'errors', None) and
            'WIDGET_ERROR_CLASS' in context):
            bounded_field = append_attr(bounded_field, 'class:%s' %
                                        context['WIDGET_ERROR_CLASS'])
        if field and field.required and 'WIDGET_REQUIRED_CLASS' in context:
            bounded_field = append_attr(bounded_field, 'class:%s' %
                                        context['WIDGET_REQUIRED_CLASS'])
        for k, v in self.set_attrs:
            bounded_field = set_attr(bounded_field, '%s:%s' % (k,v.resolve(context)))
        for k, v in self.append_attrs:
            bounded_field = append_attr(bounded_field, '%s:%s' % (k,v.resolve(context)))
        return bounded_field


@register.filter
def is_class_teacher(obj, group):
    """"""
    return GroupTeacher.objects.filter(teacher=obj,group=group,type_id=1).exists()

@register.filter
def is_school_admin(teacher):
    """"""
    try:
        admins = [u for u in teacher.school.admins.all()]
        return teacher.user in admins
    except:
        return False

@register.filter
def get_logo_url(site):
    """"""
    try:
        return site.logo.url
    except:
        return ''

@register.filter
def get_full_domain(obj,string):
    """"""
    if obj.type == 1:
        try:
            if obj.domain[0:7] == "http://":
                return str(obj.domain)
            else:
                return "http://" + str(obj.domain)
        except:
            return "javascript:;"
    else:
        return "http://" + str(obj.domain) + "." + string

@register.filter 
def domain_without_http(val):
    try:
        return val.replace('http://','')
    except:
        return val

@register.filter
def get_site_url(domain):
    """"""
    domain_parts = domain.split('.')
    if len(domain_parts) == 1:
        return 'http://localhost:8000/oa/site'
    return domain
    
@register.filter
def get_regist_status(status):
    """"""
    ty = ['待录取','未获录取','已录取','过期','待面试']
    try:
        return ty[status]
    except:
        return ''

@register.filter
def apply_undeal(app,ty=''):
    """"""
    if ty == "out":
        n = app.num - app.deal
        sn = app.supply.num
        return min(n,sn)
    else:
        return app.num - app.deal

@register.filter
def doc_apply_undeal(doc):
    """"""
    apps = doc.applies.all()
    i = 0
    for a in apps:
        if a.num - a.deal > 0:
            i += 1       
    return i

@register.filter
def in_effect(record,status):
    """"""
    records = record.subrecords.all()
    for r in records:
        if r.status == status:
        
            return True
    return False

@register.filter
def effect_records(records,status):
    return records.filter(status=status)

@register.filter
def single_supply(records,ctx):
    try:
        q = ctx['name']
        ty = ctx['ty']
        if q and ty:
            records = records.filter(supply__name=q)
    except:
        pass
    return records

@register.filter
def record_sub_pks(records):
    pks = ''
    for r in records:
        pks = pks + ',' if pks else pks
        pks += str(r.id)
    return pks

@register.filter
def belong_supply(cat_id):
    cat_list = []
    category = get_object_or_404(SupplyCategory,id=cat_id)
    cat_list.append(category)
    if category.parent_id == 0:
        sub_list = [s for s in SupplyCategory.objects.filter(parent=category)]
        cat_list = cat_list + sub_list
    supplies = Supply.objects.filter(category__in=cat_list)
    if supplies.count() > 0:
        return False
    else:
        return True

@register.filter
def share_category_pk(disk):
    try:
        disks = Disk.objects.filter(parent=disk)
        return disks[0].category_id
    except:
        return ''

@register.filter
def reback_left(record):
    return record.num - record.back
    
@register.filter
def article_type(status):
    """"""
    ty = ['草稿','发布']
    try:
        return ty[status]
    except:
        return ''

@register.filter
def is_guide_teacher(obj, group):
    """"""
    return GroupTeacher.objects.filter(teacher=obj,group=group,type_id=2).exists()

@register.filter
def in_list_q(value, list_q):
    """
    查看某个标签的 id 是否在标签请求参数中.
    """
    return value in list_q

@register.filter
def get_user_by_pk(value):
    """
    """
    if not value:
        return None
    try:
        user = User.objects.get(pk=int(value))
        return user
    except:
        return None
    
@register.filter
def teacher_check(value):
    """"""
    try:
        user = User.objects.get(username=value)
        teacher = user.teacher
    except:
        teacher = None
    if teacher:
        uid = teacher.user.id
    else:
        uid = 0
    return uid

@register.filter
def obj_pk(value, num):

    try:
        return value[num].id
    except:
        return ''

class ActiverNode(template.Node):
    moudle_group = []
    def __init__(self, activer_name):
        department = ['oa_department_list','oa_department_create','oa_department_update','oa_department_delete',]
        position = ['oa_position_list','oa_position_create','oa_position_update','oa_position_delete',]
        school = ['oa_school_list','oa_school_create','oa_school_update','oa_school_delete',]
        group = ['oa_class_list','oa_class_create','oa_class_update','oa_class_delete','oa_class_batch_import',\
                 'oa_class_template','oa_class_import','oa_class_check_import',]
        teacher = ['oa_teacher_list','oa_teacher_create','oa_teacher_update','oa_get_school_agency',\
                       'oa_get_pre_username','oa_teacher_template','oa_teacher_batch_import','oa_teacher_import',\
                       'oa_teacher_check_import',]
        student = ['oa_student_list','oa_student_create','oa_student_update','oa_get_school_class',\
                       'oa_student_template','oa_student_batch_import','oa_student_import','oa_student_check_import',]
        student_account = ['oa_student_send_account','oa_student_send_group_account',]
        teacher_account = ['oa_teacher_send_account',]
        document_category = ['oa_document_category',]
        document = ['oa_write_document','oa_my_document','oa_approval_document','oa_need_approval',\
                    'oa_approvaled_document','oa_issued_document','oa_reback_document','oa_invalid_document',\
                    'oa_document_detail','oa_personal_document','oa_edit_reback_document','oa_update_document',]
        
        regist_apply = ['oa_regist_apply_list','oa_regist_apply_detail',]
        
        schedule = ['oa_schedule_teacher','oa_create_schedule','oa_delete_schedule','oa_download_schedule']
        disks = ['oa_disk_index','oa_disk_category','oa_disk_create','oa_sdisk_detail','oa_sdisk_update',]
        senate = department + position + school + group + teacher + student + student_account + \
                    teacher_account + document_category + document + regist_apply + schedule + disks
        self.moudle_group.append({'urls':senate,'name':'教务管理'})
        
        role_list = ['oa_permission_role_list','oa_permission_create_role','oa_permission_update_role',\
                         'oa_permission_delete_role','oa_permission_role_accesses',]
        role_design = ['oa_permission_designate_role','oa_permission_role_detail','oa_permission_user_role',\
                       'oa_permission_add_role',]
        global_group = ['oa_workgroup_list','oa_workgroup_create','oa_workgroup_update','oa_workgroup_delete',\
                        'oa_workgroup_set',]
        communicate_access = ['oa_communicate',]
        teacher_authorize = ['oa_permission_set_authorize',]
        
        personal_group = ['oa_workgroup_personal','oa_workgroup_personal_create','oa_workgroup_personal_update',\
                          'oa_workgroup_personal_delete',]
        access = role_list + role_design + global_group + communicate_access + personal_group + teacher_authorize
        self.moudle_group.append({'urls':access,'name':'访问控制'})
        
        account_setting = ['oa_account_setting',]
        personal_password = ['oa_account_password_change',]
        
        account = account_setting + personal_password
        self.moudle_group.append({'urls':account,'name':'个人设置'})
        
        message = ['oa_message_list','oa_delete_message','oa_message_history',]
        message_send = ['oa_send_message',]
        message_record = ['oa_message_record','oa_message_record_view','oa_message_cancel_timing',]
        communicate = message + message_send + message_record
        self.moudle_group.append({'urls':communicate,'name':'沟通联系'})
        
        home = ['oa_home',]
        self.moudle_group.append({'urls':home,'name':'首页'})
        
        site_admin_home  = ['oa_website_list','oa_website_create','oa_website_edit',]
        self.moudle_group.append({'urls':site_admin_home,'name':'学园站点管理'})
        
        manage_site = ['oa_website_manage',]
        
        grove = ['oa_part_nav_grove',]
        feature = ['oa_part_nav_feature',]
        recruit = ['oa_part_nav_recruit',]
        teache = ['oa_part_teache','oa_part_nav_teache','oa_part_nav_teache_update',]
        site_nav = grove + feature + recruit + teache
        self.moudle_group.append({'urls':site_nav,'name':'导航栏目管理'})
        
        part_admin = ['oa_part_con_anc_list','oa_part_con_anc_create','oa_part_con_anc_delete',\
                      'oa_part_con_anc_update','oa_part_con_news_list','oa_part_con_news_create',\
                      'oa_part_con_news_delete','oa_part_con_news_update','oa_part_con_tips_create',\
                      'oa_part_con_video_list','oa_part_con_video_create','oa_part_con_video_delete',\
                      'oa_part_con_video_update',]
        school_album = ['oa_album_school_list','oa_album_create','oa_album_detail','oa_album_upload_photo',\
                        'oa_album_delete','oa_album_show_photo','oa_album_photo_detail',]
        article = ['oa_article_list','oa_article_create','oa_article_update']
        link = ['oa_link_list','oa_link_create','oa_link_delete']
        figure = ['oa_star_figure_teacher','oa_star_figure_student','oa_star_figure_detail',]
        part_all = part_admin + school_album + article + link + figure
        self.moudle_group.append({'urls':part_all,'name':'内容板块管理'})
                         
        mailbox = ['oa_mailbox','oa_mailbox_delete','oa_mailbox_detail','oa_mailbox_set',]
        school_mail = mailbox
        self.moudle_group.append({'urls':school_mail,'name':'家园互动'})
        
        website_update = ['oa_website_update',]
        template = ['oa_template_list','oa_change_template',]
        site_admin = ['oa_website_admins',]
        site_setting = website_update + template + site_admin
        self.moudle_group.append({'urls':site_setting,'name':'站点系统设置'})
        
        supply_list = ['oa_supply_index','oa_supply_update',]
        supply_category = ['oa_supply_category',]
        supply_record = ['oa_supply_record_index','oa_supply_record_detail',]
        provider_list = ['oa_provider_index','oa_provider_create','oa_provider_update',]
        supply_document = ['oa_supply_my_document','oa_supply_write_document','oa_supply_issued_document',\
                           'oa_supply_document_detail','oa_supply_document_need_approval','oa_supply_approval_document',\
                           'oa_supply_having_approvaled','oa_supply_reback_document','oa_supply_edit_reback_document',
                           'oa_supply_invalid_user_document','oa_supply_invalid_document','oa_supply_personal_document',
                           'oa_supply_delete_document','oa_supply_update_document',]
        supply_admin_home = supply_list + supply_category + supply_record + provider_list + supply_document
        self.moudle_group.append({'urls':supply_admin_home,'name':'物资管理'})
        
        growth_oa_home = ['growth_oa_index',]
        self.moudle_group.append({'urls':growth_oa_home,'name':'成长书'})
        
        #公文管理选项卡
        doc_my = ['oa_my_document','oa_supply_my_document',]
        doc_send = ['oa_issued_document','oa_supply_issued_document',]
        doc_approval = ['oa_need_approval','oa_supply_document_need_approval',]
        doc_approvaled = ['oa_approvaled_document','oa_supply_having_approvaled',]
        doc_reback = ['oa_reback_document','oa_supply_reback_document',]
        doc_invalid = ['oa_invalid_document','oa_supply_invalid_document',]
        doc_doc = ['oa_personal_document','oa_supply_personal_document',]
        doc_write = ['oa_write_document','oa_supply_write_document',]
        
        self.activer_set = {
            'department':department,'position':position,'school':school,'group':group,'teacher':teacher,\
            'student':student,'senate':senate,'role_list':role_list,'role_design':role_design,\
            'global_group':global_group,'communicate':communicate,'access':access,\
            'account_setting':account_setting,'personal_group':personal_group,'account':account,\
            'student_account':student_account,'teacher_account':teacher_account,'message':message,\
            'communicate':communicate,'home':home,'message_send':message_send,'message_record':message_record,\
            'document_category':document_category,'document':document,'grove':grove,'feature':feature,\
            'recruit':recruit,'teache':teache,'site_nav':site_nav,'site_admin_home':site_admin_home,\
            'part_admin':part_admin,'school_album':school_album,'article':article,'link':link,\
            'part_all':part_all,'mailbox':mailbox,'school_mail':school_mail,'website_update':website_update,\
            'template':template,'site_admin':site_admin,'site_setting':site_setting,'figure':figure,\
            'manage_site':manage_site,'doc_my':doc_my,'doc_send':doc_send,'doc_approval':doc_approval,\
            'doc_reback':doc_reback,'doc_invalid':doc_invalid,'doc_doc':doc_doc,'doc_write':doc_write,\
            'doc_approvaled':doc_approvaled,'regist_apply':regist_apply,'communicate_access':communicate_access,\
            'personal_password':personal_password,'schedule':schedule,'teacher_authorize':teacher_authorize,\
            'supply_list':supply_list,'supply_category':supply_category,'supply_admin_home':supply_admin_home,\
            'provider_list':provider_list,'supply_document':supply_document,'supply_record':supply_record,'disks':disks,\
            'growth_oa_home':growth_oa_home,
        }
        
        self.activer_name = activer_name

    def render(self, context):
        style = 'on'
        request = context.get('request')
        try:
            url_name = resolve(request.path).url_name
            # print url_name
            activer_name = self.activer_name
            ac = self.activer_set.get(self.activer_name)
            if ac:
                if url_name in ac:
                    return style
        except Exception, e:
            pass
        return ''

@register.tag
def oa_activer(parser, token):  
    """
    根据某个activer，返回 style
    """
    try:
        tag_name, activer_name = token.split_contents()
    except:       
        raise template.TemplateSyntaxError,\
        "%r 标签语法错误，参数为需要激活的activer" % token.split_contents[0]                    

    return ActiverNode(activer_name)

@register.assignment_tag(takes_context=True)
def is_select_tag(context, t):
    request = context.get('request')
    try:
        url_name = resolve(request.path).url_name
        ac = ActiverNode(t).activer_set.get(t)
        if ac:
            if url_name in ac:
                return True
    except Exception, e:
        pass
    return ''

@register.assignment_tag(takes_context=True)
def get_moudle_name(context):
    request = context.get('request')
    try:
        url_name = resolve(request.path).url_name
        moudle_list = ActiverNode('').moudle_group
        for m in moudle_list:
            if url_name in m['urls']:
                return m['name'] + '-'
    except Exception, e:
        pass
    return ''

@register.filter
def type_name(val):
    if val == 0:
        return u"采购"
    if val == 1:
        return u"领取"
    return ''

@register.filter
def approval_status(obj):
    try:
        if obj.document.is_approvaled:
            return u"审批完毕"
    except:
        pass

    status = ['转发','发出','发回','送审']
    try:
        if obj.approvaler == obj.document.sender:
            if obj.status == 2:
                result = '[<span class="color_s">审批人' + obj.sender.teacher.name + '</span>]' + '已审阅并' + status[obj.status] + \
                '[<span class="color_s">撰文人' + obj.approvaler.teacher.name + '</span>]'   
            else:
                result = '待[<span class="color_s">审批人' + obj.approvaler.teacher.name + '</span>]'
        else:
            if obj.status == 1:
                result = '[<span class="color_s">审批人' + obj.sender.teacher.name + '</span>]' + '已审阅并' + status[obj.status] + '[给接收对象]' 
            else:
                if obj.status == 0:
                    result = '待[<span class="color_s">审批人' + obj.approvaler.teacher.name + '</span>]'
                else:
                    result = '[<span class="color_s">审批人' + obj.sender.teacher.name + '</span>]' + '已审阅并' + status[obj.status] + \
                        '[<span class="color_s">审批人' + obj.approvaler.teacher.name + '</span>]'
        if obj.status == 0:
            result = result + '审批'
    except:
        result = ''   
  
    return result

@register.filter
def document_status(doc):
    
    if doc.is_approvaled:
        return "已发出"
    
    status = ['转发','发出','发回','送审']
    try:
        last_appr = DocumentApproval.objects.filter(document=doc).order_by('-send_time')[0]
        if last_appr.approvaler == doc.sender:
            if last_appr.status == 2:
                result = '[<span class="color_s">审批人' + last_appr.sender.teacher.name + '</span>]' + '已审阅并' + status[last_appr.status] + \
                    '[<span class="color_s">撰文人' + last_appr.approvaler.teacher.name + '</span>]'
            else:
                result = '待[<span class="color_s">审批人' + last_appr.approvaler.teacher.name + '</span>]'
        else:
            if last_appr.status == 1:
                result = '[<span class="color_s">审批人' + last_appr.sender.teacher.name + '</span>]' + '已审阅并' + status[last_appr.status] + '[给接收对象]'
            else:
                if last_appr.status == 0:
                    result = '待[<span class="color_s">审批人' + last_appr.approvaler.teacher.name + '</span>]'
                else:
                    result = '[<span class="color_s">审批人' + last_appr.sender.teacher.name + '</span>]' + '已审阅并' + status[last_appr.status] + \
                        '[<span class="color_s">审批人' + last_appr.approvaler.teacher.name + '</span>]'   
        if last_appr.status == 0:
            result = result + '审批'
    except:
        result = ''
    return result


@register.filter
def material_status(doc):
    
    if doc.is_approvaled:
        return "已发出"
    
    status = ['转发','发出','发回','送审']
    try:
        last_appr = MaterialApproval.objects.filter(document=doc).order_by('-send_time')[0]
        if last_appr.approvaler == doc.sender:
            if last_appr.status == 2:
                result = '[<span class="color_s">审批人' + last_appr.sender.teacher.name + '</span>]' + '已审阅并' + status[last_appr.status] + \
                    '[<span class="color_s">撰文人' + last_appr.approvaler.teacher.name + '</span>]'
            else:
                result = '待[<span class="color_s">审批人' + last_appr.approvaler.teacher.name + '</span>]'
        else:
            if last_appr.status == 1:
                result = '[<span class="color_s">审批人' + last_appr.sender.teacher.name + '</span>]' + '已审阅并' + status[last_appr.status] + '[给接收对象]'
            else:
                if last_appr.status == 0:
                    result = '待[<span class="color_s">审批人' + last_appr.approvaler.teacher.name + '</span>]'
                else:
                    result = '[<span class="color_s">审批人' + last_appr.sender.teacher.name + '</span>]' + '已审阅并' + status[last_appr.status] + \
                        '[<span class="color_s">审批人' + last_appr.approvaler.teacher.name + '</span>]'   
        if last_appr.status == 0:
            result = result + '审批'
    except:
        result = ''
    return result

@register.filter
def can_cancel_doc(value,user):
    doc = value
    try:
        doca = DocumentApproval.objects.filter(document=doc,sender=user,status=0)[0]
        return True
    except:
        return False

@register.filter
def can_cancel_mat(value,user):
    doc = value
    try:
        doca = MaterialApproval.objects.filter(document=doc,sender=user,status=0)[0]
        return True
    except:
        return False
    
@register.filter
def apply_reback(app):
    doc = app.document
    supply = app.supply
    records = SupplyRecord.objects.filter(id__gt=0,document=doc,supply=supply)
    backs = SupplyReback.objects.filter(record__in=records)
    num = 0
    for b in backs:
        num += b.num
    return num
    

@register.filter
def last_website_access(user,site):
    accs = WebSiteAccess.objects.filter(user=user,website=site)
    try:
        return accs[0].access_time
    except:
        return ''
    
@register.filter
def get_workgroup_user(school,workgroup=None):
    if not workgroup:
        return ''
    member_pks = [u.id for u in workgroup.members.all()]
    users = [t.user_id for t in Teacher.objects.filter(school=school)]
    user_pks = ",".join([str(u) for u in users if u in member_pks])
    return user_pks

@register.filter
def get_document_user(school,doc=None):
    if not doc:
        return ''
    member_pks = [r.user.id for r in DocumentReceiver.objects.filter(document=doc)]
    users = [t.user_id for t in Teacher.objects.filter(school=school)]
    user_pks = ",".join([str(u) for u in users if u and u in member_pks])
    return user_pks

@register.filter
def get_name(user):
    """
    获取老师或学生的姓名
    """
    if is_teacher(user) and user.teacher.name:
        return user.teacher.name
    if is_student(user) and user.student.name:
        return user.student.name
    try:
        return user.profile.chinese_name_or_username()
    except:
        return ''

@register.filter
def get_school(user):
    """
    获取老师或学生的学校
    """
    if is_teacher(user):
        return user.teacher.school
    if is_student(user):
        return user.student.school
    return None

@register.filter
def get_tile_channel(tile):
    """
    """
    if tile.is_tips == 0:
        return ''
    if tile.is_tips == 1:
        return 'edu'
    if tile.is_tips == 2:
        return 'life'
    return 'edu'

@register.filter
def domain_enable(domain,status):
    return domain if status == 1 else "javascript:;"

@register.filter
def get_last_photo(album):
    """"""
    photos = Photo.objects.filter(album=album)
    if photos.count():
        return photos[0].img if photos[0].img else None
    else:
        return None
   
@register.assignment_tag(takes_context=True)
def get_site(context, site=None):
    if site:
        return site.id
    request = context.get('request')
    school = get_schools(request.user)[0]
    try:
        sites = WebSite.objects.filter(school=school,status=1).order_by('-ctime')
        return sites[0].id
    except:
        return 0
    
@register.filter
def video_html(video):
    """"""
    if video.video_type == 1:
        video_url = video.url
    else:
        video_url = video.video.url
        
    url = settings.STATIC_URL+'kinger/img/bg_video.png'
    return '<div class="videoDiv"><video class="html5video" controls="controls" width="640" height="380" \
    poster="' + url + '"><source src="' + str(video_url) + '" type="video/mp4" \
    /></video></div>'
    
@register.filter
def video_url(video):
    """"""
    if video.video_type == 1:
        video_url = video.url
    else:
        try:
            video_url = video.video.url    
        except:
            video_url = ''
    return video_url

@register.filter
def video_img(video):
    """"""
    url = settings.STATIC_URL+'kinger/img/bg_video.png'
    return url

@register.assignment_tag(takes_context=True)
def can_visit_menu(context, plate):
    if not plate:
        return False
    request = context.get('request')
    user_accesses = [a for a in user_access_list(request.user)]
    plate_accesses = [p for p in Access.objects.filter(parent__code=plate)]
    s = [c for c in user_accesses if c in plate_accesses]
    if len(s):
        return True
    else:
        return False
    
@register.filter
def can_visit_plate(user,acc=None):
    """"""
    if not user or not acc:
        return False
    user_accesses = [a for a in user_access_list(user)]
#     print user_accesses,'uuuuuuuu'
    try:
        access = Access.objects.get(code=acc)
#         print access,'aaaaaaaaa'
    except:
        return False
    return access in user_accesses


MENU_LIST = {
             "manage_contact":[{"access":"manage_message_list","url":reverse('oa_message_list')},\
                               {"access":"manage_send_message","url":reverse('oa_send_message')},\
                               {"access":"manage_message_record","url":reverse('oa_message_record')},],
             "manage_senate":[{"access":"manage_department","url":reverse('oa_department_list')},\
                              {"access":"manage_position","url":reverse('oa_position_list')},\
                              {"access":"manage_school","url":reverse('oa_school_list')},\
                              {"access":"manage_teacher","url":reverse('oa_teacher_list')},\
                              {"access":"manage_student","url":reverse('oa_student_list')},\
                              {"access":"manage_class","url":reverse('oa_class_list')},\
                              {"access":"manage_document","url":reverse('oa_my_document')},\
                              {"access":"manage_document_type","url":reverse('oa_document_category')},\
                              {"access":"manage_send_student_account","url":reverse('oa_student_send_account')},\
                              {"access":"manage_send_teacher_account","url":reverse('oa_teacher_send_account')},\
                              {"access":"manage_cookbook","url":reverse('oa_cookbook')},\
                              {"access":"manage_apply","url":reverse('oa_regist_apply_list')},\
                              {"access":"manage_disk","url":reverse('oa_disk_index')},\
                              ],
             "manage_access":[{"access":"manage_role","url":reverse('oa_permission_role_list')},\
                              {"access":"manage_role_set","url":reverse('oa_permission_designate_role')},\
                              {"access":"manage_personal_group","url":reverse('oa_workgroup_personal')},\
                              {"access":"manage_global_group","url":reverse('oa_workgroup_list')},\
                              {"access":"manage_communicate","url":reverse('oa_communicate')},\
                              {"access":"manage_authorize","url":reverse('oa_permission_change_authorize')},\
                              ],
             "manage_account_setting":[{"access":"manage_personal_message","url":reverse('oa_account_setting')},\
                              {"access":"manage_personal_group","url":reverse('oa_workgroup_personal')},\
                              ],
             "manage_log":[],
             "manage_school_website":[{"access":"manage_school_website_list","url":reverse('oa_website_list')},],
             "manage_supply_system":[{"access":"manage_supply_list","url":reverse('oa_supply_index')},
                               {"access":"manage_supply_record","url":reverse('oa_supply_record_index')},
                               {"access":"manage_supply_caregory","url":reverse('oa_supply_category')},
                               {"access":"manage_supply_provider","url":reverse('oa_provider_index')},
                               {"access":"manage_supply_document","url":reverse('oa_supply_my_document')},],
             }
@register.filter
def get_active_url(user=None, tag=None):
    if not user or not tag:
        return "javascript:;"
    access_codes = [a.code for a in user_access_list(user)]
    plates = MENU_LIST[tag]
    for p in plates:
        if p["access"] in access_codes:
            return p["url"]
    return "javascript:;"

@register.filter
def cut_users(users,num=None):
    try:
        if not num:
            result = ' '.join([get_user_name(u) for u in users])
            return result
        if users.count() > num:
            result = ' '.join([get_user_name(u) for u in users[0:num]])
            return result + ' ...'
        else:
            result = ' '.join([get_user_name(u) for u in users])
            return result
    except:
        return ''
        
@register.filter
def is_agency_user(user):
    try:
        school = user.teacher.school
        if school.parent_id == 0:
            return True
    except:
        pass
    return False

@register.filter
def is_agency_admin(user):
    try:
        school = user.teacher.school
        if school.parent_id == 0:
            admin_pks = []
            agencies = Agency.objects.all()
            for a in agencies:
                admin_pks += [u.id for u in a.admins.all()]
            return user.id in admin_pks
    except:
        pass
    return False

@register.assignment_tag(takes_context=True)
def get_school_site(context, school=None):
    if not school:
        return []
    try:
        sites = WebSite.objects.filter(school=school,status=1).order_by('-ctime')
        return sites
    except:
        return []

@register.assignment_tag(takes_context=True)
def get_parent_domain(context):
    request = context.get('request')
    return helpers.get_parent_domain(request)

@register.assignment_tag(takes_context=True)
def get_parent_domain_string(context):
    request = context.get('request')
    return helpers.get_parent_domain_string(request)

@register.filter
def is_agency(school):
    if school.parent_id == 0:
        return True
    return False

@register.filter
def document_level(level):
    level_choice = ['普通', '重要', '机密']
    try:
        return level_choice[level]
    except:
        pass
    return ''

@register.filter
def part_type(level):
    level_choice = ['草稿', '发布', '置顶']
    try:
        return level_choice[level]
    except:
        pass
    return ''

@register.filter
def is_empty_list(value):
    try:
        if len(value):
            return len(value)
        else:
            return False
    except:
     return False

@register.filter
def get_read_num(doc,ty="read"):
    if ty == "read":
        return DocumentReceiver.objects.filter(document=doc,is_read=True).count()
    else:
        return DocumentReceiver.objects.filter(document=doc).count()
    
@register.filter
def mat_read_num(doc,ty="read"):
    if ty == "read":
        return MaterialReceiver.objects.filter(document=doc,is_read=True).count()
    else:
        return MaterialReceiver.objects.filter(document=doc).count()

@register.filter
def record_is_back(record):
    for rs in record.subrecords.all():
        if rs.back < rs.num:
            return False
    return True

class UrlTagItem(template.Node): 
    def __init__(self, activer_name): 
        self.activer_name = activer_name
         
    def render(self, context): 
        request = context['request']
        domain = request.META['HTTP_HOST']
        url = reverse(self.activer_name).replace('/oa/site','')
        return domain + url
        
@register.tag
def url_for_site(parser, token):  
    """
    根据某个activer，返回 style
    """
    try:
        tag_name, activer_name = token.split_contents()
    except:       
        raise template.TemplateSyntaxError,\
        "%r 标签语法错误，参数为需要激活的activer" % token.split_contents[0]                    

    return UrlTagItem(activer_name)   


class URLNode(Node):
    def __init__(self, view_name, args, kwargs, asvar, legacy_view_name=True):
        self.view_name = view_name
        self.legacy_view_name = legacy_view_name
        self.args = args
        self.kwargs = kwargs
        self.asvar = asvar

    def render(self, context):
        from django.core.urlresolvers import reverse, NoReverseMatch
        args = [arg.resolve(context) for arg in self.args]
        kwargs = dict([(smart_str(k, 'ascii'), v.resolve(context))
                       for k, v in self.kwargs.items()])

        view_name = self.view_name
        if not self.legacy_view_name:
            view_name = view_name.resolve(context)

        # Try to look up the URL twice: once given the view name, and again
        # relative to what we guess is the "main" app. If they both fail,
        # re-raise the NoReverseMatch unless we're using the
        # {% url ... as var %} construct in which cause return nothing.
        url = ''
        try:
            url = reverse(view_name, args=args, kwargs=kwargs, current_app=context.current_app)
        except NoReverseMatch, e:
            if settings.SETTINGS_MODULE:
                project_name = settings.SETTINGS_MODULE.split('.')[0]
                try:
                    url = reverse(project_name + '.' + view_name,
                              args=args, kwargs=kwargs,
                              current_app=context.current_app)
                except NoReverseMatch:
                    if self.asvar is None:
                        # Re-raise the original exception, not the one with
                        # the path relative to the project. This makes a
                        # better error message.
                        raise e
            else:
                if self.asvar is None:
                    raise e

        if self.asvar:
            context[self.asvar] = url
            return ''
        else:
            request = context['request']
            domain_parts = request.get_host().split('.')
#            if len(domain_parts) == 4 and (domain_parts[1] == 'website' or domain_parts[1] == 'testwebsite'):
            if len(domain_parts) == 3 and (domain_parts[1] == 'jytn365' or domain_parts[1] == 'local'):
                url = url.replace('/oa/site','')
            return url
        
        
@register.tag
def url_site(parser, token):
    """
    """
    import warnings
    warnings.warn('The syntax for the url template tag is changing. Load the `url` tag from the `future` tag library to start using the new behavior.',
                  category=DeprecationWarning)

    bits = token.split_contents()
    if len(bits) < 2:
        raise TemplateSyntaxError("'%s' takes at least one argument"
                                  " (path to a view)" % bits[0])
    viewname = bits[1]
    args = []
    kwargs = {}
    asvar = None
    bits = bits[2:]
    if len(bits) >= 2 and bits[-2] == 'as':
        asvar = bits[-1]
        bits = bits[:-2]

    # Backwards compatibility: check for the old comma separated format
    # {% url urlname arg1,arg2 %}
    # Initial check - that the first space separated bit has a comma in it
    if bits and ',' in bits[0]:
        check_old_format = True
        # In order to *really* be old format, there must be a comma
        # in *every* space separated bit, except the last.
        for bit in bits[1:-1]:
            if ',' not in bit:
                # No comma in this bit. Either the comma we found
                # in bit 1 was a false positive (e.g., comma in a string),
                # or there is a syntax problem with missing commas
                check_old_format = False
                break
    else:
        # No comma found - must be new format.
        check_old_format = False

    if check_old_format:
        # Confirm that this is old format by trying to parse the first
        # argument. An exception will be raised if the comma is
        # unexpected (i.e. outside of a static string).
        match = kwarg_re.match(bits[0])
        if match:
            value = match.groups()[1]
            try:
                parser.compile_filter(value)
            except TemplateSyntaxError:
                bits = ''.join(bits).split(',')

    # Now all the bits are parsed into new format,
    # process them as template vars
    if len(bits):
        for bit in bits:
            match = kwarg_re.match(bit)
            if not match:
                raise TemplateSyntaxError("Malformed arguments to url tag")
            name, value = match.groups()
            if name:
                kwargs[name] = parser.compile_filter(value)
            else:
                args.append(parser.compile_filter(value))

    return URLNode(viewname, args, kwargs, asvar, legacy_view_name=True)

class SetVarNode(template.Node):
    def __init__(self, new_val, var_name):
        self.new_val = new_val
        self.var_name = var_name
    def render(self, context):
        context[self.var_name] = self.new_val
        return ''

@register.tag
def setvar(parser,token):
    # This version uses a regular expression to parse tag contents.
    try:
        # Splitting by None == splitting by spaces.
        tag_name, arg = token.contents.split(None, 1)
    except ValueError:
        raise template.TemplateSyntaxError, "%r tag requires arguments" % token.contents.split()[0]
    m = re.search(r'(.*?) as (\w+)', arg)
    if not m:
        raise template.TemplateSyntaxError, "%r tag had invalid arguments" % tag_name
    new_val, var_name = m.groups()
    if not (new_val[0] == new_val[-1] and new_val[0] in ('"', "'")):
        raise template.TemplateSyntaxError, "%r tag's argument should be in quotes" % tag_name
    return SetVarNode(new_val[1:-1], var_name)

@register.filter
def has_permission(user,code=""):
    if code:
        code_list = [c.code for c in helpers.user_access_list(user)]
        return code in code_list
    else:
        return False