import os

import jwt
from flask import Blueprint, jsonify, request, Response

from _utils import models, consts, decorators, user

key_from_env = os.getenv("JWT_KEY")
jwt_key = consts.JWT_TEST_KEY if key_from_env is None else key_from_env

users = Blueprint('users', __name__, url_prefix="/users")

"""
Route usate per gestire gli utenti.
"""


@users.route("/", methods=['GET'])
def get_users():
    result = user.get_all()
    return jsonify([u.jsonify() for u in result])


@users.route("/verify", methods=['GET'])
@decorators.auth_decorator
def get_logged_in_status(_):
    return "OK"


@users.route("/user/<user_id>", methods=['GET'])
def get_user(user_id):
    return jsonify(user.get(user_id).jsonify())


@users.route("/signup", methods=['POST'])
@decorators.FormValidatorDecorator(
    required_fields=["username", "password"],
    validators=[models.User.validate_username, models.User.validate_password])
def signup():
    try:
        user.signup(request.form['username'], request.form['password'])
        return Response("OK", status=201)
    except user.DuplicateUserError:
        return Response("username conflict", status=409)


@users.route("/login", methods=['POST'])
@decorators.FormValidatorDecorator(
    required_fields=["username", "password"],
    validators=[models.User.validate_username, models.User.validate_password])
def login():


    if user is None or not user.check_password(request.form['password']):
        print("wrong password", flush=True)
        return Response("bad credentials", status=401)
    return jwt.encode({"id": user.id}, jwt_key, algorithm="HS256")

