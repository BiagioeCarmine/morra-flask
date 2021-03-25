import os

import jwt
from flask import Blueprint, request
from flask_socketio import emit, Namespace

from _utils import mmcontroller, socketio, consts

key_from_env = os.getenv("JWT_KEY")
jwt_key = consts.JWT_TEST_KEY if key_from_env is None else key_from_env

# al momento nessuna route ma non si sa mai in futuro
matchmaking = Blueprint('matchmaking', __name__, url_prefix="/mm")
"""
Route e socket usati per creare una partita tra due utenti.
"""


def communicate_match_id(sid: str, match: int):
    emit('match created', str(match), room=sid)


class MMNamespace(Namespace):
    def on_connect(self):
        pass

    def on_disconnect(self):
        """
        Funzione chiamata quando un utente si
        disconnette dal socket. Deleghiamo
        al MMController la responsabilità
        di toglierlo dalla coda giusta.
        """
        mmcontroller.MMController.remove_sid(request.sid)

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
            mmcontroller.MMController.add_to_public_queue(payload["id"], request.sid)
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
            mmcontroller.MMController.add_to_private_queue(payload['id'], request.sid)
            return "OK"
        except jwt.DecodeError:
            return "bad token"

    def on_play_with_friend(self, token, friend_id):
        try:
            payload = jwt.decode(token, jwt_key, algorithms=["HS256"])
            print("got jwt ", flush=True)
            print(payload, flush=True)
            mmcontroller.MMController.play_with_friends(payload['id'], request.sid, int(friend_id))
            return "OK"
        except jwt.DecodeError:
            return "bad token"
        except mmcontroller.UserAloneLikeADogError:
            return "friend not online"


socketio.on_namespace(MMNamespace())  # path: /socket.io
