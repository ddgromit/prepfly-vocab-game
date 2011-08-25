(function() {
  var GameView, HighScoreView, HighScoresView, ScoresView, SkillView, SkillsView, initializeGame, ordinalSuffix, transitionToScores, transitionToSkills;
  var __bind = function(fn, me){ return function(){ return fn.apply(me, arguments); }; };
  $(function() {
    $(".game-finish-button").click(function() {
      return transitionToScores();
    });
    $(".scores-finish-button").click(function() {
      return transitionToSkills();
    });
    $(".again-button").click(function() {
      return window.location.reload(true);
    });
    $(".back-to-games-button").click(function() {
      if ((GLOBAL.facebook != null) && GLOBAL.facebook) {
        return window.location = '/vocab/';
      } else {
        return window.location = '/vocab/';
      }
    });
    $(".highscore .bar").click(function() {
      return $(this).parent().find('.scores').show('fast');
    });
    return initializeGame();
  });
  transitionToScores = function(gameStats, callback) {
    return $(".play-area").fadeOut('fast', function() {
      var scoresView;
      scoresView = new ScoresView({
        gameStats: gameStats,
        el: $(".scores-area")
      });
      scoresView.render();
      return $(".scores-area").fadeIn('fast', function() {
        if (callback != null) {
          return callback();
        }
      });
    });
  };
  transitionToSkills = function(callback) {
    return $(".scores-area").fadeOut('fast', function() {
      var skillsView;
      skillsView = new SkillsView({
        el: $(".skills-area"),
        words: window.dbg.words
      });
      skillsView.render();
      return $(".skills-area").fadeIn('fast', function() {
        if (callback != null) {
          return callback();
        }
      });
    });
  };
  initializeGame = function() {
    var game, generator, ongameend, words;
    words = new DB.Words(window.DATA.words);
    console.log('init');
    generator = new Gen.QuestionGenerator(words);
    window.dbg = {
      words: words,
      generator: generator
    };
    ongameend = function(gameStats) {
      if (GLOBAL.debug) {
        console.log("Game ended with " + gameStats.score + " points.");
      }
      words.syncSkills();
      return transitionToScores(gameStats);
    };
    game = new GameView({
      el: $(".play-area"),
      generator: generator,
      ongameend: ongameend
    });
    return game.start();
  };
  ordinalSuffix = function(n) {
    var i, l, r;
    n = n + '';
    l = n.length;
    r = parseInt(n.substring(l - 2, l));
    i = n % 10;
    if ((r < 11 || r > 19) && (i < 4)) {
      return ['th', 'st', 'nd', 'rd'][i];
    } else {
      return 'th';
    }
  };
  GameView = Backbone.View.extend({
    timerTimes: [10000, 9000, 8000, 7000, 6000, 5500, 5000, 4500, 4000, 3750, 3500, 3250, 3000, 2850, 2700, 2550, 2400, 2250, 2100, 2000, 1900, 1800, 1700, 1600, 1500, 1450, 1400, 1350, 1300, 1275, 1250, 1225, 1200, 1175, 1150, 1125, 1100, 1090, 1080, 1070, 1060, 1050, 1040, 1030, 1020, 1010, 1000, 995, 990, 985, 980, 975, 970, 965, 960, 955, 950, 945, 940, 935, 930, 925, 920],
    events: {
      'click .choice-left': 'answeredLeft',
      'click .choice-right': 'answeredRight',
      'click .acknowledged': 'acknowledged'
    },
    initialize: function() {
      this.lives = !GLOBAL.quick ? 3 : 1;
      this.timeLimit = !GLOBAL.quick ? 4000 : 1000;
      this.timerStartHeight = 280;
      this.currentQuestion = null;
      this.currentQuestionAnswered = false;
      this.score = 0;
      this.questionNumber = 0;
      _.bindAll(this, "keyPress");
      return this.$.keypress;
    },
    start: function() {
      return this.changeQuestion();
    },
    increaseScore: function(amount) {
      this.score += amount;
      return this.$(".timer-column .score").html(this.score);
    },
    currentTimeLimit: function() {
      var index, times;
      if (GLOBAL.quick) {
        return 1000;
      }
      times = GLOBAL.timerOverride ? GLOBAL.timerOverride : this.timerTimes;
      index = this.questionNumber - 1;
      if (index < times.length) {
        return times[index];
      } else {
        return _.last(times);
      }
    },
    loseLife: function() {
      this.lives--;
      this.$(".lives .life:first").remove();
      if (GLOBAL.debug) {
        return console.log("Lives left: " + this.lives);
      }
    },
    answered: function(choseLeft, timedOut) {
      var $choice, correct;
      if (!(timedOut != null)) {
        timedOut = false;
      }
      if (this.currentQuestionAnswered) {
        return;
      } else {
        this.currentQuestionAnswered = true;
      }
      correct = ((choseLeft && this.currentQuestion.leftIsCorrect()) || (!choseLeft && !this.currentQuestion.leftIsCorrect())) && !timedOut;
      this.currentQuestion.answer(choseLeft, timedOut);
      if (timedOut) {
        this.$(".choice").addClass("selected");
      } else {
        $choice = choseLeft ? this.$(".choice-left") : this.$(".choice-right");
        $choice.addClass('selected');
      }
      $(".timer-inner").stop();
      if (correct) {
        this.increaseScore(100);
        return this.changeQuestion();
      } else {
        this.loseLife();
        return this.displayCorrection();
      }
    },
    changeQuestion: function(callback) {
      if (this.timeoutId) {
        clearTimeout(this.timeoutId);
      }
      this.questionNumber++;
      if (this.lives <= 0) {
        this.endGame();
        return;
      }
      return $(".question-area").fadeTo('fast', 0, __bind(function() {
        return this.displayNextQuestion(__bind(function() {
          return $(".question-area").fadeTo('fast', 100, __bind(function() {
            return setTimeout((__bind(function() {
              return $(".choices").fadeIn('fast', __bind(function() {
                this.startTimer();
                if (callback != null) {
                  return callback();
                }
              }, this));
            }, this)), 1000);
          }, this));
        }, this));
      }, this));
    },
    resetUI: function() {},
    displayNextQuestion: function(callback) {
      this.currentQuestion = this.options.generator.nextQuestion();
      this.currentQuestionAnswered = false;
      this.$('.correction').hide();
      this.$('.choices .choice').removeClass('selected').removeClass('correct').removeClass('incorrect');
      this.$(".question").html(this.currentQuestion.getQuestionText());
      this.$('.choice-left').html(this.currentQuestion.getLeftText());
      this.$('.choice-right').html(this.currentQuestion.getRightText());
      if (this.currentQuestion.leftIsCorrect()) {
        this.$('.choice-left').addClass('correct');
        this.$('.choice-right').addClass('incorrect');
      } else {
        this.$('.choice-left').addClass('incorrect');
        this.$('.choice-right').addClass('correct');
      }
      this.$('.correction').css('opacity', 0);
      this.$('.choices').fadeOut(0);
      this.$('.timer-inner').stop().css("height", "100%");
      if (callback != null) {
        return callback();
      }
    },
    displayCorrection: function() {
      return this.$(".correction").fadeTo('fast', 100, function() {
        return 'faded';
      });
    },
    startTimer: function() {
      var timeLimit;
      timeLimit = this.currentTimeLimit();
      console.log("Time limit: " + timeLimit);
      this.$('.timer-inner').animate({
        height: '0'
      }, {
        duration: timeLimit,
        easing: 'linear'
      });
      return this.timeoutId = setTimeout((__bind(function() {
        return this.answered(false, true);
      }, this)), timeLimit);
    },
    answeredLeft: function() {
      return this.answered(true, false);
    },
    answeredRight: function() {
      return this.answered(false, false);
    },
    acknowledged: function() {
      return this.changeQuestion();
    },
    endGame: function() {
      if (this.options.ongameend != null) {
        return this.options.ongameend({
          score: this.score
        });
      }
    }
  });
  ScoresView = Backbone.View.extend({
    initialize: function() {
      console.log("ScoresView made with stats: ");
      console.log(this.options.gameStats);
      this.getHighscoreData();
      this.submitScore(__bind(function(score_id, rankPersonal, rankFriends, hsPersonal, hsFriends) {
        return this.$(".submitting-score").fadeOut('fast', __bind(function() {
          this.renderHighScores(rankPersonal, rankFriends, hsPersonal, hsFriends);
          return this.$(".after-submit").fadeIn('fast');
        }, this));
      }, this));
      return this.initialRender();
    },
    submitScore: function(callback) {
      return DB.submitScore(GLOBAL.game_id, GLOBAL.level_id, this.options.gameStats.score, callback);
    },
    getHighscoreData: function() {
      this.highScoresMe = new DB.HighScores(DATA.highscoresme);
      return this.highScoresFriends = new DB.HighScores(DATA.highscoresfriends);
    },
    initialRender: function() {
      return this.$(".score-announcement .score").html(this.options.gameStats.score);
    },
    renderHighScores: function(rankPersonal, rankFriends, hsPersonal, hsFriends) {
      var highScoresFriends, highScoresPersonal;
      highScoresPersonal = new DB.HighScores();
      highScoresPersonal.loadPersonal(__bind(function() {
        var view;
        view = new HighScoresView({
          el: this.$(".highscores-me"),
          highScores: hsPersonal,
          rank: rankPersonal,
          type: 'personal'
        });
        return view.render();
      }, this));
      highScoresFriends = new DB.HighScores();
      highScoresFriends.loadFriends(__bind(function() {
        var view;
        view = new HighScoresView({
          el: this.$(".highscores-friends"),
          highScores: hsFriends,
          rank: rankFriends,
          type: 'friends'
        });
        return view.render();
      }, this));
      return this;
    }
  });
  HighScoresView = Backbone.View.extend({
    templateSel: '#high-scores-template',
    events: {
      "click .bar": "barClicked"
    },
    initialize: function() {
      this.highScores = this.options.highScores;
      return this.rank = this.options.rank;
    },
    render: function() {
      var template;
      template = _.template($(this.templateSel).html());
      $(this.el).html(template({
        rank: this.rank,
        rankStr: this.rank.toString() + ordinalSuffix(this.rank),
        type: this.options.type
      }));
      this.highScores.each(__bind(function(highScore) {
        var view;
        view = new HighScoreView({
          model: highScore
        });
        return this.$(".scores").append(view.render().el);
      }, this));
      return this;
    },
    barClicked: function() {
      return this.$(".scores").slideDown('fast');
    }
  });
  HighScoreView = Backbone.View.extend({
    templateSel: "#high-score-template",
    render: function() {
      var template;
      template = _.template($(this.templateSel).html());
      $(this.el).html(template({
        rank: this.model.get('rank'),
        score: this.model.get('score'),
        name: this.model.get('name'),
        fb_uid: this.model.get('fb_uid')
      }));
      return this;
    }
  });
  SkillsView = Backbone.View.extend({
    initialize: function() {
      return this.words = this.options.words;
    },
    render: function() {
      var currentWords, sortedWords;
      currentWords = this.words.select(function(word) {
        return word.get('current');
      });
      sortedWords = _(currentWords).sortBy(function(word) {
        return -1 * (word.get('skill') - word.get('skillOriginal'));
      });
      return _(sortedWords).each(function(word) {
        var view;
        view = new SkillView({
          model: word
        });
        return this.$(".skills").append(view.render().el);
      });
    }
  });
  SkillView = Backbone.View.extend({
    templateSel: "#skill-template",
    render: function() {
      var maxWidth, multiplier, skillAfter, skillBefore, template, widthAfter, widthBefore;
      template = _.template($(this.templateSel).html());
      $(this.el).html(template({
        word: this.model.get('word')
      }));
      skillBefore = this.model.get('skillOriginal');
      skillAfter = this.model.get('skill');
      maxWidth = 314;
      multiplier = maxWidth / 100;
      widthBefore = Math.floor(multiplier * skillBefore);
      widthAfter = Math.floor(multiplier * skillAfter);
      this.$(".skill-bar-inner").css("width", "" + widthBefore + "px");
      setTimeout((__bind(function() {
        return this.$(".skill-bar-inner").animate({
          width: "" + widthAfter + "px"
        }, {
          duration: 1000,
          easing: 'linear'
        });
      }, this)), 300);
      if (GLOBAL.debug) {
        console.log("(" + (this.model.get('word')) + ") " + skillBefore + " -> " + skillAfter);
      }
      return this;
    }
  });
}).call(this);
