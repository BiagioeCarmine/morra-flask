from flask import Blueprint, jsonify
from _utils import models

match = Blueprint('match', __name__, url_prefix="/match")

"""
Route usate per gestire una singola partita.
"""


@match.route("/", methods=['GET'])
def get_matchs():
    result = models.Match.query.all()
    return jsonify([m.jsonify() for m in result])


@match.route("/<match_id>", methods=['GET'])
def get_match(match_id):
    return jsonify(models.Match.query.get(match_id).jsonify())


# TODO: route per gestire partita
