import time
from django.http import HttpResponse
from django.shortcuts import render

from .worker import data


def index(request):
    print(request)
    contents = dict(
        currentTime=time.ctime()
    )
    return render(request, 'index.html', contents)


def query(request, pinYin):
    print(request)
    found = data.query(pinYin)
    found.index = range(len(found))
    return HttpResponse(found.to_json(), content_type='application/json')


def guess(request, zi):
    print(request)
    found = data.guess(zi)
    found.index = range(len(found))
    return HttpResponse(found.to_json(), content_type='application/json')
