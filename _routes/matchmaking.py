import os

import eventlet
import jwt
from flask import Blueprint, request, jsonify
from flask_socketio import emit, Namespace

from _utils import matchmaking, socketio, consts

key_from_env = os.getenv("JWT_KEY")
jwt_key = consts.JWT_TEST_KEY if key_from_env is None else key_from_env


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


def communicate_match_id(sid: str, match: int):
    emit('match created', str(match), room=sid)


class MMNamespace(Namespace):
    def on_connect(self):
        pass

    def on_disconnect(self):
        """
        Funzione chiamata quando un utente si
        disconnette dal socket. Deleghiamo
        alla funzione in _utils la responsabilità
        di toglierlo dalla coda giusta.
        """
        matchmaking.remove_sid(request.sid)

    def on_queue(self, data):
        """
        Risponde all'evento "queue" sul socket, e aggiunge
        l'utente alla coda pubblica
        :param data: JWT dell'utente
        """
        try:
            payload = jwt.decode(data, jwt_key, algorithms=["HS256"])
            print("got jwt ", flush=True)
            print(payload, flush=True)
            matchmaking.add_to_public_queue(payload["id"], request.sid)
            return "OK"
        except jwt.DecodeError:
            return "bad token"

    def on_private_queue(self, data):
        """
        Risponde all'evento "private_queue" sul socket,
        e aggiunge l'utente alla coda privata
        :param data: JWT dell'utente
        """
        try:
            payload = jwt.decode(data, jwt_key, algorithms=["HS256"])
            print("got jwt ", flush=True)
            print(payload, flush=True)
            matchmaking.add_to_private_queue(payload['id'], request.sid)
            return "OK"
        except jwt.DecodeError:
            return "bad token"

    def on_play_with_friend(self, token, friend_id):
        try:
            payload = jwt.decode(token, jwt_key, algorithms=["HS256"])
            print("got jwt ", flush=True)
            print(payload, flush=True)
            matchmaking.play_with_friends(payload['id'], request.sid, int(friend_id))
            return "OK"
        except jwt.DecodeError:
            return "bad token"
        except matchmaking.UserAloneLikeADogError:
            return "friend not online"


socketio.on_namespace(MMNamespace())  # path: /socket.io
