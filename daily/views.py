# -*- coding:utf-8 -*-
import local_settings
import wechater
from django.shortcuts import render_to_response
from django.http import HttpResponse, HttpResponseRedirect, HttpRequest
from WXBizMsgCrypt import WXBizMsgCrypt

import xml.etree.cElementTree as xmlTree

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
        msg_tree = xmlTree.fromstring(msg)
        msg_type = msg_tree.find("MsgType").text
        print msg_type
        if msg_type == "image":
            msg_image = msg_tree.find("PicUrl").text
            print msg_image
        elif msg_type == "text":
            content = msg_tree.find("Content").text
            print content
        return HttpResponse()