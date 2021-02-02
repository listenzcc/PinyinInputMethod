import time
from django.http import HttpResponse
from django.shortcuts import render

from .worker import data
from .tools import split_words

from WeChatOperator.script import WeChatOperator

wco = WeChatOperator()


def index(request):
    print(request)
    contents = dict(
        currentTime=time.ctime()
    )
    return render(request, 'index.html', contents)


def query(request, pinYin):
    print(request, pinYin)
    found = data.query(pinYin)
    found.index = range(len(found))
    return HttpResponse(found.to_json(), content_type='application/json')


def guess(request, zi):
    print(request, zi)
    found = data.guess(zi)
    found.index = range(len(found))
    return HttpResponse(found.to_json(), content_type='application/json')


def split(request, sentence):
    print(request, sentence)
    split = split_words(sentence)
    return HttpResponse(split.to_json(), content_type='application/json')


def sendMessage(request, message):
    print(request, message)
    wco.write_message(message)
    return HttpResponse('{"state": "OK"}', content_type='application/json')


def wechat(request, command):
    print(request, command)
    if command == 'display':
        wco.display_wechat()
    return HttpResponse('{"state": "OK"}', content_type='application/json')
