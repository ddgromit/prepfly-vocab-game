# Django settings for djprepfly project.
import os
PROJECT_PATH = os.path.abspath(os.path.split(__file__)[0])

DEBUG = True
TEMPLATE_DEBUG = DEBUG

ADMINS = (
    # ('Your Name', 'your_email@domain.com'),
)

MANAGERS = ADMINS

DATABASES = {
    'default': {
        'ENGINE': '', # Add 'postgresql_psycopg2', 'postgresql', 'mysql', 'sqlite3' or 'oracle'.
        'NAME': '',                      # Or path to database file if using sqlite3.
        'USER': '',                      # Not used with sqlite3.
        'PASSWORD': '',                  # Not used with sqlite3.
        'HOST': '',                      # Set to empty string for localhost. Not used with sqlite3.
        'PORT': '',                      # Set to empty string for default. Not used with sqlite3.
    }
}

# Local time zone for this installation. Choices can be found here:
# http://en.wikipedia.org/wiki/List_of_tz_zones_by_name
# although not all choices may be available on all operating systems.
# On Unix systems, a value of None will cause Django to use the same
# timezone as the operating system.
# If running in a Windows environment this must be set to the same as your
# system time zone.
TIME_ZONE = 'America/New_York'

# Language code for this installation. All choices can be found here:
# http://www.i18nguy.com/unicode/language-identifiers.html
LANGUAGE_CODE = 'en-us'

SITE_ID = 1

# If you set this to False, Django will make some optimizations so as not
# to load the internationalization machinery.
USE_I18N = True

# If you set this to False, Django will not format dates, numbers and
# calendars according to the current locale
USE_L10N = True

# Absolute filesystem path to the directory that will hold user-uploaded files.
# Example: "/home/media/media.lawrence.com/"
MEDIA_ROOT = ''

# URL that handles the media served from MEDIA_ROOT. Make sure to use a
# trailing slash if there is a path component (optional in other cases).
# Examples: "http://media.lawrence.com", "http://example.com/media/"
MEDIA_URL = '/uploaded_media'

# URL prefix for admin media -- CSS, JavaScript and images. Make sure to use a
# trailing slash.
# Examples: "http://foo.com/media/", "/media/".
ADMIN_MEDIA_PREFIX = '/static/admin/'

# Make this unique, and don't share it with anybody.
SECRET_KEY = 'i63yp%rm2&kb*+a09!a05tu4+oldlu)k6g!9$fk*-8o08ag0+d'

# List of callables that know how to import templates from various sources.
TEMPLATE_LOADERS = (
    'django.template.loaders.filesystem.Loader',
    'django.template.loaders.app_directories.Loader',
#     'django.template.loaders.eggs.Loader',
)

MIDDLEWARE_CLASSES = (
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    #'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
)

ROOT_URLCONF = 'urls'

TEMPLATE_DIRS = (
    os.path.join(PROJECT_PATH,"brocab/templates"),
    os.path.join(PROJECT_PATH,"home/templates"),
    os.path.join(PROJECT_PATH,"vocab/templates"),
)

TEMPLATE_CONTEXT_PROCESSORS = [
    'django.core.context_processors.debug',
    'django.core.context_processors.i18n',
    'django.core.context_processors.media',
    'django.core.context_processors.static',
    'django.contrib.auth.context_processors.auth',
]

INSTALLED_APPS = (
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    'django.contrib.admin',
    'django.contrib.admindocs',

    'accounts',
    'vocab',
    'south',
    'home',
    'social_auth',
)

AUTHENTICATION_BACKENDS = (
    'social_auth.backends.facebook.FacebookBackend',
    'django.contrib.auth.backends.ModelBackend',

    #'social_auth.backends.twitter.TwitterBackend',
    #'social_auth.backends.google.GoogleOAuthBackend',
    #'social_auth.backends.google.GoogleOAuth2Backend',
    #'social_auth.backends.google.GoogleBackend',
    #'social_auth.backends.yahoo.YahooBackend',
    #'social_auth.backends.contrib.linkedin.LinkedinBackend',
    #'social_auth.backends.contrib.LiveJournalBackend',
    #'social_auth.backends.contrib.orkut.OrkutBackend',
    #'social_auth.backends.OpenIDBackend',
)

# Override these in settings_local.py
FACEBOOK_APP_ID          = ''
FACEBOOK_API_SECRET      = ''

# Fill these out if you enable any other backends
#TWITTER_CONSUMER_KEY     = ''
#TWITTER_CONSUMER_SECRET  = ''
#LINKEDIN_CONSUMER_KEY    = ''
#LINKEDIN_CONSUMER_SECRET = ''
#ORKUT_CONSUMER_KEY       = ''
#ORKUT_CONSUMER_SECRET    = ''
#GOOGLE_CONSUMER_KEY      = ''
#GOOGLE_CONSUMER_SECRET   = ''


# Not part of social_auth, mostly for my own backend
# Override these for your own app in settings_local.py
FACEBOOK_APPLICATION_ID = ''
FACEBOOK_APPLICATION_SECRET_KEY = ''
FACEBOOK_APPLICATION_API_KEY = ''


LOGIN_URL          = '/login/facebook/'
LOGIN_REDIRECT_URL = '/vocab/'
LOGIN_ERROR_URL    = '/login-error/'

SOCIAL_AUTH_COMPLETE_URL_NAME  = 'complete'
SOCIAL_AUTH_ASSOCIATE_URL_NAME = 'associate_complete'

SOCIAL_AUTH_DEFAULT_USERNAME = 'new_social_auth_user'

FACEBOOK_EXTENDED_PERMISSIONS = ["email"]




STATIC_URL = "/static/"
STATIC_ROOT =  os.path.join(PROJECT_PATH,"static")
STATICFILES_DIRS = [
    os.path.join(PROJECT_PATH,"common_static"),
]

# Used for making the facebook redirect URLs
THIS_HOST = "http://www.prepfly.com"

try:
    from settings_local import *
except Exception:
    pass
