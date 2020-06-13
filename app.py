import os
from flask import Flask
from flask_migrate import Migrate
from flask_restful import Api
from extensions import db, jwt
from resources.user import UserListResource, UserResource, MeResource
from resources.recipe import RecipeListResource, RecipeResource, RecipePublishResource
from resources.token import TokenResource, RefreshResource, black_list, RevokeResource


def create_app():
    app = Flask(__name__)
    configurations(app)
    register_extensions(app)
    register_resources(app)
    return app


def configurations(app):
    app.config["SECRET_KEY"] = os.getenv("SECRET_KEY")
    app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv("SQLALCHEMY_DATABASE_URI")
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    app.config["JWT_BLACKLIST_ENABLED"] = True
    app.config["JWT_BLACKLIST_TOKEN_CHECKS"] = ["access", "refresh"]


def register_extensions(app):
    db.init_app(app)
    migrate = Migrate(app, db)
    jwt.init_app(app)

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


if __name__ == "__main__":
    app = create_app()
    app.run()
