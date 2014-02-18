# -*- coding: utf-8 -*-
#from django.http import HttpResponse
from django.conf import settings
from django.utils.translation import ugettext as _
from django.utils.translation import ungettext
from django.shortcuts import render_to_response, redirect, render, get_object_or_404
from django.views.decorators.http import require_http_methods
from kinger.models import Group, Student, Teacher, Mentor, Waiter,Position,WorkGroup,\
        Department,PostJob,GroupGrade,MailBox,WebSite,School,GroupTeacher
from django.core.exceptions import ObjectDoesNotExist
from kinger.helpers import get_redir_url,ajax_ok
from oa.forms import MessageForm
from django.shortcuts import render_to_response,render
from django.template import RequestContext
from django.dispatch import receiver
from django.contrib import messages
from django.shortcuts import HttpResponse

from django.contrib.auth.decorators import login_required, permission_required

from django.contrib.auth.models import User
import datetime
from django.db.models import Q
# message 额外功能
from django.contrib.auth.models import User
from userena.contrib.umessages.forms import ComposeForm
from userena.contrib.umessages.models import Message, MessageRecipient, MessageContact
from userena.utils import get_datetime_now
from django.views.generic import list_detail
from userena import settings as userena_settings
from django.contrib.auth import REDIRECT_FIELD_NAME
from django.core.urlresolvers import reverse
from oa.helpers import get_schools,get_school_with_workgroup
from oa.decorators import Has_permission
from oa import helpers
try:
    import simplejson as json
except ImportError:
    import json


@Has_permission('manage_message_list')
def message_list(request,template_name="oa/message_list.html"):
    """消息列表"""
    now = datetime.datetime.now()
    contacts = MessageContact.objects.get_contacts_for(request.user)
#    contacts = contacts.exclude(latest_message__is_send=False)
#    print contacts,'eeeeeeeeeeeeeeeeeeeeeeeeeeee'
    
    messages = MessageRecipient.objects.filter(user=request.user,\
                deleted_at__isnull=True,message__is_send=True).order_by('-id')
            
    ty = int(request.GET.get("ty",-1))
#    if ty == 0 or ty == 1:
#        messages = messages.filter(message__type=ty)
 
    ctx = {'message_list':messages,'user':request.user,'ty':ty,'contacts':contacts}
    return render(request,template_name,ctx)

@Has_permission('manage_message_record')
def message_record(request,template_name="oa/message_record.html"):
    """发信记录列表"""
    user = request.user
    messages = Message.objects.filter(sender=user,sender_deleted_at__isnull=True)
    ty = int(request.GET.get("ty",-1))
    if ty == 0 or ty == 1:
        messages = messages.filter(type=ty)
 
    ctx = {'message_list':messages,'user':request.user,'ty':ty}
    return render(request,template_name,ctx)

@Has_permission('manage_message_record')
def record_view(request,message_id,template_name="oa/message_record_view.html"):
    """发信记录详情"""
    message = get_object_or_404(Message,id=message_id)
    ctx = {'message':message}
    return render(request,template_name,ctx)

def cancel_timing(request,message_id):
    """取消定时发送"""
    message = get_object_or_404(Message,id=message_id)
    message.is_send = True
    message.send_at = message.timing
    message.save()
    ctx = {'message':message}
    return redirect(reverse('oa_message_record_view',kwargs={'message_id':message.id}))
    
@Has_permission('manage_send_message')
def send_message(request,template_name="oa/message_send.html"):
    """发送消息"""
    schools = get_school_with_workgroup(request.user)
    if request.method == "POST":
        recipient_pks = list(set(request.POST.getlist('to')))
        recipients = [u for u in User.objects.filter(pk__in=recipient_pks)]
        form = MessageForm(request.POST,recipients=recipients)
        if form.is_valid():
            message = form.save(User.objects.get(pk=request.user.id))
#             recipients = form.cleaned_data['to']
            return redirect(reverse('oa_message_record'))
    else:
        form = MessageForm()
        
    hour = range(8,23)
    minite = range(0,60,5)
    ctx = {'form':form,'hour':hour,'minite':minite,'schools':schools}
    return render(request,template_name,ctx)
    
@Has_permission('manage_message_list')
def user_message_history(request, user_id,compose_form=ComposeForm,\
                    success_url=None,template_name="oa/message_history.html"):
    """消息记录"""
    recipient = User.objects.get(id=user_id)
    
    queryset = Message.objects.get_conversation_between(request.user,
                                                        recipient).filter(is_send=True)
    # history 页面可以直接发送信息
    initial_data = dict() 
    initial_data["to"] = recipient
    form = compose_form(initial=initial_data)
    # 发布私信
    if request.method == "POST":
        form = compose_form(request.POST)
        if form.is_valid():
#             requested_redirect = request.REQUEST.get("next", False)
            message = form.save(request.user)
            message.is_send = True
            message.save()
            recipients = form.cleaned_data['to']
            if userena_settings.USERENA_USE_MESSAGES:
                messages.success(request, _('Message is sent.'),fail_silently=True)

#             return redirect("oa_message_history")

    # Update all the messages that are unread.
    page = int(request.GET.get("page", '1'))
    start = (page - 1) * 10
    end = page * 10 
    message_pks = [m.pk for m in queryset[start:end]]
    
    
    unread_list = MessageRecipient.objects.filter(message__in=message_pks,
                                                  user=request.user,
                                                  read_at__isnull=True)
    now = get_datetime_now()
    unread_list.update(read_at=now)

    ctx = dict()
    ctx['recipient'] = recipient
    ctx["form"] = form

    message_list = queryset
    ctx.update({"message_list":message_list})
    return render(request, template_name, ctx)

@login_required
def contact_remove(request):
    """
    """
    user_pks = request.POST.getlist('user_pks')
    print user_pks,'user_pks------------------------------'
    for user_id in user_pks:
        try:
            recipient = User.objects.get(id=user_id)
        except:
            continue
        if recipient:
            user = request.user
    
            try:
                #contacts = MessageContact.objects.filter(Q(from_user=request,to_user=recipient) | Q(to_user=request,from_user=recipient).all()
                contact = MessageContact.objects.filter(Q(from_user=request.user, to_user=recipient) |
                                       Q(from_user=recipient, to_user=request.user))
                #contact = MessageContact.objects.get(from_user=request.user,to_user=recipient)
                contact.delete()
                
                queryset = Message.objects.get_conversation_between(request.user,
                                                                recipient)
                message_pks = [m.pk for m in queryset]
    
                if message_pks:
                    post = request.POST.copy()
                    post.setlist('message_pks', message_pks)
                    request.POST = post
                    message_remove(request)
    
            except ObjectDoesNotExist:
                pass
    return redirect(reverse('oa_message_list'))
    
def message_remove(request, undo=False):
    """
    """
    message_pks = request.POST.getlist('message_pks')
    if message_pks:
        # Check that all values are integers.
        valid_message_pk_list = set()
        for pk in message_pks:
            try: valid_pk = int(pk)
            except (TypeError, ValueError): pass
            else:
                valid_message_pk_list.add(valid_pk)

        # Delete all the messages, if they belong to the user.
        now = get_datetime_now()
        changed_message_list = set()
        print valid_message_pk_list,'valid_message_pk_list'
        for pk in valid_message_pk_list:
            message = get_object_or_404(Message, pk=pk)

            # Check if the user is the owner
            if message.sender == request.user:
                if undo:
                    message.sender_deleted_at = None
                else:
                    message.sender_deleted_at = now
                message.save()
                changed_message_list.add(message.pk)

            # Check if the user is a recipient of the message
            if request.user in message.recipients.all():
                mr = message.messagerecipient_set.get(user=request.user,
                                                      message=message)
                if undo:
                    mr.deleted_at = None
                else:
                    mr.deleted_at = now
                mr.save()
                changed_message_list.add(message.pk)

        # update contact last message
        recipient_id = request.POST.get('recipient', False)
        if recipient_id:
            recipient = get_object_or_404(User, pk=recipient_id)
            if recipient:
                if message.sender == request.user:
                    to_user = recipient
                    from_user = request.user
                else:
                    to_user = request.user
                    from_user = recipient

                message_list = Message.objects.get_conversation_between(request.user, recipient)[:1]
                if message_list:
                    for one in message_list:
                        MessageContact.objects.update_contact(request.user,recipient,one)
                else:
                    contact = MessageContact.objects.get(Q(from_user=request.user, to_user=recipient))
                    if contact:
                        contact.delete()


        # Send messages
        if (len(changed_message_list) > 0) and userena_settings.USERENA_USE_MESSAGES:
            if undo:
                message = ungettext('Message is succesfully restored.',
                                    'Messages are succesfully restored.',
                                    len(changed_message_list))
            else:
                message = ungettext('Message is successfully removed.',
                                    'Messages are successfully removed.',
                                    len(changed_message_list))

#    return redirect(reverse('oa_message_list'))

@Has_permission('manage_message_list')
def delete_message(request):
    """删除消息"""
    message_pks = request.POST.getlist('message_pks')
    if message_pks:
        # Check that all values are integers.
        valid_message_pk_list = set()
        for pk in message_pks:
            try: valid_pk = int(pk)
            except (TypeError, ValueError): pass
            else:
                valid_message_pk_list.add(valid_pk)

        # Delete all the messages, if they belong to the user.
        now = get_datetime_now()
        changed_message_list = set()
        for pk in valid_message_pk_list:
            message = get_object_or_404(MessageRecipient, pk=pk).message
            # Check if the user is the owner
            if message.sender == request.user:
                message.sender_deleted_at = now
                 
                message.save()
                changed_message_list.add(message.pk)

            # Check if the user is a recipient of the message
            if request.user in message.recipients.all():
                mr = message.messagerecipient_set.get(user=request.user,
                                                      message=message)
                mr.deleted_at = now
                mr.save()
                changed_message_list.add(message.pk)

        if changed_message_list:
            messages.success(request, u"删除消息成功") 
    return redirect("oa_message_list")

def set_receiver(request, template_name="oa/message_receiver.html"):
    """ 设置组成员 """
#    schools = get_schools(request.user)
    schools = get_school_with_workgroup(request.user)
    school_id = int(request.POST.get("sid",0))
    data = request.POST.get('data','')
    user_pks = [int(u) for u in data.split(",") if u]
    
    try:
        school = get_object_or_404(School,id=school_id)
    except:
        school = schools[0]
    
    student_all = Student.objects.filter(school=school)
    teacher_all = Teacher.objects.filter(school=school)
    
    #全园家长群发控制
    try:
        teacher = request.user.teacher
        if teacher.is_authorize:
            group_list = Group.objects.filter(school=school).exclude(type=3)
        else:
            group_header_pks = [g.id for g in Group.objects.filter(headteacher=teacher).exclude(type=3)]
            group_teacher_pks = [gt.group_id for gt in GroupTeacher.objects.filter(teacher=teacher).exclude(type=3)]
            group_pks = group_header_pks + group_teacher_pks
            group_list = Group.objects.filter(id__in=group_pks).exclude(type=3)
    except:
        group_list = []
    print group_list,'group_list-----------------------------'
#    group_list = Group.objects.filter(school=school)

    student_group_list = []
    teacher_group_list = []
    
    group_grades = GroupGrade.objects.all()
    for grade in group_grades:
        t_list = []
        s_list = []
        grade_groups = group_list.filter(grade=grade)
#        if not request.user.teacher.is_authorize:
#            group_pks = [k.group_id for k in GroupTeacher.objects.filter(teacher=request.user.teacher)]
#            grade_groups = grade_groups.filter(id__in=group_pks)
        for g in grade_groups:
            #学生按照班级分组
            students = [s.user for s in Student.objects.filter(group=g)]
            if students:
                s_list.append({'id':g.id,'name':g.name,'members':students})
            #老师按照班级分组
            teachers = [s.user for s in Teacher.objects.filter(group=g)]
            if teachers:
                t_list.append({'id':g.id,'name':g.name,'members':teachers})
        if s_list:
            student_group_list.append({'id':grade.id,'name':grade.name,'groups':s_list})
        if t_list:
            teacher_group_list.append({'id':grade.id,'name':grade.name,'groups':t_list})
    
    #老师按照职位分组
    teacher_position_list = []
    positions = Position.objects.filter(school=school)
    for p in positions:
        print p.id,p.is_delete,'position---------------------------------'
#        members = [po.teacher.user for po in PostJob.objects.filter(position=p,teacher__is_delete=False)]
        members = []
        for po in PostJob.objects.filter(position=p):
            try:
                members.append(po.teacher.user)
            except:
                pass
        if members:
            teacher_position_list.append({'id':p.id,'name':p.name,'members':members})
    #老师按照部门分组
    teacher_depatrment_list = []
    departments = Department.objects.filter(school=school)
    for d in departments:
#        members = [p.teacher.user for p in PostJob.objects.filter(department=d)]
        members = []
        for dp in PostJob.objects.filter(department=d):
            try:
                members.append(dp.teacher.user)
            except:
                pass
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
    data = render(request, template_name,\
                  {'student_all':student_all,'teacher_all':teacher_all,\
                   'student_group_list':student_group_list,\
                   'teacher_group_list':teacher_group_list,\
                   'teacher_position_list':teacher_position_list,\
                   'teacher_depatrment_list':teacher_depatrment_list,\
                   'teacher_word_list':teacher_word_list,\
                   'personal_workgoup_list':personal_workgoup_list,\
                   'global_workgroup_list':global_workgroup_list,\
                   'school':school,'schools':schools,'user_pks':user_pks})
    con=data.content
    return ajax_ok('成功',con)

def mailbox_index(request,site_id,template_name="oa/mailbox_index_list.html"):
    """次方法已作废"""
    site = get_object_or_404(WebSite,id=site_id)
    helpers.set_website_visit(request.user,site)
#    school = site.school
#    user=school.header
    messages = MailBox.objects.filter(site=site)
    ty = int(request.GET.get("ty",-1))
    if ty != -1:
        messages = messages.filter(is_read=ty)
    ctx = {'message_list':messages,'ty':ty,'site':site}
    return render(request,template_name,ctx)

def mailbox(request,site_id,template_name="oa/mailbox_list.html"):
    """站点管理园长信箱列表"""
    site = get_object_or_404(WebSite,id=site_id)
    helpers.set_website_visit(request.user,site)
#    school = get_schools(request.user)[0]
#    user=school.header
    messages = MailBox.objects.filter(site=site).order_by('-ctime')
    ty = int(request.GET.get("ty",-1))
    if ty != -1:
        messages = messages.filter(is_read=ty)
    ctx = {'message_list':messages,'ty':ty,'site':site}
    return render(request,template_name,ctx)
        
def delete_mailbox(request,site_id):
    """站点管理园长信箱删除"""
    if request.method == 'POST':
        mailbox_pks = request.POST.getlist('mailbox_pks')
        mailboxs = MailBox.objects.filter(pk__in=mailbox_pks)
        mailboxs.delete()
    return redirect(reverse('oa_mailbox',kwargs={'site_id':site_id}))

def mailbox_detail(request,mailbox_id,template_name="oa/mailbox_detail.html"):
    """站点管理园长信箱详情"""
    mailbox = get_object_or_404(MailBox,id=mailbox_id)
    mailbox.is_read = True
    mailbox.save()
    print mailbox.is_read,'rrrrrrrrrrrrrrrrrr'
    site = mailbox.site
    helpers.set_website_visit(request.user,site)
    ctx ={'mailbox':mailbox,'site':site}
    return render(request,template_name,ctx)

def mailbox_set(request,mailbox_id):
    """更新状态"""
    mailbox = get_object_or_404(MailBox,id=mailbox_id)
    if mailbox.is_read:
        mailbox.is_read = False
    else:
        mailbox.is_read = True
    mailbox.save()
    site = mailbox.site
    ctx ={"status":mailbox.is_read}
    print mailbox.is_read,'rrrrrrrrrrrrrrrrrr'
    return HttpResponse(json.dumps(ctx))
#    return redirect(reverse('oa_mailbox_detail',kwargs={'mailbox_id':mailbox.id}))

