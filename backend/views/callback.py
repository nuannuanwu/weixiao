# -*- coding: utf-8 -*-
from soaplib.core.model.primitive import Boolean, String
from soaplib.core.service import DefinitionBase, rpc, soap
from soaplib.core.model.primitive import String, Integer
from soaplib.core.server import wsgi
from soaplib.core.model.clazz import Array

from soaplib.core import Application
from soaplib.core.server.wsgi import Application as WSGIApplication
from django.http import HttpResponse

from sms.models import SmsNotifyStatus,SmsReceipt,SmsReceive

class DjangoSoapApp(WSGIApplication):
    """
    Generic Django view for creating SOAP web services (works with soaplib 2.0)

    Based on http://djangosnippets.org/snippets/2210/
    """

    csrf_exempt = True

    def __init__(self, services, tns):
        """Create Django view for given SOAP soaplib services and tns"""

        return super(DjangoSoapApp, self).__init__(Application(services, tns))

    def __call__(self, request):
        django_response = HttpResponse()

        def start_response(status, headers):
            django_response.status_code = int(status.split(' ', 1)[0])
            for header, value in headers:
                django_response[header] = value

        response = super(DjangoSoapApp, self).__call__(request.META, start_response)
        django_response.content = '\n'.join(response)

        return django_response

# the class with actual web methods
class MySOAPService(DefinitionBase):
    @rpc(String, String, _returns=Boolean)
    def Test(self, f1, f2):
        return True
    @rpc(String, _returns=String)
    def HelloWorld(self, name):
        return 'Hello %s!' %name

    @soap(String,Integer,_returns=Array(String))
    def say_hello(self,name,times):
        results = []
        for i in range(0,times):
            results.append('Hello, %s'%name)
        return results
    
    # 记录到 mongo 短信是否成功发送到 宽乐通信 的平台
    @soap(Integer,String,String,String)
    def NotifyStatus(self,eventID,sessionID,res,para1):
        #if para1:
        u1=SmsNotifyStatus(eventID=eventID,sessionID=sessionID,res=res,para1=para1)  
        u1.save()
        
    # 记录到 mongo 短信是否成功发送到 用户手机 
    @soap(String,String,Integer,Integer,String)
    def EchoOfSendSMS(self,ucNum, cee, msgid, res,recvt):
        data_json = {'ucNum':ucNum,'cee':cee,'msgid':msgid,'res':res,'recvt':recvt}
        u1=SmsReceipt(ucNum=ucNum,cee=cee,msgid=msgid,res=res,recvt=recvt)  
        u1.save()  
        
    # 记录到 mongo
    @soap(String,String,String,String)
    def RecvSMS(self,caller,ucNum,cont,time):
        print caller,ucNum,cont,time,'*********************************************************************'
        data_json = {'send_mobile':caller,'receive_mobile':ucNum,'content':cont,'receive_date':time}
        u1=SmsReceive(send_mobile=caller,receive_mobile=ucNum,content=cont,receive_date=time)  
        u1.save()  
        return 0


sms_soap_callback = DjangoSoapApp([MySOAPService], 'weixiao178.com')

from django.http import HttpResponse
def test(request): 
    result = "total push message:"+str(count)
    return HttpResponse(result)
