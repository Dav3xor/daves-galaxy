# Django settings for newdominion project.

from gamesettings import *
import os

BASE_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'dg')

DEBUG = True
STATIC_URL = '/site_media/'
print BASE_DIR
print os.path.join(BASE_DIR, 'static')
STATICFILES_DIRS = (os.path.join(BASE_DIR, 'static'),)
TEMPLATE_DEBUG = True
DEBUG_PRINT = False
STAGING = False

ADMINS = (
     ('David Case', 'Dav3xor@gmail.com'),
)

MANAGERS = ADMINS
LOGIN_URL = '/accounts/login'

DATABASES = {
 'default': {
              #'ENGINE': 'django.db.backends.sqlite3',
              #'NAME': '/home/djdjango/newdominion/dg.sqlite3'
              'ENGINE': 'django.db.backends.postgresql_psycopg2',
              'NAME': '{{ dbname }}',
      	      'USER': '{{ dbuser }}',
              'PASSWORD': '{{ dbpassword }}',
              'HOST': 'localhost'
 }
}



# Local time zone for this installation. Choices can be found here:
# http://en.wikipedia.org/wiki/List_of_tz_zones_by_name
# although not all choices may be available on all operating systems.
# If running in a Windows environment this must be set to the same as your
# system time zone.
TIME_ZONE = 'America/Vancouver'

# for the user registration app...
ACCOUNT_ACTIVATION_DAYS = 3

# Language code for this installation. All choices can be found here:
# http://www.i18nguy.com/unicode/language-identifiers.html
LANGUAGE_CODE = 'en-us'

SITE_ID = 1

# If you set this to False, Django will make some optimizations so as not
# to load the internationalization machinery.
USE_I18N = True

# Absolute path to the directory that holds media.
# Example: "/home/media/media.lawrence.com/"
MEDIA_ROOT = os.path.join(BASE_DIR, 'static')

# URL that handles the media served from MEDIA_ROOT. Make sure to use a
# trailing slash if there is a path component (optional in other cases).
# Examples: "http://media.lawrence.com", "http://example.com/media/"
#MEDIA_URL = '/site_media/'

# URL prefix for admin media -- CSS, JavaScript and images. Make sure to use a
# trailing slash.
# Examples: "http://foo.com/media/", "/media/".
ADMIN_MEDIA_PREFIX = '/site_media/admin/'

# Make this unique, and don't share it with anybody.
SECRET_KEY = '+@!t&$(bsn=n4vu@!3ve9f^8#mbgat8vs0^3mi1q3vn!jzda$!'

# List of callables that know how to import templates from various sources.
TEMPLATE_LOADERS = (
    'django.template.loaders.filesystem.Loader',
    'django.template.loaders.app_directories.Loader',
#     'django.template.loaders.eggs.load_template_source',
)

MIDDLEWARE_CLASSES = (
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
)

ROOT_URLCONF = 'newdominion.urls'

TEMPLATE_DIRS = (
    os.path.join(BASE_DIR, 'dominion', 'templates', 'registration'),
    os.path.join(BASE_DIR, 'dominion'),
    os.path.join(BASE_DIR, 'prank')
    # Put strings here, like "/home/html/django_templates" or "C:/www/django/templates".
    # Always use forward slashes, even on Windows.
    # Don't forget to use absolute paths, not relative paths.
)
AUTH_PROFILE_MODULE = 'dominion.player'

INSTALLED_APPS = (
    'django.contrib.auth',
    'django.contrib.admin',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.staticfiles',
    'django.contrib.sites',
    'markup_deprecated',
    'registration',
    'newdominion.dominion',
)

NEW_PLAYER_SCRIPT = os.path.join(BASE_DIR, 'dominion', 'newplayer.py')

REPORTDIR = os.path.join(BASE_DIR, 'dominion', 'reports')
REPORTMAXFILES = 2000

GALAXY_MAP_LOCATION = os.path.join(BASE_DIR, 'static', 'galaxy2.png')
GALAXY_MAP_OUTPUT =   os.path.join(BASE_DIR, 'static', 'galaxyownership.png')
GALAXY_MAP_BACKUPDIR = '/home/djdjango/oldmaps/'

EMAIL_HOST = 'localhost'
EMAIL_HOST_USER = ''
EMAIL_HOST_PASSWORD = ''
DEFAULT_FROM_EMAIL = 'admin@davesgalaxy.com'
SERVER_EMAIL = 'admin@davesgalaxy.com'
#EMAIL_USE_TLS = True
