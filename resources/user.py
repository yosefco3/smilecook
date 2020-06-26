import os
from flask import request, url_for, render_template
from flask_restful import Resource
from http import HTTPStatus
from models.user import User
from utils import hash_password
from flask_jwt_extended import jwt_optional, get_jwt_identity, jwt_required
from schemas.user import UserSchema
from utils import generate_token, verify_token, allowed_file, save_image
from extensions import mail
from mail import send_email


user_schema = UserSchema()

user_public_schema = UserSchema(exclude=("email",))

user_avatar_schema = UserSchema(only=("avatar_image",))


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
        token = generate_token(user.email, salt="activate")
        subject = "Please confirm your registration"
        link = url_for("useractivateresource", token=token, _external=True)
        html = render_template("email.html", link=link, name=user.username)
        send_email(subject, [user.email], html)
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


class UserActivateResource(Resource):
    def get(self, token):
        email = verify_token(token, salt="activate")
        if email is False:
            return (
                {"message": "invalid token or token expired."},
                HTTPStatus.BAD_REQUEST,
            )

        user = User.get_by_email(email=email)
        if not user:
            return {"message": "User not found."}
        if user.is_active is True:
            return (
                {"message": "The user account is alredy activated."},
                HTTPStatus.BAD_REQUEST,
            )
        user.is_active = True
        user.save()
        return {}, HTTPStatus.NO_CONTENT


class UserAvatarUploadResource(Resource):
    @jwt_required
    def put(self):
        file = request.files.get("avatar")
        if not file:
            return {"message": "Not a valid image."}, HTTPStatus.BAD_REQUEST
        if not allowed_file(file.filename):
            return {"message": "File type not allowed."}, HTTPStatus.BAD_REQUEST
        user = User.get_by_id(get_jwt_identity())
        if user.avatar_image:
            # avatar_path = image_set.path(folder="avatars", filename=user.avatar_image)
            avatar_path = os.path.join(
                os.environ.get("UPLOAD_AVATARS_FOLDER"), user.avatar_image
            )
            if os.path.exists(avatar_path):
                os.remove(avatar_path)
        filename = save_image(image=file, folder="avatars")
        user.avatar_image = filename
        user.save()
        return user_avatar_schema.dump(user), HTTPStatus.OK
