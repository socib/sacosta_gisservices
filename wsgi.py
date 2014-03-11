activate_this = '/home/usernama/virtualenv_path/bin/activate_this.py'
execfile(activate_this, dict(__file__=activate_this))

import sys
sys.path.insert(0, '/var/www/gisservices')

from main import app_factory
from os import environ

import config

environ['GISSERVICES_CONFIG'] = '/var/www/gisservices/local_config.py'
application = app_factory(config.Config)
