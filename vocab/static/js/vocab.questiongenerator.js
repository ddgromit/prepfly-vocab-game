(function() {
  var Question, QuestionGenerator, calculateLastSeenWeights, calculateSkillWeights, chooseByWeight, combineWeights, randomBetween;
  var __bind = function(fn, me){ return function(){ return fn.apply(me, arguments); }; };
  randomBetween = function(a, b) {
    return Math.floor(Math.random() * (b - a + 1));
  };
  Question = (function() {
    function Question(testedWord, counterWord, questionGenerator) {
      this.testedWord = testedWord;
      this.counterWord = counterWord;
      this.questionGenerator = questionGenerator;
      this.leftCorrect = Math.random() >= 0.5;
      if (this.leftCorrect) {
        this.leftWord = this.testedWord;
        this.rightWord = this.counterWord;
      } else {
        this.leftWord = this.counterWord;
        this.rightWord = this.testedWord;
      }
      this.leftText = this._pickDefinition(this.leftWord).text;
      this.rightText = this._pickDefinition(this.rightWord).text;
    }
    Question.prototype.getQuestionText = function() {
      return this.testedWord.get('word');
    };
    Question.prototype.getLeftText = function() {
      return this.leftText;
    };
    Question.prototype.getRightText = function() {
      return this.rightText;
    };
    Question.prototype.leftIsCorrect = function() {
      return this.leftCorrect;
    };
    Question.prototype._pickDefinition = function(word) {
      var definitions;
      definitions = word.get('definitions');
      if (definitions.length === 0) {
        throw Error("No definition on word " + (word.get('word')) + ".");
      }
      return definitions[randomBetween(0, definitions.length - 1)];
    };
    Question.prototype.answer = function(choseLeft, timedOut) {
      var correct;
      correct = ((choseLeft && this.leftCorrect) || (!choseLeft && !this.leftCorrect)) && !timedOut;
      return this.questionGenerator.answer(this.testedWord, this.counterWord, correct);
    };
    Question.prototype.toFullString = function() {
      return "Question: (" + (this.getQuestionText()) + ") " + (this.getLeftText()) + " / " + (this.getRightText());
    };
    return Question;
  })();
  QuestionGenerator = (function() {
    function QuestionGenerator(words) {
      this.words = words;
      this.words.each(function(word) {
        return word.set({
          skillOriginal: word.get('skill')
        });
      });
      this.currentWords = this.words.select(function(word) {
        return word.get('current');
      });
      this.oldWords = this.words.select(function(word) {
        return !word.get('current');
      });
      if (this.oldWords && this.oldWords.length > 0) {
        this.pRecycle = 0.2;
        this.pRecycleCounter = 0.3;
      } else {
        this.pRecycle = 0;
        this.pRecycleCounter = 0;
      }
      if (GLOBAL.debug) {
        console.log("Using " + this.currentWords.length + " current words and " + this.oldWords.length + " old words.");
      }
      this.lastWord = null;
      this.lastSeen = 1;
    }
    QuestionGenerator.prototype.nextQuestion = function() {
      var counterWord, testedWord;
      testedWord = this._testedWord();
      counterWord = this._counterWord(testedWord);
      this.lastWord = testedWord;
      return new Question(testedWord, counterWord, this);
    };
    QuestionGenerator.prototype._testedWord = function() {
      var available, wordCollection, wordObjs;
      wordCollection = Math.random() > this.pRecycle ? this.currentWords : this.oldWords;
      available = _(wordCollection).reject(__bind(function(word) {
        return (this.lastWord != null) && (word.id === this.lastWord.id);
      }, this));
      wordObjs = _(available).map(function(word) {
        return {
          word: word
        };
      });
      calculateSkillWeights(wordObjs);
      calculateLastSeenWeights(wordObjs);
      combineWeights(wordObjs);
      if (GLOBAL.debug) {
        console.log("Weights: ");
        _(wordObjs).each(function(wordObj) {
          console.log("" + (wordObj.word.get('word')) + " has weight " + wordObj.weight);
          return console.log(wordObj);
        });
      }
      return chooseByWeight(wordObjs).word;
    };
    QuestionGenerator.prototype._counterWord = function(testedWord) {
      var available, wordCollection;
      wordCollection = Math.random() > this.pRecycleCounter ? this.currentWords : this.oldWords;
      available = _(wordCollection).reject(function(word) {
        return word.id === testedWord.id;
      });
      return available[randomBetween(0, available.length - 1)];
    };
    QuestionGenerator.prototype.answer = function(testedWord, counterWord, correct) {
      var newSkill, oldSkill;
      oldSkill = testedWord.get('skill');
      newSkill = oldSkill;
      if (correct) {
        newSkill += 10;
      } else {
        newSkill += 2;
      }
      newSkill = Math.min(newSkill, 100);
      testedWord.set({
        skill: newSkill
      });
      testedWord.set({
        lastSeen: this.lastSeen
      });
      this.lastSeen++;
      if (GLOBAL.debug) {
        return console.log("Upgraded " + (testedWord.get('word')) + " " + oldSkill + " -> " + newSkill);
      }
    };
    return QuestionGenerator;
  })();
  calculateLastSeenWeights = function(wordObjs) {
    var latestLastSeen, totalWeight, weightDiff;
    if (wordObjs.length === 0) {
      throw Error("Empty word array given");
    }
    weightDiff = 5;
    _(wordObjs).each(function(wordObj) {
      var lastSeen;
      lastSeen = wordObj.word.get('lastSeen');
      return wordObj.lastSeen = lastSeen != null ? lastSeen : null;
    });
    latestLastSeen = _(wordObjs).reduce(function(memo, wordObj) {
      if (wordObj.lastSeen != null) {
        return Math.max(wordObj.lastSeen, memo);
      }
      return memo;
    }, null);
    console.log("Latest last seen " + latestLastSeen);
    _(wordObjs).each(function(wordObj) {
      var diff, weight;
      weight = weightDiff;
      if ((wordObj.lastSeen != null) && (latestLastSeen != null)) {
        diff = latestLastSeen - wordObj.lastSeen;
        console.log("Diff: " + diff);
        weight = Math.min(diff, weightDiff);
      }
      return wordObj.lastSeenWeight = weight;
    });
    totalWeight = _(wordObjs).reduce(function(memo, wordObj) {
      return memo + wordObj.lastSeenWeight;
    }, 0);
    return _(wordObjs).each(function(wordObj) {
      return wordObj.lastSeenWeightNormalized = wordObj.lastSeenWeight / totalWeight;
    });
  };
  calculateSkillWeights = function(wordObjs) {
    var choiceFactor, totalWeight;
    choiceFactor = 4;
    _(wordObjs).each(function(wordObj) {
      return wordObj.skillWeight = 1 + ((choiceFactor - 1) * (100 - wordObj.word.get('skill')) / 100);
    });
    totalWeight = _(wordObjs).reduce(function(memo, wordObj) {
      return memo + wordObj.skillWeight;
    }, 0);
    return _(wordObjs).each(function(wordObj) {
      return wordObj.skillWeightNormalized = wordObj.skillWeight / totalWeight;
    });
  };
  combineWeights = function(wordObjs) {
    var lastSeenFactor, skillWeightFactor;
    skillWeightFactor = 0.6;
    lastSeenFactor = 1 - skillWeightFactor;
    return _(wordObjs).each(function(wordObj) {
      return wordObj.weight = (skillWeightFactor * wordObj.skillWeightNormalized) + (lastSeenFactor * wordObj.lastSeenWeightNormalized);
    });
  };
  chooseByWeight = function(items) {
    var chosen, n, totalWeight;
    totalWeight = _(items).reduce((function(memo, item) {
      return memo + item.weight;
    }), 0);
    n = Math.random() * totalWeight;
    chosen = _(items).detect(function(item) {
      if (n < item.weight) {
        return true;
      } else {
        n = n - item.weight;
        return false;
      }
    });
    if (!(chosen != null)) {
      throw Error("Couldn't find an item");
    }
    return chosen;
  };
  this.Gen = {
    Question: Question,
    QuestionGenerator: QuestionGenerator
  };
}).call(this);
