import os


class Config:
    DEBUG = False
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    # jwt config
    JWT_BLACKLIST_ENABLED = True
    JWT_BLACKLIST_TOKEN_CHECKS = ["access", "refresh"]
    JWT_ERROR_MESSAGE_KEY = "message"
    UPLOAD_AVATARS_FOLDER = "static/images/avatars"
    UPLOAD_RECIPES_FOLDER = "static/images/recipes"
    # smtp server configuration
    MAIL_SERVER = os.environ.get(MAIL_SERVER)
    MAIL_PORT = 587
    MAIL_USE_TLS = True
    MAIL_USERNAME = "apikey"
    MAIL_PASSWORD = os.environ.get("SENDGRID_API_KEY")
    MAIL_DEFAULT_SENDER = os.environ.get("MAIL_DEFAULT_SENDER")
    # upload files config
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024
    # caching:
    CACHE_TYPE = "simple"
    CACHE_DEFAULT_TIMEOUT = 10 * 60
    RATELIMIT_HEADERS_ENABLED = True


class DevelopmentConfig(Config):
    DEBUG = True
    SECRET_KEY = "super secret key"
    SQLALCHEMY_DATABASE_URI = "postgres://postgres:1qa2ws3ed@localhost:5432/smilecook"


class ProductionConfig(Config):
    SECRET_KEY = os.environ.get("SECRET_KEY")
    SQLALCHEMY_DATABASE_URI = os.environ.get("DATABASE_URL")


class StagingConfig(Config):
    SECRET_KEY = os.environ.get("SECRET_KEY")
    SQLALCHEMY_DATABASE_URI = os.environ.get("DATABASE_URL")

