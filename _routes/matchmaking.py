import eventlet
from flask import Blueprint, request, jsonify

from _utils import matchmaking, middlewares

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


@mm.route("/play_with_friend", methods=["POST"])
@middlewares.FormValidatorMiddleware(
    required_fields=["user"],
    validators=[lambda u: u.isdigit()])
@middlewares.auth_middleware
def play_with_friend(userid):
    friend_id = int(request.form["user"])
    match = matchmaking.play_with_friend(userid, friend_id)
    eventlet.spawn(matchmaking.deal_with_match_confirmation, match)
    return "OK"


@mm.route("/private_queue", methods=["POST"])
@middlewares.auth_middleware
def add_to_private_queue(userid):
    add_to_private_queue(userid)
    return "OK"


@mm.route("/public_queue", methods=["POST"])
@middlewares.auth_middleware
def add_to_public_queue(userid):
    try:
        (match_created, match) = matchmaking.add_to_public_queue(userid)
        eventlet.spawn(matchmaking.deal_with_match_confirmation, match)
        return "OK"
    except matchmaking.UserAloneLikeADogError:
        return "friend not online"
