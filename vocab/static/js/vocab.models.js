(function() {
  var HighScore, HighScores, VOCAB_API_URL, Word, Words, submitScore;
  var __bind = function(fn, me){ return function(){ return fn.apply(me, arguments); }; };
  VOCAB_API_URL = '/vocab/api/';
  Word = Backbone.Model.extend({});
  Words = Backbone.Collection.extend({
    model: Word,
    skillUpdateUrl: VOCAB_API_URL + 'update_skills/',
    syncSkills: function() {
      var changed, obj;
      changed = this.filter(function(word) {
        return word.get('skillOriginal') !== word.get('skill');
      });
      if (GLOBAL.debug) {
        console.log("Found " + changed.length + " words with new skills.");
      }
      obj = _(changed).map(function(word) {
        return {
          'wordId': word.id,
          'skill': word.get('skill')
        };
      });
      return $.ajax({
        type: 'POST',
        url: this.skillUpdateUrl,
        dataType: 'json',
        data: JSON.stringify(obj),
        success: function() {
          if (GLOBAL.debug) {
            return console.log('Successfully updated skills');
          }
        },
        error: function() {
          if (GLOBAL.debug) {
            return console.log('Error submitting skills');
          }
        }
      });
    },
    increaseAllSkills: function(amount) {
      var current;
      current = this.filter(function(word) {
        return word.get('current');
      });
      return _(current).each(function(word) {
        var skill;
        skill = word.get('skill');
        skill = Math.min(skill + amount, 100);
        return word.set({
          skill: skill
        });
      });
    }
  });
  HighScore = Backbone.Model.extend({});
  HighScores = Backbone.Collection.extend({
    model: HighScore,
    loadScores: function(url, callback) {
      return $.ajax({
        type: 'GET',
        url: url,
        dataType: 'json',
        data: {
          game_id: 1,
          level_id: 1
        },
        success: __bind(function(data) {
          _(data.response).each(__bind(function(score) {
            return this.add(score);
          }, this));
          if (callback != null) {
            return callback();
          }
        }, this),
        error: function() {
          if (GLOBAL.debug) {
            return console.log("Error getting scores");
          }
        }
      });
    },
    loadPersonal: function(callback) {
      return this.loadScores(VOCAB_API_URL + 'user_high_scores/', callback);
    },
    loadFriends: function(callback) {
      return this.loadScores(VOCAB_API_URL + 'friend_high_scores/', callback);
    },
    loadAll: function() {
      return this.loadScores(VOCAB_API_URL + 'all_high_scores/');
    }
  });
  submitScore = function(game_id, level_id, score, callback) {
    return $.ajax({
      type: 'GET',
      url: VOCAB_API_URL + "add_score/",
      dataType: 'json',
      data: {
        game_id: game_id,
        level_id: level_id,
        score: score
      },
      success: __bind(function(data) {
        var friends, personal, r;
        if (callback != null) {
          r = data.response;
          personal = new HighScores(r.personal_high_scores);
          friends = new HighScores(r.friends_high_scores);
          return callback(r.id, r.personal_rank, r.friend_rank, personal, friends);
        }
      }, this),
      error: function() {
        if (GLOBAL.debug) {
          return console.log("Error submitting score");
        }
      }
    });
  };
  this.DB = {
    Word: Word,
    Words: Words,
    HighScore: HighScore,
    HighScores: HighScores,
    submitScore: submitScore
  };
}).call(this);
