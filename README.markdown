About This App
====
This is a facebook app game for learning SAT vocab.  It presents one
definition and two
words together at the same time and the player must quickly choose which
word fits the definition before the time runs out.  As correct answers
are given, the time continues to get faster.  Three incorrect answers
and you're out.

The app requires facebook login to track your scores, and see your
friends scores and how you rank against them.

The app is built with coffeescript, backbone.js, SASS and django.  Since its no longer being maintained, we've decided to open source it!

Screenshot
====
![Vocab Game Screenshot](http://www.derekdahmer.com/images/projects/prepfly-2.png "Vocab Game Screenshot")

Installation Instructions
====

Requirements
---
* pip
* a virtualenv


Install Packages
---
First install all the necessary python packages from the included
requirements file using pip

    pip install -r requirements.txt


Customize DB Settings
---
Create settings_local.py and give it your DB details.  It will work with any kind of database you
want, but to see 'friends scores', you must use postgres since that uses
raw SQL to do the rankings.  Heres a sqlite example

    DATABASES = {
        'default': {
            'ENGINE':'django.db.backends.sqlite3',
            'NAME':'/Users/Me/prepfly-vocab-game.db',
            'USER':'',
            'PASSWORD':'',
            'USER': '',                      # Not used with sqlite3.
            'PASSWORD': '',                  # Not used with sqlite3.
            'HOST': '',                      # Set to empty string for localhost. Not used with sqlite3.
            'PORT': '',                      # Set to empty string for default. Not used with sqlite3.
        }
    }


Customize Facebook Settings
---

Since the app requires facebook login, jump over to (facebook)[https://developers.facebook.com/apps/] and make yourself an app.
Fill the settings_local.py like so:

    FACEBOOK_APPLICATION_ID = '<app id>'
    FACEBOOK_APPLICATION_SECRET_KEY = '<secret key>'
    FACEBOOK_APPLICATION_API_KEY = '<api key>'

    FACEBOOK_APP_ID          = '<app id>'
    FACEBOOK_API_SECRET      = '<secret>'

Finally set THIS_HOST to the "Site URL" you specified in the facebook
developer page e.g. `SITE_URL = 'http://www.example.com:8000'`


Configure the DB
---
Get the DB up to sync with syncdb and south

    ./manage.py syncdb
    ./manage.py migrate vocab
    ./manage.py migrate accounts

And if its the first time, pull in the sample content provided in the
fixtures file

    ./manage.py loaddata vocab/fixtures/words_defs_levels.json


Run It!
---

./manage.py runserver 8000



Authors
---
[Derek Dahmer](http://derekdahmer.com) - All code

[Evanglos Kramvis](http://www.linkedin.com/in/angelokramvis) - Sample Vocab Content

