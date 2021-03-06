# Django settings for ASHMC project.
import django.template

import local_settings

from twitter import Twitter, OAuth

VERSION = "20130401"

django.template.add_to_builtins('django.templatetags.future')

DEBUG = local_settings.DEBUG
TEMPLATE_DEBUG = local_settings.TEMPLATE_DEBUG

ADMINS = local_settings.ADMINS

MANAGERS = ADMINS

DATABASES = local_settings.DATABASES

TWITTER_USER = local_settings.TWITTER_USER
TWITTER_CACHE_TIMEOUT = local_settings.TWITTER_CACHE_TIMEOUT
TWITTER_ACCESS = local_settings.TWITTER_ACCESS
TWITTER_ACCESS_SECRET = local_settings.TWITTER_ACCESS_SECRET
TWITTER_CONSUMER = local_settings.TWITTER_CONSUMER
TWITTER_CONSUMER_SECRET = local_settings.TWITTER_CONSUMER_SECRET
TWITTER_AGENT = Twitter(auth=OAuth(TWITTER_ACCESS, TWITTER_ACCESS_SECRET,
                        TWITTER_CONSUMER, TWITTER_CONSUMER_SECRET))

BITLY_LOGIN = local_settings.BITLY_LOGIN
BITLY_API_KEY = local_settings.BITLY_API_KEY

GDOC_EMAIL = local_settings.GDOC_EMAIL
GDOC_PASSWORD = local_settings.GDOC_PASSWORD
GDOC_SOURCE = local_settings.GDOC_SOURCE
GDOC_URL = local_settings.GDOC_URL

LOGIN_REDIRECT_URL = "/"

# Local time zone for this installation. Choices can be found here:
# http://en.wikipedia.org/wiki/List_of_tz_zones_by_name
# although not all choices may be available on all operating systems.
# In a Windows environment this must be set to your system time zone.
TIME_ZONE = 'America/Los_Angeles'

# Language code for this installation. All choices can be found here:
# http://www.i18nguy.com/unicode/language-identifiers.html
LANGUAGE_CODE = 'en-us'

SITE_ID = 1

# If you set this to False, Django will make some optimizations so as not
# to load the internationalization machinery.
USE_I18N = False

# If you set this to False, Django will not format dates, numbers and
# calendars according to the current locale.
USE_L10N = True

# If you set this to False, Django will not use timezone-aware datetimes.
USE_TZ = True

# Absolute filesystem path to the directory that will hold user-uploaded files.
# Example: "/home/media/media.lawrence.com/media/"
MEDIA_ROOT = local_settings.MEDIA_ROOT

# URL that handles the media served from MEDIA_ROOT. Make sure to use a
# trailing slash.
# Examples: "http://media.lawrence.com/media/", "http://example.com/media/"
MEDIA_URL = '/media/'
ADMIN_MEDIA_PREFIX = '/static/admin/'
# Absolute path to the directory static files should be collected to.
# Don't put anything in this directory yourself; store your static files
# in apps' "static/" subdirectories and in STATICFILES_DIRS.
# Example: "/home/media/media.lawrence.com/static/"
STATIC_ROOT = local_settings.STATIC_ROOT

# URL prefix for static files.
# Example: "http://media.lawrence.com/static/"
STATIC_URL = '/static/'

# Additional locations of static files
STATICFILES_DIRS = (
    # Put strings here, like "/home/html/static" or "C:/www/django/static".
    # Always use forward slashes, even on Windows.
    # Don't forget to use absolute paths, not relative paths.
    #,
)

# List of finder classes that know how to find static files in
# various locations.
STATICFILES_FINDERS = (
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
#    'django.contrib.staticfiles.finders.DefaultStorageFinder',
)

# Make this unique, and don't share it with anybody.
SECRET_KEY = local_settings.SECRET_KEY

# List of callables that know how to import templates from various sources.
TEMPLATE_LOADERS = (
    'django.template.loaders.filesystem.Loader',
    'django.template.loaders.app_directories.Loader',
#     'django.template.loaders.eggs.Loader',
)

TEMPLATE_CONTEXT_PROCESSORS = (
    "django.contrib.auth.context_processors.auth",
    "django.core.context_processors.debug",
    "django.core.context_processors.i18n",
    "django.core.context_processors.media",
    "django.core.context_processors.static",
    "django.contrib.messages.context_processors.messages",
    "django.core.context_processors.request",
    "ASHMC.context_processors.add_login_form",
)

MIDDLEWARE_CLASSES = (
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    #'middleware.LoginRequiredMiddleware.LoginRequiredMiddleware', # force login for all pages except urls in PUBLIC_URLS
    # Uncomment the next line for simple clickjacking protection:
    #'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'django.contrib.flatpages.middleware.FlatpageFallbackMiddleware',
    'debug_toolbar.middleware.DebugToolbarMiddleware',
    'ASHMC.middleware.ImpersonateMiddleware.ImpersonateMiddleware',
)

INTERNAL_IPS = local_settings.INTERNAL_IPS

ROOT_URLCONF = 'ASHMC.urls'

# Python dotted path to the WSGI application used by Django's runserver.
WSGI_APPLICATION = 'ASHMC.wsgi.application'

TEMPLATE_DIRS = local_settings.TEMPLATE_DIRS

# This is required for object_permissions testing.
TESTING = local_settings.TESTING

AUTHENTICATION_BACKENDS = (
    'django_auth_ldap.backend.LDAPBackend',
    'django.contrib.auth.backends.ModelBackend',
)

AUTH_LDAP_SERVER_URI = local_settings.AUTH_LDAP_SERVER_URI
AUTH_LDAP_BIND_DN = local_settings.AUTH_LDAP_BIND_DN
AUTH_LDAP_BIND_PASSWORD = local_settings.AUTH_LDAP_BIND_PASSWORD
AUTH_LDAP_USER_SEARCH = local_settings.AUTH_LDAP_USER_SEARCH

AUTH_LDAP_USER_ATTR_MAP = local_settings.AUTH_LDAP_USER_ATTR_MAP
AUTH_LDAP_ALWAYS_UPDATE_USER = local_settings.AUTH_LDAP_ALWAYS_UPDATE_USER

AUTH_LDAP_START_TLS = True
ROSTER_DIRECTORY = local_settings.ROSTER_DIRECTORY
ROSTER_ROW_START = local_settings.ROSTER_ROW_START
ROSTER_FIELD_ORDERING = local_settings.ROSTER_FIELD_ORDERING

INSTALLED_APPS = (
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.comments',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.markup',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.webdesign',
    'django.contrib.flatpages',
    'django.contrib.humanize',
    # Uncomment the next line to enable the admin:
    'django.contrib.admin',
    # Uncomment the next line to enable admin documentation:
    'django.contrib.admindocs',

    'taggit',
    'mptt',
    'debug_toolbar',

    'ASHMC.main',  # landing page handler
    'ASHMC.courses',
    'blogger',
    'ASHMC.vote',
    'ASHMC.legal',
    'ASHMC.roster',
    'ASHMC.events',
    'ASHMC.treasury'
)

# A sample logging configuration. The only tangible logging
# performed by this configuration is to send an email to
# the site admins on every HTTP 500 error when DEBUG=False.
# See http://docs.djangoproject.com/en/dev/topics/logging for
# more details on how to customize your logging configuration.
SERVER_EMAIL = local_settings.SERVER_EMAIL
LOGGING = local_settings.LOGGING

ASHMC_FORMS_FOLDER = local_settings.ASHMC_FORMS_FOLDER
AMAZON_ASSOCIATES_REDIRECT_URL = local_settings.AMAZON_ASSOCIATES_REDIRECT_URL

EMAIL_BACKEND = local_settings.EMAIL_BACKEND
