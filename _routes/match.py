from flask import Blueprint
from _utils import matches

match = Blueprint('match', __name__, url_prefix="/match")

"""
Route usate per gestire una singola partita.
"""