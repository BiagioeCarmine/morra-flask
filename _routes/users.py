from flask import Blueprint
from _utils import users

users = Blueprint('users', __name__, url_prefix="/users")

"""
Route usate per gestire gli utenti.
"""