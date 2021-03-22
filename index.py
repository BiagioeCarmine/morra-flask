from flask import Flask
import os

from _utils import db, socketio, redis_db
import _routes


app = Flask(__name__)

db.init_db()
socketio.init_app(app, cors_allowed_origins="*")

app.register_blueprint(_routes.match)
app.register_blueprint(_routes.matchmaking.matchmaking)
app.register_blueprint(_routes.users)

if os.getenv("JWT_KEY") is None:
    print("Non è stata impostata una chiave per firmare i JWT, quindi verrà usata quella di test")


@app.route("/")
def test_root():
    return "Non c'è niente da vedere"


if __name__ == "__main__":
    socketio.run(app, host='0.0.0.0', port=5000, use_reloader=False)
