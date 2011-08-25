from datetime import datetime, timedelta
from django.http import Http404, HttpResponseForbidden, HttpResponseRedirect
from django.shortcuts import render
from django.utils import simplejson
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from social_auth.models import UserSocialAuth
import settings
from jsonifiers import current_words_json
from lib import get_level_percent, get_user_progress

@login_required
def vocab_home(request,fb=False):
    level_number = get_user_progress(request.user).current_level.number
    percent = get_level_percent(request.user)
    bar_width = max(int(226 * (percent/100.0)),2)
    xp = int(percent)

    try: 
        socialauth = UserSocialAuth.objects.get(user=request.user,provider='facebook')
        
        # Your own access token
        access_token = socialauth.extra_data['access_token']

        # Get users who are friends who logged in < 2 days ago
        day_ago = datetime.now() - timedelta(days=1)
        friends = User.objects.filter(userfriend__friend = request.user,
                last_login__gt = day_ago)

        # Get their uids
        fb_friends = UserSocialAuth.objects.filter(user__in = friends, provider =
                'facebook')
        uids = [friend.uid for friend in fb_friends]

    except UserSocialAuth.DoesNotExist:
        access_token = None
        uids = []

    template = "vocab_home.html" if not fb else "vocab_home_facebook.html"

    return render(request, template, {
        'level_number':level_number,
        'percent':percent,
        'bar_width':bar_width,
        'access_token':access_token,
        'uids':uids,
        'xp':xp,
        'logged_in':True,
    })

def vocab_home_facebook(request):
    return vocab_home(request, fb=True)

def facebook_home(request):
    if request.user.is_authenticated():
        return HttpResponseRedirect('/vocab/')
    return render(request,"vocab_home_facebook.html", {
        'level_number':1,
        'percent':1,
        'bar_width':30,
        'access_token':"",
        'uids':[],
        'xp':0,
        'logged_in':False,
    })

@login_required
def game(request,game_id,fb=False):
    try: 
        socialauth = UserSocialAuth.objects.get(user=request.user,provider='facebook')
        access_token = socialauth.extra_data['access_token']
    except UserSocialAuth.DoesNotExist:
        access_token = None

    template = "vocab_game.html" if not fb else "vocab_game_facebook.html"

    return render(request, template, {
        'words_json':simplejson.dumps(current_words_json(request.user)),
        'game_id':game_id,
        'level_id':request.user.userprogress.current_level.id,
        'access_token':access_token,
        'FACEBOOK_APP_ID':settings.FACEBOOK_APP_ID,
    })

def game_facebook(request,game_id):
    return game(request,game_id,fb=True)


def iframetest(request):
    return render(request,"iframetest.html")
