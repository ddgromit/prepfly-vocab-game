from django.utils import simplejson
from django.contrib.auth.decorators import login_required
from library import request_decorators as reqdecs
from models import *
from social_auth.models import UserSocialAuth
from jsonifiers import current_words_json, scores_json, score_json
from lib import get_or_create_userwords, get_user_progress, level_up, \
    can_level_up, score_rank_personal, score_rank_friends, \
    high_scores_personal, annotated_score, high_scores_friends


"""
INPUT:
[{
    wordId:1
    skill:87
}]

"""
@reqdecs.brocab_json_request
@login_required
@reqdecs.json_in_body
def update_skills_handler(request, reqObj):
    user = request.user

    # Get the words
    word_to_skills = {}
    words = []
    for entry in reqObj:
        # Validate
        wordId = int(entry['wordId'])
        word = Word.objects.get(id=wordId)
        words.append(word)

        skill = max(0,min(100,int(entry['skill'])))
        word_to_skills[word] = skill

    # Get userwords
    userwords = get_or_create_userwords(words=words,user=user)

    # Update
    for userword in userwords:
        # Get and update UserWord
        userword.skill = word_to_skills[userword.word]
        userword.save()

    # Check for levelup
    leveled_up = False
    if can_level_up(user):
        leveled_up = level_up(user.userprogress)

    return {
        "leveled_up":leveled_up
    }


### SCORING API ###


@login_required
@reqdecs.brocab_json_request
def add_score(request):
    game = Game.objects.get(id=int(request.GET['game_id']))
    level = Level.objects.get(id=int(request.GET['level_id']))
    score_amount = int(request.GET['score'])
    user = request.user

    score = Score(game=game,level=level,user=user,score=score_amount)
    score.save()


    # Calculate score rank
    personal_rank = score_rank_personal(level.id, game.id, user.id,
            score_amount)
    friend_rank = score_rank_friends(level.id, game.id, user.id, score_amount)

    # Personal high scores
    scores_personal = scores_json(high_scores_personal(game, level, user, 3))
    if not any([score.id == sc['id'] for sc in scores_personal]):
        scores_personal.append(score_json(score, user, personal_rank))
    
    # Friend high scores
    scores_friends = scores_json(high_scores_friends(game, level, user, 3))
    if not any([score.id == sc['id'] for sc in scores_friends]):
        scores_friends.append(score_json(score, user, friend_rank))

    return {
        "id":score.id,
        "personal_rank":personal_rank,
        "friend_rank":friend_rank,
        "personal_high_scores":scores_personal,
        "friends_high_scores":scores_friends,

    }




### HIGH SCORES API ###


@login_required
@reqdecs.brocab_json_request
def user_high_scores(req):
    game = Game.objects.get(id=int(req.GET['game_id']))
    level = Level.objects.get(id=int(req.GET['level_id']))
    user = req.user

    scores = Score.objects.raw('''
        select
            vocab_score.*,
            social_auth_usersocialauth.uid as fb_uid,
            auth_user.first_name as first_name,
            auth_user.last_name as last_name
        from vocab_score
        left join social_auth_usersocialauth
            ON social_auth_usersocialauth.user_id = vocab_score.user_id
        left join auth_user
            ON auth_user.id = vocab_score.user_id
        where
            vocab_score.game_id = %s and
            vocab_score.level_id = %s and
            vocab_score.user_id = %s
        ORDER BY score DESC
        ''',[game.id,level.id,user.id])

    return scores_json(scores)


@login_required
@reqdecs.brocab_json_request
def friend_high_scores(req):
    game = Game.objects.get(id=int(req.GET['game_id']))
    level = Level.objects.get(id=int(req.GET['level_id']))
    user = req.user

    scores = Score.objects.raw('''
        select
            vocab_score.*,
            social_auth_usersocialauth.uid as fb_uid,
            auth_user.first_name as first_name,
            auth_user.last_name as last_name
        from vocab_score
        left join social_auth_usersocialauth
            ON social_auth_usersocialauth.user_id = vocab_score.user_id
        left join auth_user
            ON auth_user.id = vocab_score.user_id
        right join accounts_userfriend
            ON auth_user.id = accounts_userfriend.friend_id
        where
            vocab_score.game_id = %s and
            vocab_score.level_id = %s and
            accounts_userfriend.user_id = %s
        ORDER BY score DESC
        ''',[game.id,level.id,user.id])

    return scores_json(scores)

@login_required
@reqdecs.brocab_json_request
def all_high_scores(req):
    game = Game.objects.get(id=int(req.GET['game_id']))
    level = Level.objects.get(id=int(req.GET['level_id']))
    user = req.user

    scores = Score.objects.raw('''
        select
            vocab_score.*,
            social_auth_usersocialauth.uid as fb_uid,
            auth_user.first_name as first_name,
            auth_user.last_name as last_name
        from vocab_score
        left join social_auth_usersocialauth
            ON social_auth_usersocialauth.user_id = vocab_score.user_id
        left join auth_user
            ON auth_user.id = vocab_score.user_id
        where
            vocab_score.game_id = %s and
            vocab_score.level_id = %s
        ORDER BY score DESC
        ''',[game.id,level.id])


    return scores_json(scores)






### ADMIN API ###


@reqdecs.brocab_json_request
@login_required
def reset_level_handler(request):
    user_progress = get_user_progress(request.user)
    userwords = UserWord.objects.filter(
        user = request.user,
        word__level = user_progress.current_level)
    num_userwords = len(userwords)
    userwords.delete()

    return {
        'message':"Reset %s words on level %s for user %s." %
            (num_userwords,user_progress.current_level.number,request.user)
    }

@reqdecs.brocab_json_request
@login_required
def reset_everything_handler(request):
    # Delete words
    userwords = UserWord.objects.filter(user = request.user).delete()

    # Delete progress (will be regenerated next access)
    get_user_progress(request.user).delete()

    return {
        'message':"Reset successful"
    }



@login_required
@reqdecs.brocab_json_request
def current_words_handler(request):
    if not request.user:
        raise reqdecs.Unauthorized("Not logged in")
    json = current_words_json(request.user)
    return json

