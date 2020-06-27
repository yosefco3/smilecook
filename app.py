import os
from flask import Flask
from flask_migrate import Migrate
from flask_restful import Api
from extensions import db, jwt, mail
from resources.user import (
    UserListResource,
    UserResource,
    MeResource,
    UserActivateResource,
    UserAvatarUploadResource,
    UserRecipeListResource,
)
from resources.recipe import (
    RecipeListResource,
    RecipeResource,
    RecipePublishResource,
    RecipeCoverUploadResource,
)
from resources.token import TokenResource, RefreshResource, black_list, RevokeResource


def create_app():
    app = Flask(__name__)
    configurations(app)
    register_extensions(app)
    register_resources(app)
    return app


def configurations(app):
    app.config["SECRET_KEY"] = os.getenv("SECRET_KEY")
    # db config
    app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv("SQLALCHEMY_DATABASE_URI")
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    # jwt config
    app.config["JWT_BLACKLIST_ENABLED"] = True
    app.config["JWT_BLACKLIST_TOKEN_CHECKS"] = ["access", "refresh"]
    # smtp server configuration
    app.config["MAIL_SERVER"] = "smtp.sendgrid.net"
    app.config["MAIL_PORT"] = 587
    app.config["MAIL_USE_TLS"] = True
    app.config["MAIL_USERNAME"] = "apikey"
    app.config["MAIL_PASSWORD"] = os.environ.get("SENDGRID_API_KEY")
    app.config["MAIL_DEFAULT_SENDER"] = os.environ.get("MAIL_DEFAULT_SENDER")
    # upload files config
    app.config["UPLOAD_FOLDER"] = "static/images"
    app.config["MAX_CONTENT_LENGTH"] = 16 * 1024 * 1024


def register_extensions(app):
    db.init_app(app)
    migrate = Migrate(app, db)
    jwt.init_app(app)
    mail.init_app(app)

    @jwt.token_in_blacklist_loader
    def check_if_token_in_blacklist(decrepted_token):
        jti = decrepted_token["jti"]
        return jti in black_list


def register_resources(app):
    api = Api(app)
    api.add_resource(UserListResource, "/users")
    api.add_resource(UserResource, "/users/<string:username>")
    api.add_resource(MeResource, "/me")
    api.add_resource(TokenResource, "/token")
    api.add_resource(RecipeListResource, "/recipes")
    api.add_resource(RecipeResource, "/recipes/<int:recipe_id>")
    api.add_resource(RecipePublishResource, "/recipes/<int:recipe_id>/publish")
    api.add_resource(RefreshResource, "/refresh")
    api.add_resource(RevokeResource, "/revoke")
    api.add_resource(UserActivateResource, "/users/activate/<string:token>")
    api.add_resource(UserAvatarUploadResource, "/users/avatar")
    api.add_resource(RecipeCoverUploadResource, "/recipes/<int:recipe_id>/cover")
    api.add_resource(UserRecipeListResource, "/<string:username>/recipes")


if __name__ == "__main__":
    app = create_app()
    app.run()
