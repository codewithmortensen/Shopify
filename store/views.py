from django.shortcuts import render
from django.http import HttpResponse


def store(request):
    return HttpResponse('thi is the store app')
