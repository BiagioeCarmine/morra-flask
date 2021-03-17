from flask import Blueprint
from _utils import matches

matchmaking = Blueprint('matchmaking', __name__, url_prefix="/mm")

"""
Route usate per creare una partita tra due utenti.
"""