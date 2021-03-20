from flask import Blueprint
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

class MMNamespace(Namespace):
    connections = 0
    def on_connect(self):
        self.connections += 1
        pass

    def on_disconnect(self):
        pass

    def on_connection(self):
        emit(str(self.connections))




socketio.on_namespace(MMNamespace())

