'''
Django settings for annotation tool (at) project.

For more information on this file, see
https://docs.djangoproject.com/en/1.10/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.10/ref/settings/
'''

import os
from django.utils.translation import ugettext_lazy as _

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
REPOSITORY_ROOT = os.path.dirname(BASE_DIR)
PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))

DEBUG = False
ALLOWED_HOSTS = [
    '127.0.0.1',
    'localhost',
    '.amazonaws.com',
    '.elasticbeanstalk.com',
]

def is_ec2_linux():
    """Detect if we are running on an EC2 Linux Instance
       See http://docs.aws.amazon.com/AWSEC2/latest/UserGuide/identify_ec2_instances.html
    """
    if os.path.isfile("/sys/hypervisor/uuid"):
        with open("/sys/hypervisor/uuid") as f:
            uuid = f.read()
            return uuid.startswith("ec2")
    return False

def get_linux_ec2_private_ip():
    """Get the private IP Address of the machine if running on an EC2 linux server"""
    import requests
    if not is_ec2_linux():
        return None
    try:
        return requests.get('http://169.254.169.254/latest/meta-data/local-ipv4').text
    except requests.exceptions.RequestException:
        pass

# ElasticBeanstalk healthcheck sends requests with host header = internal ip
# So we detect if we are in elastic beanstalk,
# and add the instances private ip address
private_ip = get_linux_ec2_private_ip()
if private_ip:
    ALLOWED_HOSTS.append(private_ip)

# See https://docs.djangoproject.com/en/1.10/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.getenv('DJANGO_SECRET_KEY', 'wszg)r-z!2--b2d5+%ik6z&!ey+ga9m=(15ds+i2e%jcqiz_5r')

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = os.getenv('DEBUG', 'NO').lower() in ('on', 'true', 'y', 'yes')


ADMINS = (('Serkan Sokmen', 'e.serkan.sokmen@gmail.com'), )


# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    # 'whitenoise.runserver_nostatic',
    'django.contrib.staticfiles',
    'django_extensions',
    'django_filters',
    'corsheaders',
    'storages',
    'rest_framework',
    'rest_framework.authtoken',
    'rest_auth',
    'drf_extra_fields',
    'multiselectfield',

    'sorl.thumbnail',
    'sorl_thumbnail_serializer',
    'crispy_forms',

    'flickr.apps.FlickrConfig',
]

MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.locale.LocaleMiddleware',
    # 'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.middleware.common.CommonMiddleware',
    'corsheaders.middleware.CorsPostCsrfMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'fat.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [
            os.path.join(BASE_DIR, '..', 'templates'),
        ],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.i18n',
                'django.template.context_processors.csrf',
                'django.template.context_processors.request',
                'django.template.context_processors.static',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'fat.wsgi.application'


# Database
# https://docs.djangoproject.com/en/1.10/ref/settings/#databases
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': os.getenv('RDS_DB_NAME'),
        'USER': os.getenv('RDS_USERNAME'),
        'PASSWORD': os.getenv('RDS_PASSWORD'),
        'HOST': os.getenv('RDS_HOSTNAME'),
        'PORT': os.getenv('RDS_PORT'),
    }
}

# DATABASES = {
#     'default': dj_database_url.config(default=os.environ['DATABASE_URL'], conn_max_age=500)
# }

EMAIL_BACKEND = 'backends.smtp.EmailBackend'

STATIC_HOSTING_URL = os.getenv('STATIC_HOSTING_URL', 'http://localhost:4200')
CORS_ORIGIN_WHITELIST = (
    STATIC_HOSTING_URL,
)
CSRF_TRUSTED_ORIGINS = (
    STATIC_HOSTING_URL,
)
CORS_ORIGIN_ALLOW_ALL = False


# Subsrtitute User
# AUTH_USER_MODEL = 'flickr.User'

# Password validation
# https://docs.djangoproject.com/en/1.10/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

# AUTHENTICATION_BACKENDS = (
#     'django.contrib.auth.backends.ModelBackend',
# )

# Internationalization
# https://docs.djangoproject.com/en/1.10/topics/i18n/

LANGUAGE_CODE = 'en'
gettext_noop = lambda s: s
LANGUAGES = [
    ('en', gettext_noop('English')),
]

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True


# Extra places for collectstatic to find static files.
STATICFILES_FINDERS = (
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
)

AWS_HEADERS = {  # see http://developer.yahoo.com/performance/rules.html#expires
    'Expires': 'Thu, 31 Dec 2099 20:00:00 GMT',
    'Cache-Control': 'max-age=94608000',
}
AWS_STORAGE_BUCKET_NAME = os.getenv('AWS_STORAGE_BUCKET_NAME')
AWS_ACCESS_KEY_ID = os.getenv('AWS_ACCESS_KEY_ID')
AWS_SECRET_ACCESS_KEY = os.getenv('AWS_SECRET_ACCESS_KEY')

# Tell django-storages that when coming up with the URL for an item in S3 storage, keep
# it simple - just use this domain plus the path. (If this isn't set, things get complicated).
# This controls how the `static` template tag from `staticfiles` gets expanded, if you're using it.
# We also use it in the next setting.
AWS_S3_CUSTOM_DOMAIN = '%s.s3.amazonaws.com' % AWS_STORAGE_BUCKET_NAME

STATICFILES_LOCATION = 'static'
STATICFILES_STORAGE = 'fat.custom_storages.StaticStorage'
STATIC_URL = 'https://%s/%s/' % (AWS_S3_CUSTOM_DOMAIN, STATICFILES_LOCATION)
STATICFILES_BUCKET_NAME = AWS_STORAGE_BUCKET_NAME

MEDIAFILES_LOCATION = 'media'
MEDIA_URL = 'https://%s/%s/' % (AWS_S3_CUSTOM_DOMAIN, MEDIAFILES_LOCATION)
DEFAULT_FILE_STORAGE = 'fat.custom_storages.MediaStorage'
MEDIAFILES_BUCKET_NAME = AWS_STORAGE_BUCKET_NAME

CORS_ORIGIN_WHITELIST = ()
CSRF_TRUSTED_ORIGINS = ()
CORS_ORIGIN_ALLOW_ALL = True

REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework.authentication.BasicAuthentication',
        'rest_framework.authentication.SessionAuthentication',
        'rest_framework.authentication.TokenAuthentication',
    ),
    'DEFAULT_PERMISSION_CLASSES': (
        'rest_framework.permissions.IsAuthenticated',
    ),
    'DEFAULT_PARSER_CLASSES': (
        'rest_framework.parsers.JSONParser',
    ),
    'DEFAULT_FILTER_BACKENDS': ('django_filters.rest_framework.DjangoFilterBackend',),
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.LimitOffsetPagination',
    'PAGE_SIZE': 100
}


FLICKR_API_KEY = os.getenv('FLICKR_API_KEY')
FLICKR_API_SECRET = os.getenv('FLICKR_API_SECRET')
FORCE_LOWERCASE_TAGS = True
FLICKR_LICENSES = (
  (0, _('All Rights Reserved')),
  (1, _('Attribution-NonCommercial-ShareAlike License')),
  (2, _('Attribution-NonCommercial License')),
  (3, _('Attribution-NonCommercial-NoDerivs License')),
  (4, _('Attribution License')),
  (5, _('Attribution-ShareAlike License')),
  (6, _('Attribution-NoDerivs License')),
  (7, _('No known copyright restrictions')),
  (8, _('United States Government Work')),
)
FLICKR_LICENSE_URLS = (
  (0, ''),
  (1, 'http://creativecommons.org/licenses/by-nc-sa/2.0/'),
  (2, 'http://creativecommons.org/licenses/by-nc/2.0/'),
  (3, 'http://creativecommons.org/licenses/by-nc-nd/2.0/'),
  (4, 'http://creativecommons.org/licenses/by/2.0/'),
  (5, 'http://creativecommons.org/licenses/by-sa/2.0/'),
  (6, 'http://creativecommons.org/licenses/by-nd/2.0/'),
  (7, 'http://flickr.com/commons/usage/'),
  (8, 'http://www.usa.gov/copyright.shtml'),
)


# Send an email to the site admins
# on error when DEBUG=False,
# log to console on error always.
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
        },
    },
    'loggers': {
        'django': {
            'handlers': ['console'],
            'level': os.getenv('DJANGO_LOG_LEVEL', 'INFO'),
        },
    }
}
