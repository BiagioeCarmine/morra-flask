from flask import Blueprint, jsonify, request, Response
from _utils import models, db, consts
import jwt
import os

key_from_env = os.getenv("JWT_KEY")
jwt_key = consts.JWT_TEST_KEY if key_from_env is None else key_from_env

users = Blueprint('users', __name__, url_prefix="/users")


"""
Route usate per gestire gli utenti.
"""


@users.route("/", methods=['GET'])
def get_users():
    result = models.User.query.all()
    return jsonify([user.jsonify() for user in result])


@users.route("/user/<user_id>", methods=['GET'])
def get_user(user_id):
    return jsonify(models.User.query.get(user_id).jsonify())


@users.route("/signup", methods=['POST'])
def signup():
    if not request.form:
        return Response("missing form", status=400)
    if not models.User.validate_username(request.form['username']):
        return Response("bad username", status=400)
    if not models.User.validate_password(request.form['password']):
        return Response("bad password", status=400)
    user = models.User(request.form['username'], request.form['password'].encode("utf-8"))
    db.session.add(user)
    return Response("OK", status=201)


@users.route("/login", methods=['POST'])
def login():
    user = models.User.query.filter(models.User.username == request.form['username']).first()
    check = user.check_password(request.form['password'].encode("utf-8"))
    if check:
        return jwt.encode({"id": user.id}, jwt_key, algorithm="HS256")
    else:
        return Response("wrong password", status=401)
