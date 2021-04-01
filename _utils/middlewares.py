from werkzeug.wrappers import Request, Response
import re

from _utils import models


def validate_hand(hand):
    return 1 <= hand <= 5


def validate_prediction(prediction):
    return 2 <= prediction <= 10


form_validator_middleware_association = [
    # Users
    {
        "regex": "\\/users\\/signup",
        "fields": [
            "username",
            "password"
        ],
        "validators": [
            models.User.validate_username,
            models.User.validate_password
        ]
    },
    {
        "regex": "\\/users\\/login",
        "fields": [
            "username",
            "password"
        ],
        "validators": [
            models.User.validate_username,
            models.User.validate_password
        ]
    },
    # Matches
    {
        "regex": "\\/matches\\/\\d+\\/move",  # che fatica sti escape!
        "fields": [
            "hand",
            "prediction"
        ],
        "validators": [
            validate_hand,
            validate_prediction
        ]
    },

]


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
    def __init__(self, app, regex, required_fields, validators):
        self.app = app
        self.required_fields = required_fields
        self.validators = validators
        self.regex = re.compile(regex)

    def __call__(self, environ, start_response):
        request = Request(environ)
        if request.method != 'POST' or self.regex.fullmatch(request.path).span() != (0, len(request.path)):
            return self.app(environ, start_response)

        if not request.form:
            return Response("missing form", status=400)

        missing_fields = []
        bad_fields = []

        for (i, field) in enumerate(self.required_fields()):
            if request.form.get(field) is None:
                missing_fields.append(field)
            elif not self.validators[i](request.form.get(field)):
                bad_fields.append(field)

        if missing_fields:
            return Response("missing fields "+str(missing_fields))

        if bad_fields:
            return Response("invalid fields "+str(bad_fields))

        return self.app(environ, start_response)
