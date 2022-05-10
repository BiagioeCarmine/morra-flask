import logging
import os
from os import getenv
from sys import exit

import eventlet
from eventlet import wsgi
from flask import Flask
from flask_cors import CORS

from _routes import *
from _utils import db

REQUIRED_ENV_VARS = [
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
        print("missing env variable " + var)

if missing_vars:
    exit(1)


app = Flask(__name__)

CORS(app)

# inizializzazione database

db_host = getenv("MYSQL_HOST")
db_database = getenv("MYSQL_DATABASE")
db_user = getenv("MYSQL_USER")
db_password = getenv("MYSQL_PASSWORD")

app.config["SQLALCHEMY_DATABASE_URI"] = 'mysql+mysqlconnector://{}:{}@{}/{}'.format(db_user, db_password, db_host,
                                                                                    db_database)

db.init_app(app)
with app.app_context():
    db.create_all()

app.register_blueprint(matches.matches)
app.register_blueprint(matchmaking.mm)
app.register_blueprint(users.users)

if os.getenv("JWT_KEY") is None:
    print("Non è stata impostata una chiave per firmare i JWT, quindi verrà usata quella di test")


@app.route("/")
def test_root():
    logging.error("Caricamento home page")
    return "Non c'è niente da vedere"


print("Avvio server morra")

if __name__ == "__main__":
    wsgi.server(eventlet.listen(('', 5000)), app)
