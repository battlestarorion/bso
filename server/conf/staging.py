"""Settings for staging environment."""
from server.conf.settings import *
from secret_settings import *

######################################################################
# Evennia Database config
######################################################################

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': 'foxhole_staging',
        'USER': 'foxhole_staging',
        'PASSWORD': STAGING_DB_PASSWORD,
        'HOST': 'localhost',
        'PORT': '',    # use default
    },
}

DEBUG = False
