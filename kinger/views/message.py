# -*- coding: utf-8 -*-
#from django.http import HttpResponse
from django.conf import settings
from django.utils.translation import ugettext as _
from django.utils.translation import ungettext
from django.shortcuts import render_to_response, redirect, render, get_object_or_404
from django.views.decorators.http import require_http_methods
from kinger.models import Group, Student, Teacher, Mentor, Waiter,GroupTeacher
from django.core.exceptions import ObjectDoesNotExist
from kinger.helpers import get_redir_url,ajax_ok
from django.shortcuts import render_to_response,render
from django.template import RequestContext
from django.dispatch import receiver
from django.contrib import messages
from oa.helpers import get_agency_teacher_by_group

from django.contrib.auth.decorators import login_required, permission_required

from django.contrib.auth.models import User


# message 棰濆鍔熻兘
from django.contrib.auth.models import User
from userena.contrib.umessages.forms import ComposeForm
from userena.contrib.umessages.models import Message, MessageRecipient, MessageContact
from userena.utils import get_datetime_now
from django.views.generic import list_detail
from userena import settings as userena_settings
from django.contrib.auth import REDIRECT_FIELD_NAME
from django.core.urlresolvers import reverse


@login_required
def message_list(request, page=1, paginate_by=50,
                 template_name="umessages/message_list.html",
                 extra_context=None, **kwargs):
    """

    Returns the message list for this user. This is a list contacts
    which at the top has the user that the last conversation was with. This is
    an imitation of the iPhone SMS functionality.

    :param page:
        Integer of the active page used for pagination. Defaults to the first
        page.

    :param paginate_by:
        Integer defining the amount of displayed messages per page.
        Defaults to 50 messages per per page.

    :param template_name:
        String of the template that is rendered to display this view.

    :param extra_context:
        Dictionary of variables that will be made available to the template.

    If the result is paginated, the context will also contain the following
    variables.

    ``paginator``
        An instance of ``django.core.paginator.Paginator``.

    ``page_obj``
        An instance of ``django.core.paginator.Page``.

    """

    queryset = MessageContact.objects.get_contacts_for(request.user)    
    if not extra_context: extra_context = dict()
    waiter = Waiter.objects.latest('pk')
    extra_context.update({'waiter':waiter,'type':0})  
    return list_detail.object_list(request,
                                   queryset=queryset,
                                   paginate_by=paginate_by,
                                   page=page,
                                   template_name=template_name,
                                   extra_context=extra_context,
                                   template_object_name="message",
                                   **kwargs)

#from notifications import notify
@login_required
def message_history(request, username, page=1, paginate_by=10, compose_form=ComposeForm,
                success_url=None,
                   template_name="umessages/message_history.html",
                   extra_context=None, **kwargs):
    """
    Returns a conversation between two users

    :param username:
        String containing the username of :class:`User` of whom the
        conversation is with.

    :param page:
        Integer of the active page used for pagination. Defaults to the first
        page.

    :param paginate_by:
        Integer defining the amount of displayed messages per page.
        Defaults to 50 messages per per page.

    :param extra_context:
        Dictionary of variables that will be made available to the template.

    :param template_name:
        String of the template that is rendered to display this view.

    If the result is paginated, the context will also contain the following
    variables.

    ``paginator``
        An instance of ``django.core.paginator.Paginator``.

    ``page_obj``
        An instance of ``django.core.paginator.Page``.

    """   

    type = request.GET.get("type",'')
    try:
        recipient = User.objects.get(username__iexact=username)
        if request.user == recipient:
            return redirect(reverse('userena_umessages_list'))
    except:
        return redirect(reverse('userena_umessages_list'))
    
    queryset = Message.objects.get_conversation_between(request.user,
                                                        recipient)
    # history 椤甸潰鍙互鐩存帴鍙戦�淇℃伅
    initial_data = dict() 
   
    initial_data["to"] = recipient

    form = compose_form(initial=initial_data)
    # 鍙戝竷绉佷俊
    if request.method == "POST":
        form = compose_form(request.POST)
        if form.is_valid():
            requested_redirect = request.REQUEST.get("next", False)

            message = form.save(request.user)



            recipients = form.cleaned_data['to']
            if userena_settings.USERENA_USE_MESSAGES:
                messages.success(request, _('Message is sent.'),
                                 fail_silently=True)

            requested_redirect = request.REQUEST.get(REDIRECT_FIELD_NAME,
                                                     False)

            # Redirect mechanism
            redirect_to = reverse('userena_umessages_list')
            if requested_redirect: redirect_to = requested_redirect
            elif success_url: redirect_to = success_url
            elif len(recipients) == 1:
                redirect_to = reverse('userena_umessages_history',
                                      kwargs={'username': recipients[0].username})
                redirect_to = redirect_to + '?type=' + type

            #actions = {'title':'鏂版秷鎭�,'href':redirect_to}
            #notify.send(request.user, verb='鏂版秷鎭�, action_object=message, recipient=recipient, actions=actions)

            return redirect(redirect_to)



    # Update all the messages that are unread.
    message_pks = [m.pk for m in queryset]
    
    unread_list = MessageRecipient.objects.filter(message__in=message_pks,
                                                  user=request.user,
                                                  read_at__isnull=True)
    now = get_datetime_now()
    unread_list.update(read_at=now)

    if not extra_context: extra_context = dict()
    extra_context['recipient'] = recipient
    extra_context['type'] = type
    extra_context["form"] = form

    message_list = queryset

    ctx = extra_context
    ctx.update({"message_list":message_list,"paginate_by":paginate_by})

    return render(request, template_name, ctx)
    # 浠ヤ笅鏄痙jango鑷甫鐨勫垎绫�
    return list_detail.object_list(request,
                                   queryset=queryset,
                                   paginate_by=paginate_by,
                                   page=page,
                                   template_name=template_name,
                                   extra_context=extra_context,
                                   template_object_name="message",
                                   **kwargs)


@login_required
def user_message_history(request, uid, page=1, paginate_by=10, compose_form=ComposeForm,
                success_url=None,
                   template_name="umessages/message_history.html",
                   extra_context=None, **kwargs):
    """
    Returns a conversation between two users

    :param page:
        Integer of the active page used for pagination. Defaults to the first
        page.

    :param paginate_by:
        Integer defining the amount of displayed messages per page.
        Defaults to 50 messages per per page.

    :param extra_context:
        Dictionary of variables that will be made available to the template.

    :param template_name:
        String of the template that is rendered to display this view.

    If the result is paginated, the context will also contain the following
    variables.

    ``paginator``
        An instance of ``django.core.paginator.Paginator``.

    ``page_obj``
        An instance of ``django.core.paginator.Page``.

    """   

    type = request.GET.get("type",'')
    try:
        recipient = User.objects.get(pk=uid)
        if request.user == recipient:
            return redirect(reverse('userena_umessages_list'))
    except:
        return redirect(reverse('userena_umessages_list'))
    
    queryset = Message.objects.get_conversation_between(request.user,
                                                        recipient)
    # history 椤甸潰鍙互鐩存帴鍙戦�淇℃伅
    initial_data = dict() 
   
    initial_data["to"] = recipient

    form = compose_form(initial=initial_data)
    # 鍙戝竷绉佷俊
    if request.method == "POST":
        form = compose_form(request.POST)
        if form.is_valid():
            requested_redirect = request.REQUEST.get("next", False)

            message = form.save(request.user)



            recipients = form.cleaned_data['to']
            if userena_settings.USERENA_USE_MESSAGES:
                messages.success(request, _('Message is sent.'),
                                 fail_silently=True)

            requested_redirect = request.REQUEST.get(REDIRECT_FIELD_NAME,
                                                     False)

            # Redirect mechanism
            redirect_to = reverse('userena_umessages_list')
            if requested_redirect: redirect_to = requested_redirect
            elif success_url: redirect_to = success_url
            elif len(recipients) == 1:
                redirect_to = reverse('user_umessages_history',kwargs={'uid':uid})

            #actions = {'title':'鏂版秷鎭�,'href':redirect_to}
            #notify.send(request.user, verb='鏂版秷鎭�, action_object=message, recipient=recipient, actions=actions)

            return redirect(redirect_to)



    # Update all the messages that are unread.
    message_pks = [m.pk for m in queryset]
    
    unread_list = MessageRecipient.objects.filter(message__in=message_pks,
                                                  user=request.user,
                                                  read_at__isnull=True)
    now = get_datetime_now()
    unread_list.update(read_at=now)

    if not extra_context: extra_context = dict()
    extra_context['recipient'] = recipient
    extra_context['type'] = type
    extra_context["form"] = form

    message_list = queryset

    ctx = extra_context
    ctx.update({"message_list":message_list,"paginate_by":paginate_by})

    return render(request, template_name, ctx)
    # 浠ヤ笅鏄痙jango鑷甫鐨勫垎绫�
    return list_detail.object_list(request,
                                   queryset=queryset,
                                   paginate_by=paginate_by,
                                   page=page,
                                   template_name=template_name,
                                   extra_context=extra_context,
                                   template_object_name="message",
                                   **kwargs)


@login_required
def message_quick_contact(request, template_name="umessages/message_quick_contact.html"):

    teachers = students = mentors = group = waiters = {}
    try:
        student = request.user.student
        if student:
            print student,'ssssssssssssssssssss'
            group = student.group
            teachers_pre = [t for t in group.teachers.all().select_related('user')]
            teachers_ext = [g.teacher for g in GroupTeacher.objects.filter(group=group)]
            teacher_age = get_agency_teacher_by_group(group)
#            teacher_adm = [a.teacher for a in student.school.admins.all()]
            teacher_adm = []
            for a in student.school.admins.all():
                try:
                    teacher_adm.append(a.teacher)
                except:pass
            teachers = teachers_pre + teachers_ext + teacher_age + teacher_adm
            
            teachers = list(set(teachers))
            #students = group.students.all().select_related('user')
    except ObjectDoesNotExist:
        pass
    
    try:
        group_pks = [g.id for g in request.user.teacher.groups.all()]
        students = Student.objects.filter(group_id__in=group_pks).select_related('user')
    except ObjectDoesNotExist:
        pass
    
    try:
        mentors = Mentor.objects.all().select_related('user')
    except ObjectDoesNotExist:
        pass

    try:
         waiters = Waiter.objects.all().select_related('user')
    except ObjectDoesNotExist:
        pass
       
    waiter = Waiter.objects.latest('pk')
    ctx = {'teachers':teachers,'students':students,'group':group,'mentors':mentors,'waiters':waiters,'waiter':waiter,'type':1}
    return render(request,template_name,ctx)


@login_required
#@require_http_methods(["POST"])
def message_remove(request, undo=False):
    """
    A ``POST`` to remove messages.

    :param undo:
        A Boolean that if ``True`` unremoves messages.

    POST can have the following keys:

        ``message_pks``
            List of message id's that should be deleted.

        ``next``
            String containing the URI which to redirect to after the keys are
            removed. Redirect defaults to the inbox view.

    The ``next`` value can also be supplied in the URI with ``?next=<value>``.

    """
    message_pks = request.POST.getlist('message_pks')
    redirect_to = request.REQUEST.get('next', False)

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
                print message_list,"==============="
                if message_list:
                    for one in message_list:
                        print one,"oooooooooooo"
                        MessageContact.objects.update_contact(request.user,recipient,one)
                else:
                    contact = MessageContact.objects.get(Q(from_user=request.user, to_user=recipient))
                    print contact,"===========2222222"
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


    if request.is_ajax():
        return ajax_ok(message)
    else:
        messages.success(request, message, fail_silently=True)
        if redirect_to: return redirect(redirect_to)
        else: return redirect(reverse('userena_umessages_list'))
        
        
from django.db.models import Q
@login_required
def contact_remove(request, username):
    """
    A ``POST`` to remove messages.

    :param undo:
        A Boolean that if ``True`` unremoves messages.

    POST can have the following keys:

        ``message_pks``
            List of message id's that should be deleted.

        ``next``
            String containing the URI which to redirect to after the keys are
            removed. Redirect defaults to the inbox view.

    The ``next`` value can also be supplied in the URI with ``?next=<value>``.

    """

    recipient = get_object_or_404(User,
                                  username__iexact=username)
    redirect_to = request.REQUEST.get('next', False)

    if recipient:
        user = request.user

        try:
            #contacts = MessageContact.objects.filter(Q(from_user=request,to_user=recipient) | Q(to_user=request,from_user=recipient).all()
            contact = MessageContact.objects.filter(Q(from_user=request.user, to_user=recipient) |
                                   Q(from_user=recipient, to_user=request.user))
            #contact = MessageContact.objects.get(from_user=request.user,to_user=recipient)
            contact.delete()
            
            # 鑾峰緱鎵�湁pks
            queryset = Message.objects.get_conversation_between(request.user,
                                                            recipient)
            message_pks = [m.pk for m in queryset]

            if message_pks:
                post = request.POST.copy()
                post.setlist('message_pks', message_pks)
                request.POST = post
                return message_remove(request)

        except ObjectDoesNotExist:
            pass
        return redirect(reverse('userena_umessages_list'))
