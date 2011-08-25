from django.db import models
from django.core.validators import MaxValueValidator, MinValueValidator


class Word(models.Model):
    text = models.CharField(max_length=255)
    level = models.ForeignKey('Level')

    def __str__(self):
        return "%s (level %s)" % (self.text, self.level.number)

class Definition(models.Model):
    word = models.ForeignKey('Word')
    text = models.TextField()

    def __str__(self):
        elipsis = ""
        if len(self.text) > 30:
            elipsis = "..."
        return "%s: %s%s" % (self.word.text, self.text[:30], elipsis)

class UserWord(models.Model):
    user = models.ForeignKey('auth.User', related_name="+")
    word = models.ForeignKey('Word', related_name="+")

    skill = models.IntegerField(
            default=0,
            validators = [MinValueValidator(0),MaxValueValidator(100)])

    def __str__(self):
        return "(%s) %s: %s" % (self.user.username,self.word.text,self.skill)


class Level(models.Model):
    number = models.IntegerField(validators = [MinValueValidator(1)])

    def __str__(self):
        return "Level %s" % self.number

class UserProgress(models.Model):
    user = models.OneToOneField('auth.User')
    current_level = models.ForeignKey('Level')

    def __str__(self):
        return "%s / level %s" % (self.user.username, self.current_level.number)



class Game(models.Model):
    name = models.CharField(max_length = 255)

    def __str__(self):
        return "<%s> %s" % (self.id, self.name)

class Score(models.Model):
    game = models.ForeignKey('Game')
    level = models.ForeignKey('Level')
    user = models.ForeignKey('auth.User')

    score = models.IntegerField()
    at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return "%s,l%s,g%s: %s pts" % (self.user.username, self.level.number, self.game.id, self.score)

    


