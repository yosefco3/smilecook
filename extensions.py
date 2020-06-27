from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager
from flask_mail import Mail
from flask_caching import Cache


db = SQLAlchemy()
jwt = JWTManager()
mail = Mail()
cache = Cache()
