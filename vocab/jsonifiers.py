from models import Word, Definition, Level, UserWord
from lib import get_user_progress, get_or_create_userwords, current_words
from social_auth.models import UserSocialAuth

"""
{
    id: 1
    word:'whatup'
    skill: 87
    current: True
    definitions: []
        text: 'Something'
}
"""
def current_words_json(user):
    progress = get_user_progress(user)

    # Get level words
    words = current_words(progress)

    # UserWords for this level
    userwords = get_or_create_userwords(words,user)

    # Definitions
    definitions = Definition.objects.filter(word__in = words)

    # Create the resulting object
    json = []
    for word in words:
        userword = [userword for userword in userwords if userword.word == word][0]
        defs = [definition for definition in definitions if definition.word == word]
        def def_to_json(defn):
            return {
                "id":defn.id,
                "text":defn.text,
            }
        defs_json = [def_to_json(defn) for defn in defs]
        json.append({
            'id':word.id,
            'word':word.text,
            'skill':userword.skill,
            'current':True,
            'definitions':defs_json,
        })
    return json

"""
{
    id:1
    rank:2
    score:2700
    name:"Derek Dahmer"
    fb_uid:648434
}
"""
def scores_json(scores):
    rank = 1
    scores_json = []
    for score in scores:
        scores_json.append({
            "id":score.id,
            "rank":rank,
            "score":score.score,
            "name":"%s %s." % (score.first_name, score.last_name[:1]),
            "fb_uid":score.fb_uid,
        })
        rank = rank + 1

    return scores_json

# Doesn't require an annotated score
def score_json(score, user, rank):
    try:
        uid = user.social_auth.get(provider='facebook').uid
    except UserSocialAuth.DoesNotExist:
        uid = None

    return {
        "id":score.id,
        "rank":rank,
        "score":score.score,
        "name":"%s %s." % (user.first_name, user.last_name[:1]),
        "fb_uid":uid,
    }

