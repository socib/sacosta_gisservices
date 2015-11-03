# -*- config:utf-8 -*-

import logging
from datetime import timedelta

project_name = "gisservices"


class Config(object):
    # use DEBUG mode?
    DEBUG = False

    # use TESTING mode?
    TESTING = False

    # use server x-sendfile?
    USE_X_SENDFILE = False

    # DATABASE CONFIGURATION
    # Defined at local_config.py
    # (not in git repository. local_config is called by GISSERVICES_CONFIG envvar)
    DATABASE_URI = "dbname=DBNAME host=HOST port=PORT user=USER password=PASSWORD"

    CSRF_ENABLED = True
    SECRET_KEY = "secret"  # import os; os.urandom(24)

    # LOGGING
    LOGGER_NAME = "/tmp/%s_log" % project_name
    LOG_FILENAME = "/tmp/%s.log" % project_name
    LOG_LEVEL = logging.INFO
    LOG_FORMAT = "%(asctime)s %(levelname)s\t: %(message)s"  # used by logging.Formatter

    PERMANENT_SESSION_LIFETIME = timedelta(days=1)

    # EMAIL CONFIGURATION
    MAIL_SERVER = "localhost"
    MAIL_PORT = 25
    MAIL_USE_TLS = False
    MAIL_USE_SSL = False
    MAIL_DEBUG = False
    MAIL_USERNAME = None
    MAIL_PASSWORD = None
    DEFAULT_MAIL_SENDER = "example@%s.com" % project_name

    # see example/ for reference
    # ex: BLUEPRINTS = ['blog.app']  # where app is a Blueprint instance
    # ex: BLUEPRINTS = [('blog.app', {'url_prefix': '/myblog'})]
    # where app is a Blueprint instance
    BLUEPRINTS = ['services.app']

    # Map layers. Ordered from bottom layer to top layer
    MAP_LAYERS = {
        'proteccion': [
            'sa:mean_atlas_land',
            'ge:bal_municipios',
            'ideib:batimetria20M',
            'ideib:toponimia100M',
            'sa:mca_protection_test',
            'sa:cab_protection_2015',
            'sa:men_protection_2015',
            'sa:pit_protection_2015'],
        'sacosta': [
            'sa:mean_atlas_land',
            'ge:bal_municipios',
            'ideib:batimetria20M',
            'ideib:toponimia100M',
            'sa:bal_sa_costa_2012']
    }
    # Defined at local_config.py
    SENTRY_DSN = ''


class Dev(Config):
    DEBUG = True
    MAIL_DEBUG = True
    LOGGER_NAME = "log/%s_log" % project_name
    LOG_FILENAME = "log/%s.log" % project_name


class Testing(Config):
    TESTING = True
    CSRF_ENABLED = False
