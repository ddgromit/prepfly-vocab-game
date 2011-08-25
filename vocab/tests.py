from django.test import TestCase
from django.test.client import Client
from django.contrib.auth.models import User
from django.test.client import RequestFactory
from django.utils import simplejson
from vocab.lib import get_user_progress, current_words, get_level_percent
from vocab.models import Word

class LevelupTestCase(TestCase):
    def setUp(self):
        self.factory = RequestFactory()

    def create_user(self):
        # Create a user
        user = User.objects.create_user("u1","u1@example.com","pass")

        # Make sure they are at least level 1
        progress = get_user_progress(user)

        # Login
        c = Client()
        success = c.login(username="u1",password="pass")
        self.assertTrue(success)

        return (user, c)

    def assert_json_response(self, response):
        data = simplejson.loads(response.content)
        if response.status_code != 200:
            raise Exception("Error %s: %s" % (response.status_code,
                data['meta']['errorDetail']))
        return data

    def test_user_creation(self):
        self.create_user()

    def test_current_words(self):
        (user, client) = self.create_user()
        response = client.get('/lingo/api/current_words/')
        data = simplejson.loads(response.content)

        # Make sure there are some there
        self.assertTrue(len(data['response']) > 0)

        self.assertTrue(data['response'][0]['current'])

    def test_update_skills(self):
        (user, client) = self.create_user()
        response = client.get('/lingo/api/current_words/')
        current_words_json = simplejson.loads(response.content)['response']
        word_ids = [word['id'] for word in current_words_json]

        # Grab the current words
        words = Word.objects.all().filter(id__in=word_ids)
        self.assertTrue(len(words) > 0)

        # Create the response
        response_json = []
        for word in words:
            response_json.append({
                "wordId":word.id,
                "skill":50,
            })

        # Submit response
        response = client.post('/lingo/api/update_skills/',data =
                simplejson.dumps(response_json),
                content_type='application/json')
        data = self.assert_json_response(response)
        leveled_up = data['response']['leveled_up']
        self.assertFalse(leveled_up)

        # Test skill percent
        percent = get_level_percent(user)
        self.assertEqual(percent,50)

        # Try and level up
        response_json = []
        for word in words:
            response_json.append({
                "wordId":word.id,
                "skill":95,
            })

        # Submit response
        response = client.post('/lingo/api/update_skills/',data =
                simplejson.dumps(response_json),
                content_type='application/json')
        data = self.assert_json_response(response)
        leveled_up = data['response']['leveled_up']
        self.assertTrue(leveled_up)


        # Check that the user is at a new level
        user = User.objects.get(id=user.id)
        self.assertEqual(user.userprogress.current_level.number,2)

        # Check that all the words are at the second level
        words = current_words(user.userprogress)
        for word in words:
            self.assertEqual(word.level.number,2)
        
        # Test skill percent has reset
        percent = get_level_percent(user)
        self.assertEqual(percent,0)
