from flask import Flask
import _routes

app = Flask(__name__)
app.register_blueprint(_routes.match)

if __name__ == "__main__":
    app.run()
