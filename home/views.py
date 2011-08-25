from django.shortcuts import render
from django.http import HttpResponseRedirect
from django import http
import settings

def homepage(request):
    if request.user.is_authenticated():
        return HttpResponseRedirect(settings.LOGIN_REDIRECT_URL)

    return render(request,"homepage.html", {
            'logged_in':request.user.is_authenticated(),
            'logged_out':not request.user.is_authenticated(),
            'waiting':request.user.is_authenticated(),
        })

def homepage_facebook(request):
    return render(request, "homepage_facebook.html", {
            'logged_in':request.user.is_authenticated(),
            'logged_out':not request.user.is_authenticated(),
            'waiting':request.user.is_authenticated(),
        })

def RedirectToBrocab(request):
    return http.HttpResponseRedirect('/brocab/')

