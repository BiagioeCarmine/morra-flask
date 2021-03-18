from flask import Flask
from _utils.db import init_db
import _routes

app = Flask(__name__)

init_db()

app.register_blueprint(_routes.match)
app.register_blueprint(_routes.matchmaking)
app.register_blueprint(_routes.users)


@app.route("/")
def root():
  return "Non c'è niente da vedere"

if __name__ == "__main__":
    app.run()
