import os
from os import getenv
from sys import exit
import logging

import sentry_sdk
import eventlet
from eventlet import wsgi
from flask import Flask
from flask_cors import CORS
from sentry_sdk.integrations.flask import FlaskIntegration

import _routes
from _utils import db

REQUIRED_ENV_VARS = [
    "MYSQL_DATABASE",
    "MYSQL_USER",
    "MYSQL_PASSWORD",
    "MYSQL_HOST",
    "REDIS_HOST",
    "SENTRY_ENABLED"
]

missing_vars = False

for var in REQUIRED_ENV_VARS:
    if getenv(var) is None:
        missing_vars = True
        print("missing env variable "+var)

if missing_vars:
    exit(1)

"""
Inizializzazione Sentry per log aggregation
"""


if os.getenv("SENTRY_ENABLED") == "1":
    sentry_sdk.init(
        dsn=os.getenv("SENTRY_DSN_URL"),
        integrations=[FlaskIntegration()],
        traces_sample_rate=1.0  # TODO:vedere documentazione
    )


app = Flask(__name__)
CORS(app)

db.init_db()

app.register_blueprint(_routes.matches.matches)
app.register_blueprint(_routes.matchmaking.mm)
app.register_blueprint(_routes.users.users)

if os.getenv("JWT_KEY") is None:
    print("Non è stata impostata una chiave per firmare i JWT, quindi verrà usata quella di test")


@app.route("/")
def test_root():
    logging.error("Caricamento home page")
    return "Non c'è niente da vedere"


print("Avvio server morra")

if __name__ == "__main__":
    wsgi.server(eventlet.listen(('', 5000)), app)

