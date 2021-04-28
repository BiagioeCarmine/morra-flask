import os

import jwt
from flask import Blueprint, jsonify, request, Response

from _utils import models, match, consts, decorators

key_from_env = os.getenv("JWT_KEY")
jwt_key = consts.JWT_TEST_KEY if key_from_env is None else key_from_env


matches = Blueprint('matches', __name__, url_prefix="/matches")

"""
Route usate per gestire una singola partita.
"""


@matches.route("/", methods=['GET'])
def get_matches():
    result = models.Match.query.all()
    return jsonify([m.jsonify() for m in result])


@matches.route("/<match_id>", methods=['GET'])
def get_match(match_id):
    m = models.Match.query.get(match_id)
    return jsonify(m.jsonify()) if m is not None else ("not found", 404)


@matches.route("/<match_id>/move", methods=["POST"])
@decorators.auth_decorator
@decorators.FormValidatorDecorator(
    required_fields=["hand", "prediction"],
    validators=[lambda h: h.isdigit() and 1 <= int(h) <= 5, lambda p: p.isdigit() and 2 <= int(p) <= 10]
)
def set_move(userid, match_id):
    """
    Decodifica il token, prende l'user id
    e registra la mossa usando match.set_move()
    ;:return: se il token è buono, restituirà OK, altrimenti bad token
    """
    if match.set_move(match_id, userid, request.form["hand"], request.form["prediction"]):
        return "OK"
    else:
        return "User not in match", 401


@matches.route("/<match_id>/last_round", methods=['GET'])
def last_round(match_id):
    res = match.get_round_result(match_id)
    return jsonify(res)
