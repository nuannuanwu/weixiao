#!/usr/bin/env python
# -*- coding: utf8 -*-
import hashlib
import base64
import time
import datetime



#from SOAPpy import SOAPProxy
from suds.client import Client

class send:
    def __init__(self):
        self.register_wsdl = "http://202.105.212.146:8080/jboss-net/services/Register?wsdl"
        self.sendsms_wsdl = "http://202.105.212.146:8080/jboss-net/services/SendSMS?wsdl"
        #self.register_wsdl = "http://192.168.1.222:8080/jboss-net/services/Register?wsdl"
        #self.sendsms_wsdl = "http://192.168.1.222:8080/jboss-net/services/SendSMS?wsdl"
        self.callback_url = 'http://42.120.19.124/backend/callback/sms/?wsdl'


        
        self.connid = ""
        self.rand = ""
        self.pw = ""         
    
    #获取注册链接
    def getClient(self):
        register_client = Client(self.register_wsdl).service
        #register_client = SOAPProxy(self.register_wsdl)
        return register_client

    #获取注册链接
    def getSmsClient(self):
        sendsms_client = Client(self.sendsms_wsdl)
        #sendsms_client = SOAPProxy(self.sendsms_wsdl)
        return sendsms_client


    #md5加密
    def md5(self,string):
        m=hashlib.md5(string)
        m.digest()
        return m.hexdigest()

    #密码生成
    def setpw(self,rand,pw):
        return self.md5(str(rand)+pw+pw)        

    #调用sendSMS
    def sendMessage(self,user,pw,rand,callee,back,msg,msgid,connid):
        connid = str(connid)
        rand = str(rand)
        print 'user',type(user),user
        print 'pw',type(pw),pw
        print 'rand',type(rand),rand
        print 'callee',type(callee),callee
        print 'back',type(back),back
        print 'msg',type(msg),msg
        print 'msgid',type(msgid),msgid
        print 'connid',type(connid),connid

        # for suds / sae 使用soap时出现问题！！！！
        client = self.getSmsClient()
        array = client.factory.create('ns1:Array') 
        array.item = callee

        status = client.service.sendSMS(user,pw,rand,array,back,msg,msgid,connid)
        return status

    #短信发送
    def send(self,user,pw,callee,back,msg,msgid):
        #预处理字符串
        
        msg=base64.encodestring(msg)
        print "s1"
        if self.connid == "": 
            #短信发送开始
            print "0"
            client = self.getClient()
            print "1111111"
            rand = client.getRandom()
            print "222222"
            pw = self.setpw(rand,pw)  
            print "333333"
            
            print user,pw,rand,self.callback_url,"========================="
            connid = client.setCallBackAddr(user,pw,rand,self.callback_url)
            
            if connid < 0:   
                client = self.getClient()
                rand = client.getRandom()
                pw = self.setpw(rand,pw)
                connid = client.setCallBackAddr(user,pw,rand,self.callback_url)
            	
            #二次取得随机数
            #client2 = self.getClient()
            #rand = client2.getRandom()
            #pw = self.setpw(rand,pw)
            
            self.rand = rand
            self.connid = connid
            self.pw = pw
        print "==============789"
        print self.rand
        print self.pw        
        print self.connid
 
        return self.sendMessage(user,self.pw,self.rand,callee,back,msg,msgid,self.connid)


    #获取发送列表
    def getSendList(self):
        
        now_time = str(datetime.datetime.now())      
        #从sms库获得未发送数据
        find_json = { "sms_time":{ "$lt": now_time } ,"is_del" : 0,"is_deal" : 0}
        find_json = { "is_del" : 0,"is_deal" : 0,"receive_mobile":"13725503249","sms_time": "2012-03-31 15: 10: 00"}
        #records = db.sms.find(find_json).sort("_id").limit(50) #查询一条
        records = db.sms_send.find(find_json).sort("sms_time").limit(200) #查询
        count = records.count()
        
        if count == 0:
            print "there is no sms to gateway,waitting..."
            return 0
        else:
            for record in records:

                sms_send_pk = record['_id']
                msgid=str(sms_send_pk)          
                msgid = msgid[-6:]
                msgid = int(msgid)

                print msgid
                #return True
                callee=[record['receive_mobile']]
                print callee
                user= str(record['send_mobile'])
                pw='201002'
                msg = record['sms_content'].encode('UTF8')
                
                back='1'
                result = self.send(user,pw,callee,back,msg,msgid)
                try:
                    result = self.send(user,pw,callee,back,msg,msgid)
                except (KeyboardInterrupt, MemoryError):
                    raise

                except:
                    print "socket.error: (104, 'Connection reset by peer')"
                    continue
                print send
                if result == "-5" or result == "-7":
                    self.connid = ""
                    #sql="update " +table+ " set deal_status="+result+" where msg_id = "+ str(msgid)
                    
                    update_json = {"is_deal":1,'receipt_status':result}    
                else:
                    #sql="update " +table+ " set send_status='1',deal_status="+result+" where msg_id = "+ str(msgid)
                    
                    update_json = {"is_deal":1,"send_status":1,'receipt_status':result}    
                print update_json
                print "=============="
                db.sms_send.update({"_id":sms_send_pk},{"$set":update_json})
        return 1
            

    #获取当前月份
    def getMonth(self):
        return time.strftime('%Y%m',time.localtime(time.time()))
        
        

if __name__ == "__main__":
    m = send()
    running = True
    running = True
    sleep_time = 1
    max_time = 5
    while running:
        status = m.getSendList()
        if(status == 0):
            if sleep_time < max_time:
                sleep_time += 1
        else:
            sleep_time = 0

        print "sleeping :",str(sleep_time)
        time.sleep(sleep_time)

