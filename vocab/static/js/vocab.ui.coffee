$ ->
    $(".game-finish-button").click ->
        transitionToScores()
    $(".scores-finish-button").click ->
        transitionToSkills()
    $(".again-button").click ->
        window.location.reload(true)
    $(".back-to-games-button").click ->
        if GLOBAL.facebook? && GLOBAL.facebook
            window.location = '/vocab/'
        else
            window.location = '/vocab/'

    # Debugging
    #transitionToScores ->
    #    transitionToSkills()


    # Eventually move this to view
    $(".highscore .bar").click ->
        $(this).parent().find('.scores').show('fast')

    initializeGame()

# Hides the game, shows the scores
transitionToScores = (gameStats, callback) ->
        $(".play-area").fadeOut 'fast', ->
            scoresView = new ScoresView
                gameStats:gameStats
                el:$(".scores-area")
            scoresView.render()

            $(".scores-area").fadeIn 'fast', ->
                if callback? then callback()


transitionToSkills = (callback) ->
    $(".scores-area").fadeOut 'fast', ->
        skillsView = new SkillsView
            el:$(".skills-area")
            words:window.dbg.words
        skillsView.render()

        $(".skills-area").fadeIn 'fast', ->
            if callback? then callback()

initializeGame = ->
    # Load the words
    words = new DB.Words window.DATA.words
    console.log 'init'
    # Create the generator
    generator = new Gen.QuestionGenerator words

    # Debugging
    window.dbg =
        words:words
        generator:generator

    ongameend = (gameStats) ->
        if GLOBAL.debug then console.log "Game ended with #{gameStats.score} points."
        # Sync skills
        words.syncSkills()

        transitionToScores gameStats

    # Start the game view
    game = new GameView
        el:$(".play-area")
        generator: generator
        ongameend:ongameend

    game.start()

ordinalSuffix = (n) ->
    n = n + ''
    l = n.length
    r = parseInt(n.substring(l-2,l))
    i = n % 10
    return if ((r < 11 || r > 19) && (i < 4)) then ['th','st','nd','rd'][i] else 'th'

GameView = Backbone.View.extend

    timerTimes:[10000,9000,8000,7000,6000,5500,5000,4500,4000,3750,3500,3250,3000,2850,2700,2550,2400,2250,2100,2000,1900,1800,1700,1600,1500,1450,1400,1350,1300,1275,1250,1225,1200,1175,1150,1125,1100,1090,1080,1070,1060,1050,1040,1030,1020,1010,1000,995,990,985,980,975,970,965,960,955,950,945,940,935,930,925,920]

    events:
        'click .choice-left':'answeredLeft'
        'click .choice-right':'answeredRight'
        'click .acknowledged':'acknowledged'

    initialize: ->
        @lives = if not GLOBAL.quick then 3 else 1
        @timeLimit = if not GLOBAL.quick then 4000 else 1000
        @timerStartHeight = 280
        @currentQuestion = null
        @currentQuestionAnswered = no
        @score = 0
        @questionNumber = 0

        _.bindAll(this,"keyPress")
        @$.keypress

    start: ->
        @changeQuestion()

    increaseScore: (amount) ->
        @score += amount
        @$(".timer-column .score").html(@score)

    currentTimeLimit: ->
        if GLOBAL.quick
            return 1000
        times = if GLOBAL.timerOverride then GLOBAL.timerOverride else @timerTimes

        index = @questionNumber - 1
        if index < times.length
            return times[index]
        else
            return _.last(times)


    loseLife: ->
        @lives--
        @$(".lives .life:first").remove()
        if GLOBAL.debug then console.log "Lives left: #{@lives}"

    answered: (choseLeft, timedOut) ->
        # Default
        if not timedOut? then timedOut = no

        # Assure single answerings
        if @currentQuestionAnswered
            return
        else
            @currentQuestionAnswered = yes

        # Correct?
        correct = ((choseLeft and @currentQuestion.leftIsCorrect()) or (not choseLeft and not @currentQuestion.leftIsCorrect())) and not timedOut

        # Tell generator about the answer
        @currentQuestion.answer(choseLeft, timedOut)

        # Set selected
        if timedOut
            @$(".choice").addClass("selected")
        else
            $choice = if choseLeft then @$(".choice-left") else @$(".choice-right")
            $choice.addClass('selected')

        # Handle answers in UI
        $(".timer-inner").stop()
        if correct
            @increaseScore 100
            @changeQuestion()
        else
            @loseLife()
            @displayCorrection()


    changeQuestion: (callback) ->
        # Clear timeout
        if @timeoutId then clearTimeout(@timeoutId)
        @questionNumber++

        # Check if lives are at 0
        if @lives <= 0
            @endGame()
            return

        # Reshow question area with new question
        $(".question-area").fadeTo 'fast', 0, =>
            @displayNextQuestion =>
                $(".question-area").fadeTo 'fast', 100, =>
                    setTimeout (=> $(".choices").fadeIn 'fast', =>
                        @startTimer()
                        if callback? then callback()
                    ),1000

    resetUI: ->

    displayNextQuestion: (callback) ->
        # Load new question
        @currentQuestion = @options.generator.nextQuestion()

        # Reset the UI
        @currentQuestionAnswered = no
        @$('.correction').hide()
        @$('.choices .choice')
            .removeClass('selected')
            .removeClass('correct')
            .removeClass('incorrect')

        # Change the question text
        @$(".question").html @currentQuestion.getQuestionText()
        @$('.choice-left').html @currentQuestion.getLeftText()
        @$('.choice-right').html @currentQuestion.getRightText()

        # Add correct/incorrect classes
        if @currentQuestion.leftIsCorrect()
            @$('.choice-left').addClass('correct')
            @$('.choice-right').addClass('incorrect')
        else
            @$('.choice-left').addClass('incorrect')
            @$('.choice-right').addClass('correct')

        # Hide correction
        @$('.correction').css('opacity',0)
        @$('.choices').fadeOut 0

        # Reset the timer
        @$('.timer-inner')
            .stop()
            .css("height", "100%")


        if callback? then callback()

    displayCorrection: ->
        @$(".correction").fadeTo 'fast', 100, -> 'faded'

    startTimer: ->
        timeLimit = @currentTimeLimit()
        console.log "Time limit: #{timeLimit}"
        @$('.timer-inner')
            .animate { height:'0' },
                duration:timeLimit
                easing:'linear'
        @timeoutId = setTimeout (=> @answered no, yes), timeLimit

    answeredLeft: -> @answered(yes,no)
    answeredRight: -> @answered(no,no)

    acknowledged: -> @changeQuestion()

    endGame: ->
        if @options.ongameend?
            @options.ongameend
                score:@score


ScoresView = Backbone.View.extend
    initialize: ->
        console.log "ScoresView made with stats: "
        console.log @options.gameStats

        @getHighscoreData()

        @submitScore (score_id, rankPersonal, rankFriends, hsPersonal, hsFriends) =>
            @$(".submitting-score").fadeOut 'fast', =>
                @renderHighScores(rankPersonal, rankFriends, hsPersonal, hsFriends)
                @$(".after-submit").fadeIn('fast')

        @initialRender()

    submitScore: (callback) ->
        DB.submitScore GLOBAL.game_id, GLOBAL.level_id, @options.gameStats.score, callback

    getHighscoreData: ->
        @highScoresMe = new DB.HighScores DATA.highscoresme
        @highScoresFriends = new DB.HighScores DATA.highscoresfriends

    initialRender: ->
        # Score Line up top
        @$(".score-announcement .score")
            .html(@options.gameStats.score)

    renderHighScores: (rankPersonal, rankFriends, hsPersonal, hsFriends) ->
        # List of scores
        highScoresPersonal = new DB.HighScores()
        highScoresPersonal.loadPersonal =>
            view = new HighScoresView
                el:@$(".highscores-me")
                highScores: hsPersonal
                rank:rankPersonal
                type:'personal'
            view.render()

        # List of scores
        highScoresFriends = new DB.HighScores()
        highScoresFriends.loadFriends =>
            view = new HighScoresView
                el:@$(".highscores-friends")
                highScores: hsFriends
                rank:rankFriends
                type:'friends'
            view.render()


        return this


HighScoresView = Backbone.View.extend
    templateSel:'#high-scores-template'

    events:
        "click .bar":"barClicked"

    initialize: ->
        @highScores = @options.highScores
        @rank = @options.rank

    render: ->
        # Render container html
        template = _.template($(@templateSel).html())
        $(@el).html template
            rank:@rank
            rankStr:@rank.toString() + ordinalSuffix(@rank)
            type:@options.type

        # Render the scores
        @highScores.each (highScore) =>
            view = new HighScoreView
                model:highScore

            @$(".scores").append view.render().el

        return this

    barClicked: ->
        @$(".scores").slideDown 'fast'

HighScoreView = Backbone.View.extend
    templateSel:"#high-score-template"

    render: ->
        template = _.template($(@templateSel).html())
        $(@el).html template
            rank:@model.get('rank')
            score:@model.get('score')
            name:@model.get('name')
            fb_uid:@model.get('fb_uid')

        return this


SkillsView = Backbone.View.extend
    initialize: ->
        @words = @options.words

    render: ->
        # Current words
        currentWords = @words.select (word) -> word.get('current')

        # Sort by skill difference
        sortedWords = _(currentWords).sortBy (word) ->
            return -1 * (word.get('skill') - word.get('skillOriginal'))

        # Render each
        _(sortedWords).each (word) ->
            view = new SkillView
                model:word
            @$(".skills").append view.render().el

SkillView = Backbone.View.extend
    templateSel: "#skill-template"

    render: ->
        # Render the html
        template = _.template($(@templateSel).html())
        $(@el).html template
            word:@model.get('word')

        # Animate
        skillBefore = @model.get('skillOriginal')
        skillAfter = @model.get('skill')
        maxWidth = 314
        multiplier = maxWidth/100
        widthBefore = Math.floor(multiplier * skillBefore)
        widthAfter = Math.floor(multiplier * skillAfter)

        @$(".skill-bar-inner").css("width","#{widthBefore}px")

        setTimeout (=>
            @$(".skill-bar-inner").animate { width:"#{widthAfter}px" },
                duration:1000
                easing:'linear'
        ), 300

        if GLOBAL.debug
            console.log "(#{@model.get('word')}) #{skillBefore} -> #{skillAfter}"

        return this
