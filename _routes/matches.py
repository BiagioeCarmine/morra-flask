import os

import jwt
from flask import Blueprint, jsonify, request, Response

from _utils import models, match, consts

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
def set_move(match_id):
    """
    Decodifica il token, prende l'user id
    e registra la mossa usando match.set_move()
    ;:return: se il token è buono, restituirà OK, altrimenti bad token
    """
    try:
        token = request.headers.get("Authorization").split("Bearer ")[1]
        payload = jwt.decode(token, jwt_key, algorithms=["HS256"])
        print("got jwt ", flush=True)
        print(payload, flush=True)
        match.set_move(match_id, payload['id'], hand, prediction)
        return "OK"
    except jwt.DecodeError:
        return "bad token"
    except IndexError:
        return Response("bad Authorization string", status=400)
    except AttributeError:
        return Response("missing Authorization header", status=400)


@matches.route("/<match_id>/last_round", methods=['GET'])
def last_round(match_id):
    res = match.get_round_result(match_id)
    return jsonify(res)
