from models import UserWord, UserProgress, Level, Word, Score
from django.db import connection

def current_words(userprogress):
    return Word.objects.filter(level = userprogress.current_level)
    
def get_level_percent(user):
    words = current_words(user.userprogress)
    userwords = get_or_create_userwords(words,user)

    # Handle case with 0 words
    if not len(words):
        return 0

    skill = sum([userword.skill for userword in userwords])
    possible_skill = 100 * len(userwords)

    return int(float(skill) / possible_skill * 100)

def get_or_create_userwords(words, user):
    # Grab the existing userwords
    userwords = list(UserWord.objects.filter(word__in = words,user=user))

    # Figure out which words have no userwords
    userword_words = [userword.word for userword in userwords]
    not_in = [word for word in words if word not in userword_words]

    # Create new userwords
    new_userwords = []
    for word in not_in:
        userword = UserWord(user = user, word = word)
        userword.save()
        new_userwords.append(userword)

    # Return both the retrieved and created userwords
    return userwords + new_userwords

# Gets the current user progress or creates a new one
def get_user_progress(user):
    (user_progress, created) = UserProgress.objects.get_or_create(
        user=user, 
        defaults = {
            "current_level":Level.objects.get(number=1)
        })
    if created:
        level_up(user_progress, new=True)

    return user_progress

def can_level_up(user):
    # Get words
    userwords = UserWord.objects.filter(
            word__level = user.userprogress.current_level,
            user = user)

    return all([userword.skill > 90 for userword in userwords])


def level_up(user_progress, new=False):
    if not new:
        try:
            # Find next level, assumes level pks are sequential
            next_level = Level.objects.get(
                    number = user_progress.current_level.number + 1)

            # Update
            user_progress.current_level = next_level
            user_progress.save()
        except Level.DoesNotExist:
            # Level maxed out
            return False

    # Create new userwords
    get_or_create_userwords(
            words = user_progress.current_level.word_set.all(),
            user = user_progress.user)

    return True

def score_rank_personal(level_id, game_id, user_id, score):
    cursor = connection.cursor()
    cursor.execute('''
        select count(*)
        from vocab_score
        where 
            vocab_score.level_id = %s AND
            vocab_score.game_id = %s AND
            vocab_score.user_id = %s AND
            vocab_score.score >= %s 
        ''',[level_id, game_id, user_id, score])

    return cursor.fetchone()[0]


def score_rank_friends(level_id, game_id, user_id, score):
    cursor = connection.cursor()
    cursor.execute('''
        select count(*)
        from vocab_score
        left outer join accounts_userfriend
            ON vocab_score.user_id = accounts_userfriend.friend_id 
        where
            (accounts_userfriend.user_id = %s OR
            vocab_score.user_id = %s)
            AND
            vocab_score.game_id = %s AND
            vocab_score.level_id = %s AND
            vocab_score.score >= %s
        ''', [user_id, user_id, game_id, level_id, score])

    return cursor.fetchone()[0]


def high_scores_personal(game, level, user, top):
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
        LIMIT %s
        ''',[game.id,level.id,user.id,top])
    return scores

def high_scores_friends(game, level, user, top):
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
        left outer join accounts_userfriend
            ON auth_user.id = accounts_userfriend.friend_id
        where
            vocab_score.game_id = %s and
            vocab_score.level_id = %s and
              (accounts_userfriend.user_id = %s or
               vocab_score.user_id = %s)
        ORDER BY score DESC
        LIMIT %s
        ''',[game.id,level.id,user.id,user.id,top])

    return scores

def annotated_score(score):
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
            vocab_score.id = %s
        LIMIT 1
        ''',[score.id])
    return scores[0]


