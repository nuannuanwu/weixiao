# -*- coding: utf-8 -*-
from django.shortcuts import render_to_response, redirect, render, get_object_or_404
from django.contrib.auth.models import User
from django.contrib import messages
from django.utils.translation import ugettext as _
from django.core.exceptions import ObjectDoesNotExist

from aq.decorators import aq_required
from aq.models import Track,OperatorsMessage
from kinger.helpers import ajax_ok, ajax_error, pagination
from django.core.urlresolvers import reverse
from django.http import HttpResponse
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.db.models import Q
from kinger.models import Mentor
from userena.contrib.umessages.models import Message, MessageRecipient, MessageContact
from userena.utils import get_datetime_now

# 返回导师的最新消息数
@aq_required
def index(request,template_name="aq/index.html"): 

	# 得到筛选的导师
	try:
		the_mentor = int(request.GET['mentor'])		
	except:
		the_mentor = ''

	mentors = Mentor.objects.all()
	if the_mentor == '':		
		mentor_id_list = [mentor.user_id for mentor in mentors]	
	else:
		mentor_id_list = [the_mentor]
	
	# 取得跟导师的对话的人
	to_mentor_conversation = MessageContact.objects.filter(Q(from_user__in=mentor_id_list))
	
	# 提问总人数
	askers_count = to_mentor_conversation.count()

	# 筛选出最后一次回复是家长的对话,并构建数据
	mes = []

	for c in to_mentor_conversation:
		# 得到最后一条消息->会话以导师的角度为准
		conversation = Message.objects.get_conversation_between(c.from_user,c.to_user)[:3]	
		last_message = conversation[0]

		if not last_message.sender.pk in mentor_id_list:

			user = c.to_user
			to_user = c.from_user

			try:
				is_track = c.mentor_track.is_track
			except:
				is_track = False
		
			mes.append({
					'contact_id':c.id,
					'user':user,
					'to_user':to_user,
					'last_message':last_message,
					'conversation':conversation,
					'is_track':is_track,
					'unread_num': MessageRecipient.objects.count_unread_messages_between(to_user,user)
			})
	mes_count = len(mes)

	mes,query = pagination(request,mes,10)	

	return render(request,template_name,{'mes':mes,'mes_count':mes_count,'askers_count':askers_count,'mentors': mentors,'query':query, 'page_type':'ask'})

# 导师问题跟踪页
@aq_required
def track(request,template_name="aq/track.html"): 
	# 得到筛选的导师
	try:
		the_mentor = int(request.GET['mentor'])		
	except:
		the_mentor = ''

	mentors = Mentor.objects.all()
	if the_mentor == '':		
		mentor_id_list = [mentor.user_id for mentor in mentors]	
	else:
		mentor_id_list = [the_mentor]	
	
	# 取得跟导师的对话,且是跟踪的
	to_mentor_conversation = MessageContact.objects.filter(Q(from_user__in=mentor_id_list), mentor_track__is_track=True)
		
	# 构建数据
	mes = []

	for c in to_mentor_conversation:
		# 得到最后一条消息
		conversation = Message.objects.get_conversation_between(c.from_user,c.to_user)[:3]	
		last_message = conversation[0]	
			
		user = c.to_user
		to_user = c.from_user

		try:
			is_track = c.mentor_track.is_track
		except:
			is_track = False
	
		mes.append({
				'contact_id':c.id,
				'user':user,
				'to_user':to_user,
				'last_message':last_message,
				'conversation':conversation,
				'is_track':is_track,
				'unread_num': MessageRecipient.objects.count_unread_messages_between(to_user,user)
		})
	# 未回消息数
	# mes_count = len(mes)	

	# 已跟踪人数
	trackers_count = len(to_mentor_conversation)

	mes,query = pagination(request,mes,10)	

	ctx = {
		'mes':mes,		
		'trackers_count':trackers_count,
		'page_type':'track',
		'query':query,
		'mentors': mentors
	}
	return render(request,template_name,ctx)

# 添加跟踪
@aq_required
def add_track(request,): 	
	contact_id = request.GET['contact_id']
	try:
		track = Track.objects.get(message_contact=contact_id)
	except ObjectDoesNotExist:
		message_contact = MessageContact.objects.get(id=contact_id)
		track = Track(message_contact=message_contact,is_track=True,user=request.user)
		track.save()
	track.is_track = True
	track.save()
	return ajax_ok('添加跟踪成功')

# 取消跟踪
@aq_required
def cancle_track(request,):
	contact_id = request.GET['contact_id']	
	try:
		track = Track.objects.get(message_contact=contact_id)
	except ObjectDoesNotExist:
		return ajax_error('取消失败')
	track.is_track = False
	track.save()
	return ajax_ok('已取消跟踪')

# 对话记录页
@aq_required
def history(request,user_id,to_user_id,template_name="aq/history.html"): 	
	if request.method == 'GET':
		userid = user_id
		to_userid = to_user_id		

		user = get_object_or_404(User,id=userid)
		to_user = get_object_or_404(User,id=to_userid)

		conversation = Message.objects.get_conversation_between(to_user,user)

		# 分页
		conversation,query = pagination(request,conversation,10)

		return render(request,template_name,{'conversation':conversation,'user':user})

# 消息保存 
@aq_required
def save_message(request,):
	if request.is_ajax():		
		if request.method == 'POST':
			try:
				parent_id = request.POST['parent_id']
				mentor_id = request.POST['mentor_id']
				body = request.POST['body']

				parent = get_object_or_404(User,id=parent_id)
				mentor = get_object_or_404(User,id=mentor_id)
				#验证工作

				#添加会话
				mes = Message.objects.send_message(mentor,[parent],body)

				#运营记录			
				om = OperatorsMessage(user=request.user,message=mes)
				om.save()
				return ajax_ok('消息发送成功')
			except:
				return ajax_error('消息发送失败')

# 更新某个用户的对某人的所有未读消息 
@aq_required
def update_unread_message(request,):
	try:		
		userid = request.GET['userid']
		recipientid = request.GET['recipientid']

		user = get_object_or_404(User,pk=userid)
		recipient = get_object_or_404(User,pk=recipientid)

		# 找到 user 发给 recipient 的消息。
		queryset = Message.objects.filter(Q(sender=user, recipients=recipient,
	                                 messagerecipient__deleted_at__isnull=True))
	    
		message_pks = [m.pk for m in queryset]
	    
	    # 更新 user 发给 recipient 的未读消息
		unread_list = MessageRecipient.objects.filter(message__in=message_pks,
	                                                  user=recipient,
	                                                  read_at__isnull=True)
		now = get_datetime_now()
		unread_list.update(read_at=now)
		return ajax_ok('消息发送成功')
	except:
		return ajax_error('消息发送失败')
    
def get_unread_mentor_count():
	mentors = Mentor.objects.all()
        mentor_id_list = [mentor.user_id for mentor in mentors]    
        # 取得跟导师的对话的人
        to_mentor_conversation = MessageContact.objects.filter(Q(from_user__in=mentor_id_list))
        
        # 筛选出最后一次回复是家长的对话,并构建数据
        mes = []
        
        for c in to_mentor_conversation:
            # 得到最后一条消息->会话以导师的角度为准
            conversation = Message.objects.get_conversation_between(c.from_user,c.to_user)[:3]    
            last_message = conversation[0]
        
            if not last_message.sender.pk in mentor_id_list:
        
                user = c.to_user
                to_user = c.from_user
        
                try:
                    is_track = c.mentor_track.is_track
                except:
                    is_track = False
            
                mes.append({
                        'contact_id':c.id,
                        'user':user,
                        'to_user':to_user,
                        'last_message':last_message,
                        'conversation':conversation,
                        'is_track':is_track,
                        'unread_num': MessageRecipient.objects.count_unread_messages_between(to_user,user)
                })
        mes_count = len(mes)
        return mes_count
			