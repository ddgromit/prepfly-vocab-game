from django.shortcuts import render
from django.contrib.auth import logout
from django import http

def login_handler(request):
    return http.HttpResponseRedirect('/login/facebook/')


def logout_handler(request):
    logout(request)
    return http.HttpResponseRedirect('/')
