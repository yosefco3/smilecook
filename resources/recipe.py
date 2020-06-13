from flask import request
from flask_restful import Resource
from http import HTTPStatus
from models.recipe import Recipe
from flask_jwt_extended import get_jwt_identity, jwt_required, jwt_optional


class RecipeListResource(Resource):
    def get(self):
        recipes = Recipe.get_all_published()
        data = []
        for recipe in recipes:
            data.append(recipe.data())
        return {"data": data}, HTTPStatus.OK

    @jwt_required
    def post(self):
        json_data = request.get_json()
        current_user = get_jwt_identity()
        recipe = Recipe(**json_data, user_id=current_user)
        recipe.save()
        return recipe.data(), HTTPStatus.CREATED


class RecipeResource(Resource):
    @jwt_optional
    def get(self, recipe_id):
        recipe = Recipe.get_by_id(recipe_id)
        if recipe is None:
            return {"message": "recipe not found"}, HTTPStatus.NOT_FOUND
        current_user = get_jwt_identity()
        if recipe.is_publish == False and current_user != recipe.user_id:
            return {"message": "access not allowed"}, HTTPStatus.FORBIDDEN
        return recipe.data(), HTTPStatus.OK

    @jwt_required
    def put(self, recipe_id):
        json_data = request.get_json()
        recipe = Recipe.get_by_id(recipe_id=recipe_id)
        if recipe is None:
            return {"message": "recipe not found"}, HTTPStatus.NOT_FOUND
        current_user = get_jwt_identity()
        if current_user != recipe.user_id:
            return {"message": "access not allowed"}, HTTPStatus.FORBIDDEN

        recipe.__dict__ = {
            **json_data,
            "id": recipe.id,
            "is_publish": recipe.is_publish,
        }
        recipe.save()
        return recipe.data, HTTPStatus.OK

    @jwt_required
    def delete(self, recipe_id):
        recipe = Recipe.get_by_id(recipe_id=recipe_id)
        if recipe is None:
            return {"message": "recipe not found"}, HTTPStatus.NOT_FOUND
        current_user = get_jwt_identity()
        if current_user != recipe.user_id:
            return {"message": "access not allowed"}, HTTPStatus.FORBIDDEN
        recipe.delete()
        return {"recipe deleted": recipe.id}, HTTPStatus.OK


class RecipePublishResource(Resource):
    @jwt_required
    def put(self, recipe_id):
        recipe = Recipe.get_by_id(recipe_id=recipe_id)
        if recipe is None:
            return {"message": "recipe not found"}, HTTPStatus.NOT_FOUND
        recipe.is_publish = True
        recipe.save()
        return {"message": "recipe published"}, HTTPStatus.OK

    @jwt_required
    def delete(self, recipe_id):
        recipe = Recipe.get_by_id(recipe_id=recipe_id)
        if recipe is None:
            return {"message": "recipe not found"}, HTTPStatus.NOT_FOUND
        recipe.is_publish = False
        recipe.save()
        return {"message": "recipe will not published"}, HTTPStatus.OK
