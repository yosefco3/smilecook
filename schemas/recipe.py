from marshmallow import Schema, fields, post_dump, validate, validates, ValidationError
from schemas.user import UserSchema
from models.recipe import Recipe


class RecipeSchema(Schema):
    class Meta:
        ordered = True

    id = fields.Integer(dump_only=True)
    name = fields.String(required=True, validate=[validate.Length(max=200)])
    description = fields.String(validate=[validate.Length(max=200)])
    directions = fields.String(validate=[validate.Length(max=1000)])
    is_publish = fields.Boolean(dump_only=True)
    created_at = fields.DateTime(dump_only=True)
    updated_at = fields.DateTime(dump_only=True)
    num_of_servings = fields.Integer()
    cook_time = fields.Integer()
    author = fields.Nested(
        UserSchema, attribute="user", dump_only=True, only=["id", "username"]
    )

    @validates("num_of_servings")
    def validate_num_of_servings(self, n):
        if n < 1:
            raise ValidationError("Number of servings must be greater than 0.")
        if n > 50:
            raise ValidationError("Number of servings must not be greater than 50.")

    @validates("cook_time")
    def validates_cook_time(self, value):
        if value < 1 or value > 300:
            raise ValidationError("Cook time must be between 1 to 300 min.")

    @post_dump(pass_many=True)
    def wrap(self, data, many, **kwargs):
        if many:
            return {"data": data}
        return data

    @validates("name")
    def recipe_exists(self, name):
        if Recipe.query.filter(Recipe.name == name).first() is not None:
            raise ValidationError("Recipe name already exist")
