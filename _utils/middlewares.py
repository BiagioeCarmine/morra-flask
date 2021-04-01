from flask import request, Response, abort
import re
import functools

from _utils import models


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

    Visto che Flask non permette di avere middleware
    route-per-route, dobbiamo creare un middleware generico
    di cui creiamo un'istanza per ogni route e fare in modo
    che il middleware non faccia nulla per le route per cui
    non deve essere chiamato in causa.
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
