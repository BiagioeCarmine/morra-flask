from flask import Blueprint, jsonify
from _utils import models, socketio, match
from flask_socketio import Namespace
import jwt

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


class MatchNamespace(Namespace):
    def on_connect(self):
        pass

    def on_disconnect(self):
        """
        Funzione chiamata quando un utente si
        disconnette dal socket. La partita
        deve finire e dobbiamo avvisare
        l'utente rimasto che la partita
        è finita e ha vinto.
        """
        # emit("the other user disconnected", room=altroutente)
        pass

    def on_move(self, token, hand, prediction):
        """
        Risponde all'evento "move" sul socket,
        decodifica il token, prende l'user id
        e registra la mossa usando match.set_move()
        """
        return "CIAO"


socketio.on_namespace(MatchNamespace('/matches'))
