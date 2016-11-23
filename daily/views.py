# -*- coding:utf-8 -*-
import local_settings
import wechater
from django.shortcuts import render_to_response
from django.http import HttpResponse, HttpResponseRedirect, HttpRequest
from WXBizMsgCrypt import WXBizMsgCrypt

def checkout(request):
    signature = request.GET.get('msg_signature')  # Request 中 GET 参数 signature
    timestamp = request.GET.get('timestamp')  # Request 中 GET 参数 timestamp
    nonce = request.GET.get('nonce')
    echoStr = request.GET.get('echostr')
    # print nonce
    # print signature
    # print timestamp
    # 对签名进行校验
    wxcpt = WXBizMsgCrypt(local_settings.token_recall, local_settings.aeckey_recall, local_settings.corpid)
    ret, sEechoStr = wxcpt.VerifyURL(signature, timestamp, nonce, echoStr)
    print sEechoStr
    if(ret != 0):
        print "ERR: Verify ret: " + bytes(ret)
        return HttpResponse("error!!")
    else:
        return HttpResponse(sEechoStr)