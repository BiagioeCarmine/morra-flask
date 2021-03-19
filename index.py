from flask import Flask
from _utils.db import init_db
import _routes
import os

app = Flask(__name__)

init_db()

app.register_blueprint(_routes.match)
app.register_blueprint(_routes.matchmaking)
app.register_blueprint(_routes.users)

if os.getenv("JWT_KEY") is None:
    print("Non è stata impostata una chiave per firmare i JWT, quindi verrà usata quella di test")


@app.route("/")
def test_root():
    return "Non c'è niente da vedere"


if __name__ == "__main__":
    app.run()
