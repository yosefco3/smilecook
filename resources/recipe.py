from flask import request
from flask_restful import Resource
from http import HTTPStatus
from models.recipe import Recipe
from flask_jwt_extended import get_jwt_identity, jwt_required, jwt_optional
from schemas.recipe import RecipeSchema

recipe_schema = RecipeSchema()
recipe_list_schema = RecipeSchema(many=True)


class RecipeListResource(Resource):
    def get(self):
        recipes = Recipe.get_all_published()
        return recipe_list_schema.dump(recipes), HTTPStatus.OK

    @jwt_required
    def post(self):
        json_data = request.get_json()
        current_user = get_jwt_identity()
        try:
            data = recipe_schema.load(data=json_data)
        except Exception as errors:
            return (
                {"message": "Validation error", "errors": errors.messages},
                HTTPStatus.BAD_REQUEST,
            )
        recipe = Recipe(**data)
        recipe.user_id = current_user
        recipe.save()
        return recipe_schema.dump(recipe), HTTPStatus.CREATED


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
    def patch(self, recipe_id):
        json_data = request.get_json()
        try:
            data = recipe_schema.load(data=json_data, partial=("name",))
        except Exception as errors:
            return (
                {"message": "Validation errors", "errors": errors.messages},
                HTTPStatus.BAD_REQUEST,
            )
        recipe = Recipe.get_by_id(recipe_id=recipe_id)
        if recipe is None:
            return {"message": "Recipe not found"}, HTTPStatus.NOT_FOUND
        current_user = get_jwt_identity()
        if current_user != recipe.user_id:
            return {"message": "access is not allowed."}, HTTPStatus.FORBIDDEN
        # updates object with dicts attributes !
        for key, value in data.items():
            setattr(recipe, key, value)

        recipe.save()
        return recipe_schema.dump(recipe), HTTPStatus.OK

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
