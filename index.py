from flask import Flask
import os
from flask_cors import CORS

from _utils import db, socketio, redis
import _routes
from os import getenv
from sys import exit

REQUIRED_ENV_VARS = [
    "MYSQL_ROOT_PASSWORD",
    "MYSQL_DATABASE",
    "MYSQL_USER",
    "MYSQL_PASSWORD",
    "MYSQL_HOST",
    "REDIS_HOST"
]

missing_vars = False

for var in REQUIRED_ENV_VARS:
    if getenv(var) is None:
        missing_vars = True
        print("missing env variable "+var)

if missing_vars:
    exit(1)

app = Flask(__name__)
CORS(app)

db.init_db()
socketio.init_app(app, cors_allowed_origins="*")

app.register_blueprint(_routes.matches.matches)
app.register_blueprint(_routes.matchmaking.mm)
app.register_blueprint(_routes.users.users)

if os.getenv("JWT_KEY") is None:
    print("Non è stata impostata una chiave per firmare i JWT, quindi verrà usata quella di test")


@app.route("/")
def test_root():
    return "Non c'è niente da vedere"


print("Avvio server morra")

if __name__ == "__main__":
    socketio.run(app, host='0.0.0.0', port=5000, use_reloader=False)
