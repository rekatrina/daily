# -*- coding:utf-8 -*-
import local_settings
import wechater
from django.shortcuts import render_to_response
from django.http import HttpResponse, HttpResponseRedirect, HttpRequest
from WXBizMsgCrypt import WXBizMsgCrypt

import xml.etree.cElementTree as xmlTree

import urllib
import urllib2
import base64
import re
from sgmllib import SGMLParser
import smtplib
from email.mime.text import MIMEText
import sqlite3
import datetime
import time
import threading
import json

def wechat_request(request):
    wxcpt = WXBizMsgCrypt(local_settings.token_recall, local_settings.aeckey_recall, local_settings.corpid)
    signature = request.GET.get('msg_signature')  # Request 中 GET 参数 signature
    timestamp = request.GET.get('timestamp')  # Request 中 GET 参数 timestamp
    nonce = request.GET.get('nonce')

    if request.method == 'GET':
        echoStr = request.GET.get('echostr')
        # print nonce
        #  print signature
        #  print timestamp
        #  对签名进行校验
        ret, sEechoStr = wxcpt.VerifyURL(signature, timestamp, nonce, echoStr)
        print sEechoStr
        if(ret != 0):
            print "ERR: Verify ret: " + bytes(ret)
            return HttpResponse()
        else:
            return HttpResponse(sEechoStr)

    else:
        postMsg = request.body
        ret, msg = wxcpt.DecryptMsg(postMsg, signature, timestamp, nonce)
        if(ret != 0):
            print "ERR: DecryptMsg" + bytes(ret)
            return HttpResponse("")
        # fp = open("E:\log.txt","w")
        # fp.write(msg)
        # fp.close
        print msg
        msg_tree = xmlTree.fromstring(msg)
        msg_type = msg_tree.find("MsgType").text
        msg_from = msg_tree.find("FromUserName").text
        msg_to = msg_tree.find("ToUserName").text
        msg_time = msg_tree.find("CreateTime").text
        print msg_from
        print msg_type

        if msg_type == "image":
            msg_image = msg_tree.find("PicUrl").text
            print msg_image
        elif msg_type == "text":
            content = msg_tree.find("Content").text
            print content
            msg_back  = "不要再说话啦！ 这里没有做好！！"

            tpl = '''<xml>
            <ToUserName>''' + msg_from + '''</ToUserName>
            <FromUserName>''' + msg_to + '''</FromUserName>
            <CreateTime>''' + msg_time + '''</CreateTime>
            <MsgType><![CDATA[text]]></MsgType>
            <Content><![CDATA['''+ msg_back +''']]></Content>
            </xml>'''
            after = wxcpt.EncryptMsg(tpl, nonce)
            return HttpResponse(after)
            # send_wechat_msg("别说话！ 这里还没做好！", msg_from)

        elif msg_type == "event":
            eventKey = msg_tree.find("EventKey").text
            print eventKey
            msg_back = wechat_cmd(eventKey)

            tpl = '''<xml>
            <ToUserName>''' + msg_from + '''</ToUserName>
            <FromUserName>''' + msg_to + '''</FromUserName>
            <CreateTime>''' + msg_time + '''</CreateTime>
            <MsgType><![CDATA[text]]></MsgType>
            <Content><![CDATA['''+ msg_back +''']]></Content>
            </xml>'''
            after = wxcpt.EncryptMsg(tpl, nonce)
            return HttpResponse(after)

        return HttpResponse()


def get_dhcp_page():
    print 1;
    login_user = 'admin'
    login_pw = 'password'
    url = local_settings.url
    auth = 'Basic' + base64.b64encode(login_user + ':' + login_pw)
    heads = local_settings.heads
    request = urllib2.Request(url, None, heads)
    response = urllib2.urlopen(request)
    cont = response.read()
    return cont


def get_dhcp_list(cont):
    print 2;
    pattern = r'DHCPDynList=new Array\((.*?)\);'

    tmp = re.findall(pattern, cont, flags=re.DOTALL)
    list = re.findall('"(.*?)"', tmp[0])
    user_list = []
    time_list = []
    for iter in range(0,len(list)/4):
        user_list.append(list[4*iter])
        time_list.append(list[4*iter+3])
    return [user_list, time_list]


def send_mail(to_list,content):
    mail_host = local_settings.mail_host
    mail_user = local_settings.mail_user
    mail_pw = local_settings.mail_pw
    current = datetime.datetime.now()
    me = 'Daily<'+mail_user+'>'
    msg = MIMEText(content, _subtype='plain')
    msg['Subject'] = 'Daily report %s'%(datetime.datetime.now().strftime("%m-%d"))
    msg['From'] = me
    msg['To'] = to_list
    try:
        server = smtplib.SMTP()
        server.connect(mail_host)
        server.login(mail_user,mail_pw)
        server.sendmail(me,to_list,msg.as_string())
        server.close()
        print 'send to '+ to_list
        return True
    except Exception, e:
        print e
        return False

def get_token():
    values = {'corpid': local_settings.corpid, 'corpsecret': local_settings.corpsecret}
    url = "https://qyapi.weixin.qq.com/cgi-bin/gettoken?corpid="\
          + values['corpid'] + "&corpsecret=" + values['corpsecret']
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/46.0.2490.80 Safari/537.36"}
    urlreq = urllib2.Request(url=url, headers=headers)
    #response = urllib2.urlopen(url).read()
    response = urllib2.urlopen(urlreq).read()
    token_info = json.loads(response)
    print 'we get token as:'
    print token_info['access_token']
    return token_info['access_token']

def send_wechat_msg(msg, toUser):
    url = "https://qyapi.weixin.qq.com/cgi-bin/message/send?access_token=" + get_token()
    post_data ={}
    msg_content = {}
    msg_content["content"] = msg
    post_data["touser"] = toUser #"ludage|rekatrina" ##ludage|
    post_data["msgtype"] = "text"
    post_data["agentid"] = 1
    post_data["safe"] = "0"
    post_data["text"] = msg_content
    jdata = json.dumps(post_data,  ensure_ascii=False)
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/46.0.2490.80 Safari/537.36"}
    urlreq = urllib2.Request(url=url, headers=headers, data=jdata)
    req = urllib2.urlopen(url, jdata)
    print req.read()
    return req

class checker(threading.Thread):
    msg_ = ""
    to_ = ""
    def __init__(self, msg = "", to = ""):
        threading.Thread.__init__(self)
        msg_ = msg
        to_ = to
        pass

    def run(self):
        cont = get_dhcp_page()
        [user, time_list] = get_dhcp_list(cont)
        time.sleep(1)
        send_wechat_msg(self.msg_, self.to_)

def wechat_cmd(msg_cmd):
    if msg_cmd == "online":
        [user_list, time_list] = get_dhcp_list(get_dhcp_page())
        content = "\n".join(user_list)
        return content
    elif msg_cmd == "chifan":
        return "点个鸡毛！ 赶紧出来吃饭"

if __name__ == '__main__':
    send_wechat_msg("test", "rekatrina")