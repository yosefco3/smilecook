import os
from flask import Flask
from flask_migrate import Migrate
from flask_restful import Api
from extensions import db
from models.user import User
from resources.recipe import RecipeListResource, RecipeResource, RecipePublishResource

# from flask_script import Manager


def create_app():
    app = Flask(__name__)
    app.config["SECRET_KEY"] = os.getenv("SECRET_KEY")
    app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv("SQLALCHEMY_DATABASE_URI")
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    register_extensions(app)
    register_resources(app)
    return app


def register_extensions(app):
    db.init_app(app)
    migrate = Migrate(app, db)
    # manager = Manager(app)
    # manager.add_command("db", MigrateCommand)


def register_resources(app):
    api = Api(app)
    api.add_resource(RecipeListResource, "/recipes")
    api.add_resource(RecipeResource, "/recipes/<int:recipe_id>")
    api.add_resource(RecipePublishResource, "/recipes/<int:recipe_id>/publish")


if __name__ == "__main__":
    app = create_app()
    app.run()
