# -*- coding: utf-8 -*-
from django.shortcuts import render_to_response, redirect, render, get_object_or_404
from django.contrib.auth.models import User
from django.contrib import messages
from django.utils.translation import ugettext as _
from django.core.exceptions import ObjectDoesNotExist

from waiter.decorators import waiter_required
from waiter.models import WaiterMessage
from kinger.helpers import ajax_ok, ajax_error, pagination
from django.core.urlresolvers import reverse
from django.http import HttpResponse
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.db.models import Q
from kinger.models import Waiter
from userena.contrib.umessages.models import Message, MessageRecipient, MessageContact
from userena.utils import get_datetime_now

# 返回向客服人员提问的问题列表
@waiter_required
def index(request,template_name="waiter/default/index.html"): 

	# 得到筛选的客服人员
	try:
		the_waiter = int(request.GET['waiter'])		
	except:
		the_waiter = ''

	waiters = Waiter.objects.all()
	if the_waiter == '':		
		waiter_id_list = [waiter.user_id for waiter in waiters]	
	else:
		waiter_id_list = [the_waiter]
	
	# 取得跟客服的对话的人
	to_waiter_conversation = MessageContact.objects.filter(Q(from_user__in=waiter_id_list))
	
	# 提问总人数
	askers_count = to_waiter_conversation.count()

	# 筛选出最后一次回复是家长的对话,并构建数据
	mes = []

	for c in to_waiter_conversation:
		# 得到最后一条消息->会话以导师的角度为准
		conversation = Message.objects.get_conversation_between(c.from_user,c.to_user)[:3]	
		last_message = conversation[0]

		if not last_message.sender.pk in waiter_id_list:

			user = c.to_user
			to_user = c.from_user			
		
			mes.append({
					'contact_id':c.id,
					'user':user,
					'to_user':to_user,
					'last_message':last_message,
					'conversation':conversation,					
					'unread_num': MessageRecipient.objects.count_unread_messages_between(to_user,user)
			})
	mes_count = len(mes)

	mes,query = pagination(request,mes,10)	

	return render(request,template_name,{'mes':mes,'mes_count':mes_count,'askers_count':askers_count,'waiters': waiters,'query':query})

# 对话记录页
@waiter_required
def history(request,user_id,to_user_id,template_name="waiter/default/history.html"): 	
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
@waiter_required
def save_message(request,):
	if request.is_ajax():		
		if request.method == 'POST':
			try:
				parent_id = request.POST['parent_id']
				waiter_id = request.POST['waiter_id']
				body = request.POST['body']

				parent = get_object_or_404(User,id=parent_id)
				waiter = get_object_or_404(User,id=waiter_id)
				#验证工作

				#添加会话
				mes = Message.objects.send_message(waiter,[parent],body)

				#客服记录		
				wm = WaiterMessage(user=request.user,message=mes)
				wm.save()
				return ajax_ok('消息发送成功')
			except:
				return ajax_error('消息发送失败')

# 更新某个用户的对某人的所有未读消息
@waiter_required
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
	

def get_unread_waiter_count():
	
	waiters = Waiter.objects.all()
	waiter_id_list = [waiter.user_id for waiter in waiters]    
	# 取得跟客服的对话的人
	to_waiter_conversation = MessageContact.objects.filter(Q(from_user__in=waiter_id_list))
	# 筛选出最后一次回复是家长的对话,并构建数据
	mes = []
	for c in to_waiter_conversation:
	    # 得到最后一条消息->会话以导师的角度为准
	    conversation = Message.objects.get_conversation_between(c.from_user,c.to_user)[:3]    
	    last_message = conversation[0]
	
	    if not last_message.sender.pk in waiter_id_list:
	
	        user = c.to_user
	        to_user = c.from_user            
	    
	        mes.append({
	                'contact_id':c.id,
	                'user':user,
	                'to_user':to_user,
	                'last_message':last_message,
	                'conversation':conversation,                    
	                'unread_num': MessageRecipient.objects.count_unread_messages_between(to_user,user)
	        })
	mes_count = len(mes)
	return mes_count
	


