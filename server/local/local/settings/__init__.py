"""
The HOSTMAP variable is a dictionary of lists, the keys representing
roles of a server, the values representing the hostnames of machines that
fill those roles.

You can get your hostname by typing `hostname` into a terminal.
"""
from __future__ import unicode_literals

import re
import os
import sys
import socket
import warnings

from django.utils.importlib import import_module

IMPORTED_SETTINGS_MODULES = []


def _load_settings(settings_module_list):
    """ Loads up all the settings from the settings module list given """

    for setting_module in settings_module_list:
        new_settings_path = 'local.settings.{0}'.format(setting_module)

        try:
            new_settings = import_module(new_settings_path)
        except ImportError:
            warnings.warn("Failed to import {0}".format(new_settings_path))
            raise
        else:
            IMPORTED_SETTINGS_MODULES.append(new_settings_path)
            sys.stdout.write("`{0}` setting module loaded successfully.\n".format(new_settings_path))

            for k, v in new_settings.__dict__.items():
                globals().update({k: v})


to_load = ['default']

#############################
# HOSTNAME BASED SETTINGS   #
#############################
DAVIDE_DEV_MACHINE = 'iRule.local'
DOTCLOUD = '^local-default-www'
PRODUCTION = 'hemera'

# hostname map to settings modules
# you can even have regular expressions to match hostnames now
HOSTMAP = (
    # settings loaded for all developers
    ('development', (
        DAVIDE_DEV_MACHINE,
    )),
    ('dotcloud', (
        DOTCLOUD,
    )),
    ('production', (
        PRODUCTION,
    )),
    ('late', ("*",)),
)

#########################################
# ENVIRONMENT VARIABLE BASED SETTINGS   #
#########################################
if 'ON_HEROKU' in os.environ:
    to_load.append('heroku')

if 'OPENSHIFT_REPO_DIR' in os.environ:
    to_load.append('openshift')

if 'TRAVIS_PYTHON_VERSION' in os.environ:
    to_load.append('development')

# retrieve all the settings based on the hostmap
hostname = socket.gethostname()
for settings_module, hostnames in HOSTMAP:
    if hostname in hostnames or '*' in hostnames:
        to_load.append(settings_module)
    else:
        # regular expression matching
        for name in hostnames:
            if re.match(name, hostname):
                to_load.append(settings_module)

_load_settings(to_load)
