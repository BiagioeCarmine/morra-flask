from flask import Blueprint, jsonify
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
