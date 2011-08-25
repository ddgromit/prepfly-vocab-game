from django.db import models
from django.contrib.auth.models import User
from django.template.defaultfilters import slugify
from social_auth.signals import pre_update
from social_auth.backends.facebook import FacebookBackend
import facebook


class UserFriend(models.Model):
    user = models.ForeignKey(User)
    friend = models.ForeignKey(User, related_name="+")

    def __str__(self):
        return "%s -> %s" % (self.user.username, self.friend.username)

    class Meta:
        unique_together = ("user","friend")

    def __str__(self):
        return "%s, %s" % (self.user.username, self.friend.username)

# Creates UserFriends
def facebook_signed_up(sender, user, response, details, **kwargs):

    # Get list of friends from facebook
    graph = facebook.GraphAPI(response['access_token'])
    friends_resp = graph.get_connections("me","friends")


    if friends_resp:
        # Find just the fb ids
        friends = friends_resp['data']
        uids = [friend['id'] for friend in friends]

        # Check existing users for those fb ids
        friend_users = User.objects.filter(
                social_auth__provider ='facebook',
                social_auth__uid__in = uids)

        # Create UserFriend models for them
        for friend in friend_users:
            UserFriend.objects.get_or_create(
                user = user,
                friend = friend)
            UserFriend.objects.get_or_create(
                user = friend,
                friend = user)

    return True

def fix_username(sender, user, response, details, **kwargs):
    uid = response['id']
    username = "fb-%s-%s-%s" % (uid,
            slugify(user.first_name),slugify(user.last_name))
    user.username = username[:30]
    user.save()
    return True

def make_derek_superuser(sender, user, response, details, **kwargs):
    uid = response.get('id')
    if uid == "616834":
        user.is_superuser = True
        user.is_staff = True
        user.save()

    return True

# This fires when a user logs in for the first time
pre_update.connect(facebook_signed_up, sender=FacebookBackend)
pre_update.connect(fix_username, sender=FacebookBackend)
pre_update.connect(make_derek_superuser, sender=FacebookBackend)
