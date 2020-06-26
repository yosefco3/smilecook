from marshmallow import Schema, fields, validates, ValidationError
from utils import hash_password
from models.user import User
from flask import url_for


class UserSchema(Schema):
    class Meta:
        ordered = True

    id = fields.Int(dump_only=True)
    username = fields.String(required=True)
    email = fields.Email(required=True)
    password = fields.Method(required=True, deserialize="load_password")
    created_at = fields.DateTime(dump_only=True)
    updated_at = fields.DateTime(dump_only=True)
    avatar_image = fields.Method(serialize="dump_avatar_url")

    def dump_avatar_url(self, user):
        if user.avatar_image:
            return url_for(
                "static", filename=f"images/avatars/{user.avatar_image}", _external=True
            )
        else:
            return url_for(
                "static", filename="images/assets/default_avatar.jpg", _external=True
            )

    def load_password(self, value):
        return hash_password(value)

    @validates("username")
    def username_exist(self, name):
        if User.query.filter(User.username == username).first() is not None:
            raise ValidationError("Username already exist")

    @validates("email")
    def username_exist(self, email):
        if User.query.filter(User.email == email).first() is not None:
            raise ValidationError("email already exist")
