from flask import request
from flask_restful import Resource
from http import HTTPStatus
from models.recipe import Recipe


class RecipeListResource(Resource):
    def get(self):
        data = []
        for recipe in Recipe.recipe_list:
            if recipe.is_publish is True:
                data.append(recipe.data)
        return {"data": data}, HTTPStatus.OK

    def post(self):
        data = request.get_json()
        recipe = Recipe(**data)
        Recipe.recipe_list.append(recipe)
        return recipe.data, HTTPStatus.CREATED


class RecipeResource(Resource):
    def get(self, recipe_id):
        recipe = next(
            (
                recipe
                for recipe in Recipe.recipe_list
                if recipe.id == recipe_id and recipe.is_publish == True
            ),
            None,
        )
        if recipe is None:
            return {"message": "recipe not found"}, HTTPStatus.NOT_FOUND
        return recipe.data, HTTPStatus.OK

    def put(self, recipe_id):
        data = request.get_json()
        recipe = next(
            (recipe for recipe in Recipe.recipe_list if recipe.id == recipe_id), None
        )
        if recipe is None:
            return {"message": "recipe not found"}, HTTPStatus.NOT_FOUND

        recipe.__dict__ = {**data, "id": recipe.id, "is_publish": recipe.is_publish}
        return recipe.data, HTTPStatus.OK

    def delete(self, recipe_id):
        recipe = next(
            (recipe for recipe in Recipe.recipe_list if recipe.id == recipe_id), None
        )
        if recipe is None:
            return {"message": "recipe not found"}, HTTPStatus.NOT_FOUND
        Recipe.recipe_list = list(
            recipe for recipe in Recipe.recipe_list if recipe.id != recipe_id
        )
        return {"recipe deleted": recipe.id}, HTTPStatus.OK


class RecipePublishResource(Resource):
    def put(self, recipe_id):
        recipe = next(
            (recipe for recipe in Recipe.recipe_list if recipe.id == recipe_id), None
        )
        if recipe is None:
            return {"message": "recipe not found"}, HTTPStatus.NOT_FOUND
        recipe.is_publish = True
        return {}, HTTPStatus.NO_CONTENT

    def delete(self, recipe_id):
        recipe = next(
            (recipe for recipe in Recipe.recipe_list if recipe.id == recipe_id), None
        )
        if recipe is None:
            return {"message": "recipe not found"}, HTTPStatus.NOT_FOUND
        recipe.is_publish = False
        return {}, HTTPStatus.NO_CONTENT
