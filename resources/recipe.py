from flask import request
from flask_restful import Resource
from http import HTTPStatus
from models.recipe import Recipe
from flask_jwt_extended import get_jwt_identity, jwt_required, jwt_optional
import os
from utils import save_image, allowed_file, clear_cache
from schemas.recipe import RecipeSchema, RecipePaginationSchema
from extensions import cache, limiter


recipe_schema = RecipeSchema()
recipe_list_schema = RecipeSchema(many=True)
recipe_cover_schema = RecipeSchema(only=("cover_url",))
recipe_pagination_schema = RecipePaginationSchema()


class RecipeListResource(Resource):
    decorators = [
        limiter.limit(
            "3 per minute", methods=["GET"], error_message="Too many requests"
        )
    ]

    @cache.cached(timeout=60, query_string=True)
    def get(self):
        sort = request.args.get("sort", "created_at")
        order = request.args.get("order", "desc")
        q = request.args.get("q", "")
        per_page = int(request.args.get("per_page", 10))
        page = int(request.args.get("page", 1))

        if sort not in ["created_at", "cook_time", "num_of_servings"]:
            sort = "created_at"
        if order not in ["asc", "desc"]:
            order = "desc"

        paginated_recipes = Recipe.get_all_published(q, page, per_page, order, sort)
        return recipe_pagination_schema.dump(paginated_recipes), HTTPStatus.OK

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
        return recipe_schema.dump(recipe), HTTPStatus.OK

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
        clear_cache("/recipes")
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
        clear_cache("/recipes")
        return {"recipe deleted": recipe.id}, HTTPStatus.OK


class RecipePublishResource(Resource):
    @jwt_required
    def put(self, recipe_id):
        recipe = Recipe.get_by_id(recipe_id=recipe_id)
        if recipe is None:
            return {"message": "recipe not found"}, HTTPStatus.NOT_FOUND
        recipe.is_publish = True
        recipe.save()
        clear_cache("/recipes")
        return {"message": "recipe published"}, HTTPStatus.OK

    @jwt_required
    def delete(self, recipe_id):
        recipe = Recipe.get_by_id(recipe_id=recipe_id)
        if recipe is None:
            return {"message": "recipe not found"}, HTTPStatus.NOT_FOUND
        recipe.is_publish = False
        recipe.save()
        clear_cache("/recipes")
        return {"message": "recipe will not published"}, HTTPStatus.OK


class RecipeCoverUploadResource(Resource):
    @jwt_required
    def put(self, recipe_id):
        # print(request.files)
        file = request.files.get("cover")
        if not file:
            return {"message": "Not a valid image"}, HTTPStatus.BAD_REQUEST
        if not allowed_file(file.filename):
            return {"message": "File type not allowed."}, HTTPStatus.BAD_REQUEST
        recipe = Recipe.get_by_id(recipe_id=recipe_id)
        if recipe is None:
            return {"message": "Recipe not found"}, HTTPStatus.NOT_FOUND
        current_user = get_jwt_identity()
        if current_user != recipe.user_id:
            return {"message": "Access is not allowed"}, HTTPStatus.FORBIDDEN

        if recipe.cover_image:
            cover_path = os.path.join(
                os.environ.get("UPLOAD_RECIPES_FOLDER"), recipe.cover_image
            )

            if os.path.exists(cover_path):
                os.remove(cover_path)
        filename = save_image(image=file, folder="recipes")
        recipe.cover_image = filename
        recipe.save()
        clear_cache("/recipes")
        return recipe_cover_schema.dump(recipe), HTTPStatus.OK

