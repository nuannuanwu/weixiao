# -*- coding: utf-8 -*-

from piston.handler import BaseHandler
from api.helpers import rc, DispatchMixin

from kinger.models import Student, Group, Mentor, Tile,Waiter,Teacher, MessageToClass,GroupTeacher
from django.contrib.auth.models import User
from notifications.models import Notification

from userena.contrib.umessages.models import Message, MessageRecipient, MessageContact
from userena.contrib.umessages.forms import ComposeForm
from userena.utils import get_datetime_now
from api.helpers import query_range_filter,get_agency_teacher_by_group
#from oa.helpers import get_agency_teacher_by_group

class MessageContactHandler(BaseHandler):
    model = MessageContact
    allowed = ("GET",)


class MessageHandler(DispatchMixin, BaseHandler):
    model = Message
    fields = ("id", "content", "ctime", "from_user","body","sender_id")
    allowed_methods = ("GET")
    csrf_exempt = True

    @classmethod
    def content(cls, model, request):
        return model.body

    @classmethod
    def from_user(cls, model, request):
        return model.sender

    @classmethod
    def ctime(cls, model, request):
        return model.sent_at

    def unread_count(self, request):
        """
        获取某个用户的各种消息未读数

        ``GET`` `remind/unread_count/ <http://192.168.1.222:8080/v1/remind/unread_count>`_

        """
        user = request.user
        class_id = request.GET.get("class_id")
        try:
            teacher = user.teacher
            if teacher:
                tile_count = 0
                push_tile_count = 0
        except Teacher.DoesNotExist:
            tile_count = Tile.objects.count_unread_tiles_for(user)
            push_tile_count = Tile.objects.count_unread_push_tiles_for(user)
        
        if class_id:
            now = get_datetime_now()
            try:
                group = Group.objects.get(pk=class_id)
            except Group.DoesNotExist:
                return rc.NOT_HERE
            
            group_user = []
            teacher_user = [t.user for t in group.get_teachers()]
            group_user.extend(teacher_user)
            
            student_user = [s.user for s in group.students.all()]
            group_user.extend(student_user)
            
            try:
                mentor_user = [m.user for m in Mentor.objects.all()]
                group_user.extend(mentor_user)
         
                waiter_user = [w.user for w in Waiter.objects.all().select_related('user')]
                group_user.extend(waiter_user)
            except:
                pass
            
#            messages_count = MessageRecipient.objects.filter(user=user,read_at__isnull=True,message__sent_at__lte=now,\
#                    deleted_at__isnull=True,message__sender__in=group_user).exclude(message__sender=request.user).count()
            messages_records = MessageRecipient.objects.filter(user=user,read_at__isnull=True,message__sent_at__lte=now,\
                    deleted_at__isnull=True,message__sender__in=group_user).exclude(message__sender=request.user)
            try:
                if user.teacher:
                    messages_records = messages_records.exclude(message__sender__in=teacher_user)
                if user.student:
                    messages_records = messages_records.exclude(message__sender__in=student_user)
            except:
                pass
            messages_count = messages_records.count()
            
        else:
            messages_count = MessageRecipient.objects.count_unread_messages_for(request.user)
        
        unread_contact = {}
        try:
            unread_list = MessageRecipient.objects.filter(user=request.user,read_at__isnull=True,deleted_at__isnull=True)
            unread_list.update(no_need_send=1)

            for m in unread_list:
                sender_id = m.message.sender.id
                unread_contact.setdefault(sender_id,0)  
            for m in unread_list:
                sender_id = m.message.sender.id
                unread_contact[sender_id] += 1
        except:
            pass
        
        notify_count = Notification.objects.count_notify_group(user)    
        return {"messages": messages_count,'tile_count':tile_count,'push_tile_count':push_tile_count,'notify_count':notify_count,'messages_info':unread_contact}

    def history(self, request):
        """
        与某人的沟通记录

        ``GET`` `messages/history/ <http://192.168.1.222:8080/v1/messages/history>`_

        :param uid:
            用户 id
        """
        params = request.GET
        user_id = request.GET.get("uid")
        try:
            recipient = User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return rc.NOT_HERE

        messages = Message.objects.get_conversation_between(request.user,
                                                        recipient)

       # Update all the messages that are unread.
        message_pks = [m.pk for m in messages]
        unread_list = MessageRecipient.objects.filter(message__in=message_pks,
                                                      user=request.user,
                                                      read_at__isnull=True)
        now = get_datetime_now()
        unread_list.update(read_at=now)
        return query_range_filter(params, messages, "messages")        
        return messages

    def contacts(self, request):
        """
        快速联系人(学生/教师)列表

        ``GET`` `messages/contacts/ <http://192.168.1.222:8080/v1/messages/contacts>`_

        :param class_id:
            关联班级的 id
        """
#        from api.helpers import get_agency_teacher_by_group
        teachers = students = mentors = group = waiters = []
        class_id = request.GET.get("class_id")
#        if not class_id:
#            return rc.BAD_REQUEST
        if class_id:
            try:
                group = Group.objects.get(pk=class_id)
            except Group.DoesNotExist:
                pass

#        teachers = group.teachers.all()
        if group:
            teachers_pre = [t for t in group.teachers.all()]
            teachers_ext = [g.teacher for g in GroupTeacher.objects.filter(group=group)]
            teacher_age = get_agency_teacher_by_group(group)
#            teacher_adm = [a.teacher for a in group.school.admins.all()]
            teacher_adm = []
            for a in group.school.admins.all():
                try:
                    teacher_adm.append(a.teacher)
                except:pass
            teachers = teachers_pre + teachers_ext + teacher_age + teacher_adm
            teachers = list(set(teachers))
    
            try:
                teacher = request.user.teacher
                if teacher:
                    students = group.students.all()
            except:
                pass


        try:
            mentors = Mentor.objects.all()
        except:
            pass

        try:
             waiters = Waiter.objects.all().select_related('user')
        except :
            pass

        user = request.user

        contact_list = []
        mc = MessageContact.objects.get_contacts_for(user) 
        for m in mc:
            latest_message = Message.objects.get_latest_message(user, m)

            from_user = latest_message.sender
            to_user = m.to_user if m.from_user == from_user else m.from_user          

            unread_count = 0
            if user == to_user:           
                unread_count = MessageRecipient.objects.count_unread_messages_between(user,from_user)
            try:
                name = m.to_user.get_profile().chinese_name_or_username()
            except :
                name = m.to_user.get_profile().chinese_name()
                pass
            
            contact_info = {
                'user': m.to_user,
                'name': name,
                'latest_message':{
                    'id':latest_message.pk,
                    'from_user':from_user,
                    'to_user':to_user,
                    'content':latest_message.body,                    
                    'sent_at':latest_message.sent_at
                },
                'unread_count':unread_count,             
            }          

            contact_list.append(contact_info)            

        # other model need to reset fields
        self.fields = ("id","school_id", "name", "appellation", "description", "ctime", ("user", ()),\
            "username", "avatar", "avatar_large", "mobile", "about_me")
        mm = {"teachers": teachers, "students": students, "mentors": mentors, "waiters": waiters, "contacts": contact_list}
        return mm



class MessageActionHandler(MessageHandler):
    """
    管理瓦片操作.
    """
    allowed_methods = ("POST")


    def post_to_class(self, request):
        """
        发送一条班级信息（群发）

        ``POST`` `messages/create_to_class/ <http://192.168.1.222:8080/v1/messages/create_to_class>`_

        :param class_id:
            接收班级的班级 id

        :param content:
            发送内容
        """
        class_id = request.POST.get("class_id")
        params = request.POST.dict()
        params['body'] = params.pop('content')
 
        group = None
        try:
            group = Group.objects.get(pk=class_id)
        except Group.DoesNotExist:
            return rc.NOT_HERE
        if group and params['body']:
            c = MessageToClass(group=group, user=request.user, content=params['body'])
            c.save()
            
        students = Student.objects.filter(group__pk=class_id)
        recipients = [s.user for s in students]
        params['to'] = ",".join([r.username for r in recipients])
        
        form = ComposeForm(params)
        if form.is_valid():
            return form.save(request.user)
        return rc.BAD_REQUEST

    def post(self, request):
        """
        发送一条信息

        ``POST`` `messages/create/ <http://192.168.1.222:8080/v1/messages/create>`_

        :param uid:
            接受者的用户 id

        :param content:
            发送内容
        """
        params = request.POST.dict()
        user_id = params.pop("uid")
        try:
            recipient = User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return rc.NOT_HERE

        params['body'] = params.pop('content')
        params['to'] = recipient.username
        form = ComposeForm(params)
        if form.is_valid():
            return form.save(request.user)

        return rc.BAD_REQUEST

    def delete(self, request):
        """
        删除一条信息

        ``POST`` `messages/destroy/ <http://192.168.1.222:8080/v1/messages/destroy>`_

        :param id:
            该信息的 id
        """
        message_id = request.POST.get("id")
        if not message_id:
            return rc.BAD_REQUEST

        try:
            message = Message.objects.get(pk=message_id)
        except Message.DoesNotExist:
            return rc.NOT_HERE

        now = get_datetime_now()
        if message.sender == request.user:
            message.sender_deleted_at = now
            message.save()

        if request.user in message.recipients.all():
            mr = message.messagerecipient_set.get(user=request.user,
                                                  message=message)
            mr.deleted_at = now
            mr.save()

        return rc.accepted({"result": True})


class MessageToClassHandler(BaseHandler):
    model = MessageToClass
    fields = ("id", "content", "ctime", "from_user")
    allowed_methods = ("GET")
    
    @classmethod
    def from_user(cls, model, request):
        return model.user
   
    
    def read(self, request,):
        """
        班级记录查询接口

        ``GET`` `messages/history_to_class/ <http://192.168.1.222:8080/v1/messages/history_to_class>`_

        :param class_id:班级 id
        :param since_id:返回ID比since_id大的评论,默认为0。
        :param max_id:返回ID小于或等于max_id的评论,默认为0。
        :param count:单页返回的记录条数，默认为50
        :param page:结果的页码,默认为1
        """
        params = request.GET
        class_id = request.GET.get("class_id")
        since_id = request.GET.get("since_id","0")
        max_id = request.GET.get("max_id","0")
        count = request.GET.get("count","0")
        page = request.GET.get("page","0")
        try:
            group = Group.objects.get(pk=class_id)
        except Group.DoesNotExist:
            return rc.NOT_HERE

        contents = MessageToClass.objects.filter(group=group)
        contents = contents.filter(id__gte=since_id) if since_id!='0' else contents
        contents = contents.filter(id__lte=max_id) if max_id!='0' else contents
        return query_range_filter(params, contents, "messages")

    
class MessageTestHandler(BaseHandler):
    model = Message
    allowed_methods = ("GET")
    fields = ("id", "content", "ctime", "from_user","body","sender_id")

    @classmethod
    def content(cls, model, request):
        return model.body

    @classmethod
    def from_user(cls, model, request):
        return model.sender

    @classmethod
    def ctime(cls, model, request):
        return model.sent_at

    def read(self, request,):
        """
        与某人的沟通记录

        ``GET`` `messages/history/ <http://192.168.1.222:8080/v1/messages/history>`_

        :param uid:
            用户 id
        """
        params = request.GET
        user_id = request.GET.get("uid")
        try:
            recipient = User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return rc.NOT_HERE

        messages = Message.objects.get_conversation_between(request.user,
                                                        recipient)

       # Update all the messages that are unread.
        message_pks = [m.pk for m in messages]
        unread_list = MessageRecipient.objects.filter(message__in=message_pks,
                                                      user=request.user,
                                                      read_at__isnull=True)
        now = get_datetime_now()
        unread_list.update(read_at=now)
        return query_range_filter(params, messages, "messages")

