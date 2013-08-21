# -*- coding: utf-8 -*-
# OPENSHIFT
from __future__ import unicode_literals

import os, openshiftlibs

from local.settings import PROJECT_ROOT

# a setting to determine whether we are running on OpenShift
ON_OPENSHIFT = True

#PROJECT_ROOT = os.path.dirname(os.path.realpath(__file__))

# os.environ['OPENSHIFT_MYSQL_DB_*'] variables can be used with databases created
# with rhc app cartridge add (see /README in this git repo)
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': 'local',
        'USER': 'admin',
        'PASSWORD': 'XnCFGYw9n1SL',
        'HOST': os.environ['OPENSHIFT_POSTGRESQL_DB_HOST'],
        'PORT': os.environ['OPENSHIFT_POSTGRESQL_DB_PORT'],
    }
}

MEDIA_ROOT = os.environ.get('OPENSHIFT_DATA_DIR', '')
MEDIA_URL = ''

STATIC_ROOT = os.path.join(PROJECT_ROOT, '..', 'static')
STATIC_URL = '/static/'

#ADMIN_MEDIA_PREFIX = '/static/admin/'

# Replace default keys with dynamic values if we are in OpenShift
USE_KEYS = openshiftlibs.openshift_secure({
    'SECRET_KEY': 'vm4rl5*ymb@2&d_(gc$gb-^twq9w(u69hi--%$5xrh!xk(t%hw',
})

# Make this unique, and don't share it with anybody.
SECRET_KEY = USE_KEYS['SECRET_KEY']