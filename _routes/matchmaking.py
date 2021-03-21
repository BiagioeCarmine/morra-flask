from flask import Blueprint, request
from flask_socketio import send, emit, Namespace
from _utils import mmcontroller, socketio, consts
import jwt
import os

key_from_env = os.getenv("JWT_KEY")
jwt_key = consts.JWT_TEST_KEY if key_from_env is None else key_from_env

matchmaking = Blueprint('matchmaking', __name__, url_prefix="/mm")
"""
Route usate per creare una partita tra due utenti.
"""


def communicate_match_id(sid: str, match: int):
    emit('match created', str(match), room=sid)


class MMNamespace(Namespace):
    def on_connect(self):
        pass

    def on_disconnect(self):
        mmcontroller.MMController.remove_sid(request.sid)
        pass

    def on_queue(self, data):
        try:
            payload = jwt.decode(data, jwt_key, algorithms=["HS256"])
            print("got jwt ", flush=True)
            print(payload, flush=True)
            mmcontroller.MMController.add_to_public_queue(payload["id"], request.sid)
            return "OK"
        except:
            return "bad token"


socketio.on_namespace(MMNamespace())

