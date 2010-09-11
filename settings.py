# Django settings for newdominion project.

DEBUG = False 
TEMPLATE_DEBUG = DEBUG

ADMINS = (
    # ('Your Name', 'your_email@domain.com'),
)

MANAGERS = ADMINS
LOGIN_URL = '/accounts/login'
DATABASE_ENGINE = 'postgresql_psycopg2'           # 'postgresql_psycopg2', 'postgresql', 'mysql', 'sqlite3' or 'oracle'.
DATABASE_NAME = 'dav3xor_'             # Or path to database file if using sqlite3.
DATABASE_USER = 'dav3xor_'             # Not used with sqlite3.
DATABASE_PASSWORD = '114sobel'         # Not used with sqlite3.
DATABASE_HOST = ''             # Set to empty string for localhost. Not used with sqlite3.
DATABASE_PORT = ''             # Set to empty string for default. Not used with sqlite3.

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
MEDIA_ROOT = '/home/dav3xor/webapps/game/newdominion/static/'

# URL that handles the media served from MEDIA_ROOT. Make sure to use a
# trailing slash if there is a path component (optional in other cases).
# Examples: "http://media.lawrence.com", "http://example.com/media/"
MEDIA_URL = '/site_media/'

# URL prefix for admin media -- CSS, JavaScript and images. Make sure to use a
# trailing slash.
# Examples: "http://foo.com/media/", "/media/".
ADMIN_MEDIA_PREFIX = '/media/'

# Make this unique, and don't share it with anybody.
SECRET_KEY = '+@!t&$(bsn=n4vu@!3ve9f^8#mbgat8vs0^3mi1q3vn!jzda$!'

# List of callables that know how to import templates from various sources.
TEMPLATE_LOADERS = (
    'django.template.loaders.filesystem.load_template_source',
    'django.template.loaders.app_directories.load_template_source',
#     'django.template.loaders.eggs.load_template_source',
)

MIDDLEWARE_CLASSES = (
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
)

ROOT_URLCONF = 'newdominion.urls'

TEMPLATE_DIRS = (
    "/home/dav3xor/webapps/game/newdominion/dominion/templates/registration",
    "/home/dav3xor/webapps/game/newdominion/dominion",
    "/home/dav3xor/webapps/game/newdominion/prank",
    # Put strings here, like "/home/html/django_templates" or "C:/www/django/templates".
    # Always use forward slashes, even on Windows.
    # Don't forget to use absolute paths, not relative paths.
)
AUTH_PROFILE_MODULE = 'dominion.player'

INSTALLED_APPS = (
    'django.contrib.markup',
    'registration',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.admin',
    'newdominion.dominion',
    'newdominion.prank'
)


EMAIL_HOST = 'smtp.webfaction.com'
EMAIL_HOST_USER = 'dav3xor'
EMAIL_HOST_PASSWORD = '341c1d10'
DEFAULT_FROM_EMAIL = 'admin@davesgalaxy.com'
SERVER_EMAIL = 'admin@davesgalaxy.com'
#EMAIL_USE_TLS = True
