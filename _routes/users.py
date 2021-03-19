from flask import Blueprint, jsonify
from _utils import models, db

users = Blueprint('users', __name__, url_prefix="/users")

"""
Route usate per gestire gli utenti.
"""


@users.route("/", methods=['GET'])
def get_users():
    return jsonify(models.User.query.all())
