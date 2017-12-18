"""Settings for production environment."""
from server.conf.settings import *

######################################################################
# Evennia Database config
######################################################################

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': 'foxhole',
        'USER': 'foxhole',
        'PASSWORD': PRODUCTION_DB_PASSWORD,
        'HOST': 'localhost',
        'PORT': '',    # use default
    },
}

DEBUG = False
