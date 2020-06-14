from flask import request
from flask_restful import Resource
from http import HTTPStatus
from models.user import User
from utils import hash_password
from flask_jwt_extended import jwt_optional, get_jwt_identity, jwt_required
from schemas.user import UserSchema


user_schema = UserSchema()

user_public_schema = UserSchema(exclude=("email",))


class UserListResource(Resource):
    def post(self):
        json_data = request.get_json()
        try:
            data = user_schema.load(data=json_data)
        except Exception as errors:
            return (
                {"message": "Validation errors", "errors": errors.messages},
                HTTPStatus.BAD_REQUEST,
            )
        if User.get_by_username(data.get("username")):
            return {"message": " Username already used"}, HTTPStatus.BAD_REQUEST
        if User.get_by_email(data.get("email")):
            return {"message": " Email already used"}, HTTPStatus.BAD_REQUEST
        user = User(**data)
        user.save()
        return user_schema.dump(user), HTTPStatus.CREATED


class UserResource(Resource):
    @jwt_optional
    def get(self, username):
        user = User.get_by_username(username=username)
        if user is None:
            return {"message": "user not found"}, HTTPStatus.NOT_FOUND
        current_user = get_jwt_identity()
        if current_user == user.id:
            data = user_schema.dump(user)
        else:
            data = user_public_schema.dump(user)
        return data, HTTPStatus.OK


class MeResource(Resource):
    @jwt_required
    def get(self):
        user = User.get_by_id(get_jwt_identity())
        data = user_schema.dump(user)
        return data, HTTPStatus.OK
