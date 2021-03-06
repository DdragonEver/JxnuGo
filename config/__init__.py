# coding: utf-8

import os
basedir = os.path.abspath(os.path.dirname(__file__))

try:
    from .config import *
except ImportError:
    from .config_sample import *


class Config(object):
    SECRET_KEY = FLASK['SECRET_KEY']
    SQLALCHEMY_COMMIT_ON_TEARDOWN = FLASK['SQLALCHEMY_COMMIT_ON_TEARDOWN']
    JXNUGO_MAIL_SUBJECT_PREFIX = FLASK['JXNUGO_MAIL_SUBJECT_PREFIX']
    JXNUGO_MAIL_SENDER = FLASK['JXNUGO_MAIL_SENDER']
    JXNUGO_ADMIN = FLASK['JXNUGO_ADMIN']
    SQLALCHEMY_DATABASE_URI = FLASK['SQLALCHEMY_DATABASE_URI']
    JXNUGO_POSTS_PER_PAGE = JXNUGO['JXNUGO_POSTS_PER_PAGE']

    @staticmethod
    def init_app(app):
        pass


class DevelopmentConfig(Config):
    MAIL_SERVER = MAIL['MAIL_SERVER']
    MAIL_PORT = MAIL['MAIL_PORT']
    MAIL_USE_TLS = MAIL['MAIL_USE_TLS']
    MAIL_USERNAME = MAIL['MAIL_USERNAME']
    MAIL_PASSWORD = MAIL['MAIL_PASSWORD']
    DEBUG = True


class TestingConfig(Config):
    TESTING = True


class ProductionConfig(Config):
    TESTING = False


configs = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig,
}
