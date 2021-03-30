from flask import Blueprint, jsonify, request, Response
from _utils import models, match, consts

import jwt
import os

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
    if not request.form:
        return Response("missing form", status=400)
    if not request.form.get("hand") is None:
        return Response("missing hand", status=400)
    if not request.form.get("prediction") is None:
        return Response("missing prediction", status=400)
    try:
        hand = int(request.form['hand'])
        if hand < 1 or hand > 5:
            return Response("bad hand", status=400)
        prediction = int(request.form['prediction'])
        if prediction < 2 or prediction > 10:
            return Response("bad prediction", status=400)
        token = request.headers.get("Authorization").split("Bearer ")[1]
        payload = jwt.decode(token, jwt_key, algorithms=["HS256"])
        print("got jwt ", flush=True)
        print(payload, flush=True)
        match.set_move(match_id, payload['id'], hand, prediction)
        return "OK"
    except jwt.DecodeError:
        return "bad token"
    except ValueError:
        return Response("hand and prediction weren't integers", status=400)
    except IndexError:
        return Response("bad Authorization string", status=400)
    except AttributeError:
        return Response("missing Authorization header", status=400)
