#!/usr/bin/env python
# -*-coding: utf8 -*-

"""Task Queue API
TaskQueue is a distributed task queue service provided by SAE for developers as
a simple way to execute asynchronous user tasks.

Example:

1. Add a GET task.
    
    from sae.taskqueue import Task, TaskQueue

    queue = TaskQueue('queue_name')
    queue.add(Task("/tasks/cd"))

2. Add a POST task.

    queue.add(Task("/tasks/strip", "postdata"))

3. Add a bundle of tasks.

    tasks = [Task("/tasks/grep", d) for d in datas]
    queue.add(tasks)

4. A simple way to add task.

    from sae.taskqueue import add_task
    add_task('queue_name', '/tasks/fsck', 'postdata')
"""

__all__ = ['Error', 'PushSeverConnecttionError', 'PushSeverPermissionDeniedError', 
           'CertificateNumError', 'CertificateNotExistsError', 'CertificatePushToQueueError', 
           'ApnsTokenNotExistsError', 'ApnsTokenFormatError', 'UnknownError', 
           'InvalidApnsError', 'push', 'Apns']

import os
import time
import json
import urllib
import urllib2
import urlparse
import base64

import random
import string
from sae import (const, util)

def http_build_query(params, topkey = ''):
    from urllib import quote

    if len(params) == 0:
        return ""

    result = ""

    # is a dictionary?
    if type (params) is dict:
        for key in params.keys():
            newkey = quote (key)
            if topkey != '':
                newkey = topkey + quote('[' + key + ']')

            if type(params[key]) is dict:
                result += http_build_query (params[key], newkey)

            elif type(params[key]) is list:
                i = 0
                for val in params[key]:
                    result += newkey + quote('[' + str(i) + ']') + "=" + quote(str(val)) + "&"
                    i = i + 1

            # boolean should have special treatment as well
            elif type(params[key]) is bool:
                result += newkey + "=" + quote (str(int(params[key]))) + "&"

            # assume string (integers and floats work well)
            else:
                result += newkey + "=" + quote (str(params[key])) + "&"

    # remove the last '&'
    if (result) and (topkey == '') and (result[-1] == '&'):
        result = result[:-1]

    return result
        
class Error(Exception):
    """Base-class for all exception in this module"""

class InternalError(Error):
    """There was an internal error while accessing this queue, it should be 
    temporary, it problem continues, please contact us"""
    
class PushSeverConnecttionError(Error):
    """The task's url, payload, or options is invalid"""

class PushSeverPermissionDeniedError(Error):
    """authorize faild"""

class CertificateNumError(Error):
    """certificate number error"""

class CertificateNotExistsError(Error):
    """certificate does not exist"""

class CertificatePushToQueueError(Error):
    """error when pushing to the queue"""

class ApnsTokenNotExistsError(Error):
    """client token can not be empty"""

class ApnsTokenFormatError(Error):
    """invalid format of client token"""

class UnknownError(Error):
    """unknown error"""

class InvalidApnsError(Error):
    """Either the taskqueue is Full or the space left's not enough"""


_ERROR_MAPPING = {
    1: PushSeverConnecttionError, 
    2: PushSeverPermissionDeniedError, 
    3: CertificateNumError, 
    4: CertificateNotExistsError,
    5: CertificatePushToQueueError,
    6: ApnsTokenNotExistsError,
    7: ApnsTokenFormatError,
    8: UnknownError,
    9: InvalidApnsError
    }
"""
 *  - errno: 0        成功
 *  - errno: -1        PUSH服务器数据库不能连接
 *  - errno: -2        权限不足，即accesskey参数有错
 *  - errno: -3        证书序号错误，即num参数有错
 *  - errno: -4        证书不存在
 *  - errno: -5        消息进入推送队列出错
 *  - errno: -6        推给的用户Iphone的token错误，即client参数为空
 *  - errno: -7        推给的用户Iphone的token错误，即client参数格式不正确
 *  - errno: -8        未知错误
"""
_APNS_BACKEND = 'http://push.sae.sina.com.cn/api.php'

class Apns:

    def __init__(self, cert_id = None, body = None, force_ssl_command = False, debug_ssl = False):

        self.access_key = const.ACCESS_KEY
        self.secret_key = const.SECRET_KEY
        self.cert_id = cert_id
        pass


    def push(self,cert_id,body,device_token):
        """
        /**
         * 推送消息
         * 
         * @param int $cert_id  许可证序号
         * @param array $body 消息体（包括消息、提醒声音等等），格式请参考示例和{@link http://developer.apple.com/library/ios/#documentation/NetworkingInternet/Conceptual/RemoteNotificationsPG/ApplePushService/ApplePushService.html#//apple_ref/doc/uid/TP40008194-CH100-SW1 Apple官方文档}
         * @param string $device_token 设备令牌
         * @return bool 成功返回true，失败返回false.
         * @author Elmer Zhang
         */
         """
        print body,"=========="
        if not body.has_key('alert'):
            raise InvalidApnsError()

        url = _APNS_BACKEND+"?cert_id="+str(cert_id)+"&device_token="+str(device_token)
        print url,"======"
        req = urllib2.Request(url)

        req.unredirected_hdrs.update(self._get_headers())



        body = {'aps':body}
        payload = urllib.urlencode(body)
        #return payload

        body = {"aps":{"alert":"99999999"}}
        data = {"body" : body } 


        payload = urllib.urlencode(data)
        #payload = payload.replace('+','')



        try:
            rep = urllib2.urlopen(req, payload, 5)
        except urllib2.URLError:
            raise InternalError()

        return rep.read()
        if rep.code == 200:
            body = rep.read()
            #print body

            try:
                rc = json.loads(body)
            except TypeError:
                raise InternalError()

            #rc = json.loads(rep.read())
            if rc.has_key('errno'):
                errno = rc['errno']
                if errno == 0:
                    if rc.has_key('data'):
                        return rc['data']
                    else:
                        return True
                else:
                    error_klass = _ERROR_MAPPING.get(errno, None)
                    if error_klass:
                        raise error_klass()
                    else:
                        raise Error(body)
            else:
                raise InternalError()
        else:
            raise InternalError()


        print _APNS_BACKEND,'aaaaaaaa'
        return info

    def _get_headers(self):
        timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
        msg = 'ACCESSKEY' + self.access_key + 'TIMESTAMP' + timestamp
        headers = {'TimeStamp': timestamp,
                   'AccessKey': self.access_key,
                   'Signature': util.get_signature(self.secret_key, msg)}

        return headers

