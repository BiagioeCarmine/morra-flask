import functools
import os

import jwt
from flask import request, Response, abort

from _utils import consts

key_from_env = os.getenv("JWT_KEY")
jwt_key = consts.JWT_TEST_KEY if key_from_env is None else key_from_env


def validate_hand(hand):
    try:
        return 1 <= int(hand) <= 5
    except ValueError:
        return False


def validate_prediction(prediction):
    try:
        return 2 <= int(prediction) <= 10
    except ValueError:
        return False


class FormValidatorMiddleware:
    """
    Middleware che verifica se un form è presente,
    contiene i campi richiesti e chiama una funzione
    di validazione su ognuno.
    """
    def __init__(self, required_fields, validators):
        self.required_fields = required_fields
        self.validators = validators

    def __call__(self, f):
        @functools.wraps(f)
        def decorated(*args, **kwargs):
            if not request.form:
                print("no form")
                abort(Response("missing form", status=400))

            print("got a form")

            missing_fields = []
            bad_fields = []

            for (i, field) in enumerate(self.required_fields):
                if request.form.get(field) is None:
                    print("missing field {}".format(field))
                    missing_fields.append(field)
                elif not self.validators[i](request.form.get(field)):
                    print("bad field {}".format(field))
                    bad_fields.append(field)

            if missing_fields:
                abort(Response("missing fields "+str(missing_fields)))

            print("got all fields")

            if bad_fields:
                abort(Response("invalid fields "+str(bad_fields)))

            print("all fields OK")

            return f(*args, **kwargs)
        return decorated


def auth_middleware(f):
    @functools.wraps(f)
    def decorated(*args, **kwargs):
        """
        Middleware che verifica se il jwt è presente ed è valido.
        """
        try:
            token = request.headers.get("Authorization").split("Bearer ")[1]
            payload = jwt.decode(token, jwt_key, algorithms=["HS256"])
            userid = int(payload["id"])
            return f(userid, *args, **kwargs)
        except jwt.DecodeError:
            abort(Response("bad token", status=401))
        except IndexError:
            abort(Response("bad Authorization string", status=400))
        except AttributeError:
            abort(Response("missing Authorization header", status=400))
    return decorated
