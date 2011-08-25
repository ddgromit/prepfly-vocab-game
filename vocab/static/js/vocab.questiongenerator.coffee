# Generates a random number between a and b, inclusive
randomBetween = (a,b) -> return Math.floor(Math.random() * (b-a + 1))

class Question
    constructor: (@testedWord, @counterWord, @questionGenerator) ->
        # Randomize order or options
        @leftCorrect = Math.random() >= 0.5
        if @leftCorrect
            @leftWord = @testedWord
            @rightWord = @counterWord
        else
            @leftWord = @counterWord
            @rightWord = @testedWord

        # Pick definitions
        @leftText = @_pickDefinition(@leftWord).text
        @rightText = @_pickDefinition(@rightWord).text

    getQuestionText: -> return @testedWord.get('word')

    getLeftText: -> return @leftText

    getRightText: -> return @rightText

    leftIsCorrect: -> return @leftCorrect

    _pickDefinition: (word) ->
        definitions = word.get('definitions')
        if definitions.length == 0
            throw Error("No definition on word #{word.get('word')}.")

        # Grab a random definition from the word
        return definitions[randomBetween(0,definitions.length-1)]

    answer: (choseLeft, timedOut) ->
        correct = ((choseLeft and @leftCorrect) or (not choseLeft and not @leftCorrect)) and not timedOut
        @questionGenerator.answer(@testedWord,@counterWord,correct)

    toFullString: ->
        return "Question: (#{@getQuestionText()}) #{@getLeftText()} / #{@getRightText()}"


class QuestionGenerator
    constructor: (@words) ->
        # Keep track of original skill
        @words.each (word) ->
            word.set
                skillOriginal:word.get('skill')

        # Split into current and old words
        @currentWords = @words.select (word) -> word.get('current')
        @oldWords = @words.select (word) -> not word.get('current')

        if @oldWords and @oldWords.length > 0
            @pRecycle = 0.2
            @pRecycleCounter = 0.3
        else
            @pRecycle = 0
            @pRecycleCounter = 0

        if GLOBAL.debug
            console.log "Using #{@currentWords.length} current words and #{@oldWords.length} old words."

        # Dont choose last word
        @lastWord = null
        @lastSeen = 1

    # Get the next question
    nextQuestion: ->
        # Pick words
        testedWord = @_testedWord()
        counterWord = @_counterWord(testedWord)

        # Remember last word
        @lastWord = testedWord

        # Make the question
        return new Question(testedWord, counterWord, this)

    # Picks the word to be tested
    _testedWord: ->
        # Use old words or current words
        wordCollection = if Math.random() > @pRecycle then @currentWords else @oldWords

        # Exclude last word
        available = _(wordCollection).reject (word) => 
            @lastWord? and (word.id == @lastWord.id)

        # Convert to objects
        wordObjs = _(available).map (word) -> return { word:word }

        # Calculate the weights
        calculateSkillWeights(wordObjs)
        calculateLastSeenWeights(wordObjs)
        combineWeights(wordObjs)

        if GLOBAL.debug
            console.log "Weights: "
            _(wordObjs).each (wordObj) ->
                console.log "#{wordObj.word.get('word')} has weight #{wordObj.weight}"
                console.log wordObj

        return chooseByWeight(wordObjs).word

    # Picks a word to be pitted against the given word
    _counterWord: (testedWord) ->
        # Use old words or current words
        wordCollection = if Math.random() > @pRecycleCounter then @currentWords else @oldWords

        # Exclude correct word
        available = _(wordCollection).reject (word) -> word.id == testedWord.id

        # Pick random one
        return available[randomBetween(0, available.length - 1)]


    answer: (testedWord, counterWord, correct) -> 
        # Calculate skill increase
        oldSkill = testedWord.get('skill')
        newSkill = oldSkill
        if correct
            newSkill += 10
        else
            newSkill += 2

        # Set the new skill
        newSkill = Math.min(newSkill,100)
        testedWord.set
            skill:newSkill

        # Keep track of when in this session the word was last seen
        testedWord.set
            lastSeen:@lastSeen
        @lastSeen++

        # Feedback about upgrades
        if GLOBAL.debug
            console.log "Upgraded #{testedWord.get('word')} #{oldSkill} -> #{newSkill}"



calculateLastSeenWeights = (wordObjs) ->
    if wordObjs.length == 0
        throw Error("Empty word array given")

    weightDiff = 5

    # Give objects that haven't been seen a null value
    _(wordObjs).each (wordObj) -> 
        lastSeen = wordObj.word.get('lastSeen')
        wordObj.lastSeen = if lastSeen? then lastSeen else null

    
    # Find the last seen word id so we can do relative ordering
    latestLastSeen = _(wordObjs).reduce (memo, wordObj) ->
        if wordObj.lastSeen?
            return Math.max(wordObj.lastSeen,memo)
        return memo
    , null
    
    console.log "Latest last seen #{latestLastSeen}"

    # Calculate a weight for each word
    _(wordObjs).each (wordObj) ->
        # A never seen word gets the max diff
        weight = weightDiff

        if wordObj.lastSeen? and latestLastSeen?
            # A word seen last gets 0, seen 5 or more times ago gets 5
            diff = latestLastSeen - wordObj.lastSeen
            console.log "Diff: #{diff}"
            weight = Math.min(diff,weightDiff)

        wordObj.lastSeenWeight = weight

    # Normalize
    totalWeight = _(wordObjs).reduce (memo, wordObj) ->
        return memo + wordObj.lastSeenWeight
    , 0
    _(wordObjs).each (wordObj) ->
        wordObj.lastSeenWeightNormalized = wordObj.lastSeenWeight / totalWeight


calculateSkillWeights = (wordObjs) ->
    choiceFactor = 4

    # Make the weights
    _(wordObjs).each (wordObj) ->
        wordObj.skillWeight = 1 + ((choiceFactor - 1) * (100 - wordObj.word.get('skill')) / 100)

    # Normalize
    totalWeight = _(wordObjs).reduce (memo, wordObj) ->
        return memo + wordObj.skillWeight
    , 0
    _(wordObjs).each (wordObj) ->
        wordObj.skillWeightNormalized = wordObj.skillWeight / totalWeight

combineWeights = (wordObjs) ->
    skillWeightFactor = 0.6
    lastSeenFactor = 1 - skillWeightFactor

    _(wordObjs).each (wordObj) ->
        wordObj.weight = (skillWeightFactor * wordObj.skillWeightNormalized) +
            (lastSeenFactor * wordObj.lastSeenWeightNormalized)

chooseByWeight = (items) ->
    totalWeight = _(items).reduce ((memo, item) -> memo + item.weight), 0

    n = Math.random()*totalWeight
    chosen = _(items).detect (item) ->
        #debugger
        if n < item.weight
            return true
        else
            n = n - item.weight
            return false

    if not chosen?
        throw Error("Couldn't find an item")

    return chosen
            


# Exports
@Gen =
    Question:Question
    QuestionGenerator:QuestionGenerator

