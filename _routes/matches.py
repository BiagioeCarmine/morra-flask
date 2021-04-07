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
    return jsonify(models.Match.query.get(match_id).jsonify())


@matches.route("/<match_id>/move", methods=["POST"])
@decorators.auth_decorator
@decorators.FormValidatorDecorator(
    required_fields=["hand", "prediction"],
    validators=[lambda h: 1 <= h <= 5, lambda p: 2 <= p <= 10]
)
def set_move(userid, match_id):
    """
    Decodifica il token, prende l'user id
    e registra la mossa usando match.set_move()
    ;:return: se il token è buono, restituirà OK, altrimenti bad token
    """
    match.set_move(match_id, userid, request.form["hand"], request.form["prediction"])
    return "OK"


@matches.route("/<match_id>/last_round", methods=['GET'])
def last_round(match_id):
    res = match.get_round_result(match_id)
    return jsonify(res)
