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
    return jsonify(models.User.query.all())

@users.route("/signup", methods=['POST'])
def signup():
    user = models.User(request.form['username'].encode("utf-8"), request.form['password'].encode("utf-8"))
    db.session.add(user)
    db.session.commit()
    return "OK"

@users.route("/login", methods=['POST'])
def login():
    user = models.User.query.filter(models.User.username == request.form['username'].encode("utf-8")).first()
    check = user.check_password(request.form['password'].encode("utf-8"))
    if check:
        return jwt.encode({"username": request.form['username']}, jwt_key, algorithm="HS256")
    else:
        return Response("la password non è buona", status=401)
