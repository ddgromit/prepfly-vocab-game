
VOCAB_API_URL = '/vocab/api/'

# Word
# - id
# - word
# - skill
# - skillOriginal
# - current
# - definitions []
# -- text
Word = Backbone.Model.extend {}

Words = Backbone.Collection.extend
    model: Word

    skillUpdateUrl: VOCAB_API_URL + 'update_skills/'

    syncSkills: ->
        changed = @filter (word) -> word.get('skillOriginal') != word.get('skill')
        if GLOBAL.debug
            console.log "Found #{changed.length} words with new skills."

        obj = _(changed).map (word) ->
            return {
                'wordId':word.id,
                'skill':word.get('skill')
            }

        $.ajax
            type:'POST'
            url:@skillUpdateUrl
            dataType:'json'
            data:JSON.stringify(obj)
            success: ->
                if GLOBAL.debug
                    console.log 'Successfully updated skills'
            error: ->
                if GLOBAL.debug
                    console.log 'Error submitting skills'

    increaseAllSkills: (amount) ->
        current = @filter (word) -> word.get('current')
        _(current).each (word) ->
            skill = word.get('skill')
            skill = Math.min(skill+amount,100)
            word.set({skill:skill})



HighScore = Backbone.Model.extend {}

HighScores = Backbone.Collection.extend
    model: HighScore

    loadScores: (url, callback) ->
        $.ajax
            type:'GET'
            url:url
            dataType:'json'
            data:
                game_id:1
                level_id:1
            success: (data) =>
                _(data.response).each (score) =>
                    @add score
                if callback? then callback()
            error: ->
                if GLOBAL.debug
                    console.log "Error getting scores"

    loadPersonal: (callback) -> 
        @loadScores VOCAB_API_URL + 'user_high_scores/', callback

    loadFriends: (callback) -> 
        @loadScores VOCAB_API_URL + 'friend_high_scores/', callback

    loadAll: -> @loadScores VOCAB_API_URL + 'all_high_scores/'


# Adds a score
# Callback is (id, personal_rank, friends_rank)
submitScore = (game_id, level_id, score, callback) ->
    $.ajax
        type:'GET'
        url:VOCAB_API_URL + "add_score/"
        dataType:'json'
        data:
            game_id:game_id
            level_id:level_id
            score:score
        success: (data) =>
            if callback?
                r = data.response

                # Parse scores
                personal = new HighScores r.personal_high_scores
                friends = new HighScores r.friends_high_scores

                # Pass info to callback
                callback(
                    r.id, 
                    r.personal_rank, 
                    r.friend_rank,
                    personal,
                    friends)
        error: ->
            if GLOBAL.debug
                console.log "Error submitting score"
    

# Exports
@DB =
    Word:Word
    Words:Words
    HighScore:HighScore
    HighScores:HighScores
    submitScore:submitScore
