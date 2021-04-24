import eventlet
from flask import Blueprint, request, jsonify, Response

from _utils import matchmaking, decorators

mm = Blueprint('mm', __name__, url_prefix="/mm")
"""
Route e socket usati per creare una partita tra due utenti.
"""


@mm.route("/public_queue", methods=['GET'])
def get_public_queue():
    pb = matchmaking.get_public_queue()
    return jsonify([user.jsonify() for user in pb])


@mm.route("/private_queue", methods=["GET"])
def get_private_queue():
    pr = matchmaking.get_private_queue()
    return jsonify([user.jsonify() for user in pr])


@mm.route("/queue_status", methods=["GET"])
@decorators.auth_decorator
def get_queue_status(userid):
    res = matchmaking.get_queue_status(userid)
    if res["created"]:
        status = 201
    else:
        status = 200
    return jsonify(res), status


@mm.route("/play_with_friend", methods=["POST"])
@decorators.FormValidatorDecorator(
    required_fields=["user"],
    validators=[str.isdigit])
@decorators.auth_decorator
def play_with_friend(userid):
    try:
        friend_id = int(request.form["user"])
        match = matchmaking.play_with_friend(userid, friend_id)
        return Response(jsonify({"created": True, "match": match.id}), status=201)
    except matchmaking.FriendNotOnlineError:
        return Response("friend not online", status=404)


@mm.route("/queue", methods=["POST"])
@decorators.auth_decorator
@decorators.FormValidatorDecorator(
    required_fields=["type"],
    validators=[lambda t: t == "public" or t == "private"]
)
def add_to_queue(userid):
    if request.form["type"] == "private":
        return jsonify(matchmaking.add_to_private_queue(userid))
    (match_created, res) = matchmaking.add_to_public_queue(userid)
    if match_created:
        status = 201
    else:
        status = 200
    return jsonify({"created": True, "match": res.id} if match_created else res), status
