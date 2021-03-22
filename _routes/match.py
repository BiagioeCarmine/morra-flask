from flask import Blueprint, jsonify
from _utils import models

match = Blueprint('match', __name__, url_prefix="/match")

"""
Route usate per gestire una singola partita.
"""


@match.route("/match/<match_id>", methods=['GET'])
def get_user(match_id):
    return jsonify(models.Match.query.get(match_id).jsonify())
