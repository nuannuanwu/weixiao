# -*- coding: utf-8 -*-
from celery.schedules import crontab
from datetime import timedelta

CELERYBEAT_SCHEDULE = {
    #推送apns消息
    # Executes every 5 mins
    'push_tile': {
        'task': 'backend.tasks.push_tile',
        'schedule': crontab(minute='*/5'),
        'args': (),
    },
    #推送未读消息
    # Executes every 30 seconds
    'push_unread_message': {
        'task': 'backend.tasks.push_unread_message',
        'schedule': timedelta(seconds=30),
        'args': (),
    },
    #发送未读消息1
    # Executes every 30 seconds
    'send_unread_message': {
        'task': 'backend.tasks.send_unread_message',
        'schedule': timedelta(seconds=30),
        'args': (),
    },
    #发送紧急消息
    # Executes every 30 seconds
    'send_emergency_message': {
        'task': 'backend.tasks.send_emergency_message',
        'schedule': timedelta(seconds=30),
        'args': (),
    },
      #发送未登录用户紧急消息
    # Executes every 30 seconds
    'send_emergency_message_unlogin': {
        'task': 'backend.tasks.send_emergency_message_unlogin',
        'schedule': timedelta(seconds=30),
        'args': (),
    },
    #发送短信
    # Executes every 20 seconds
    'sms2send': {
        'task': 'backend.tasks.sms2send',
        'schedule': timedelta(seconds=20),
        'args': (),
    },
    #发送短信
    # Executes every 20 seconds
    'sms2gate': {
        'task': 'backend.tasks.sms2gate',
        'schedule': timedelta(seconds=20),
        'args': (),
    },
    #提醒未读导师数据与客服数据
    # Executes every 1 mins
    'send_staff_unread': {
        'task': 'backend.tasks.send_staff_unread',
        'schedule': crontab(minute=12,hour=10, day_of_week='1-5'),
        'args': (),
    },
    #未读食谱
    # Executes everyday at 17 pm
    'send_unread_cookbook': {
        'task': 'backend.tasks.send_unread_cookbook',
        'schedule': crontab(minute=10,hour=17),
        'args': (),
    },
    #给7天未登录，且有未读瓦片的用户发送短信
    # Executes everyday at 17 pm
    'send_user_message': {
        'task': 'backend.tasks.send_user_message',
        'schedule': crontab(minute=10,hour=17),
        'args': (),
    },    
   #发送定时消息
    # Executes every 20 seconds
    'send_timing_message': {
        'task': 'backend.tasks.send_timing_message',
        'schedule': timedelta(seconds=20),
        'args': (),
    },    
    #恢复smssend到队列
    # Executes every 5 mins
    'smssend_set': {
        'task': 'backend.tasks.smssend_set',
        'schedule': crontab(minute='*/5'),
        'args': (),
    }, 
    #短信回复转换到message
    # Executes every 30 seconds
    'smsreceive2message': {
        'task': 'backend.tasks.smsreceive2message',
        'schedule': timedelta(seconds=30),
        'args': (),
    },        
#     'mytest': {
#         'task': 'backend.tasks.mytest',
#         'schedule': timedelta(seconds=10),
#         'args': (1000,),
#     },
}
