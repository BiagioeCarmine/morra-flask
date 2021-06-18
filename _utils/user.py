import os

import jwt
from sqlalchemy import text

from _utils import models, db, consts

"""
Cose di utilità per gestire gli utenti
"""

key_from_env = os.getenv("JWT_KEY")
jwt_key = consts.JWT_TEST_KEY if key_from_env is None else key_from_env


class DuplicateUserError(Exception):
    pass


class BadCredentialsError(Exception):
    pass


def valid_column(c: str):
    columns = models.User.metadata.tables["Users"].columns.keys()
    print(columns)
    for column in columns:
        if column == c:
            return True
    return False


def query_ordered(order_by: str, n=None, descending=False):
    c = valid_column(order_by)
    if not c:
        print("Passata descrizione colonna non valida: {}".format(order_by))
        return get_all()
    if not n.isdigit():
        print("Passato numero di risultati non numerico: {}".format(n))
        n = None
    if descending:
        # safe perché controlliamo che order_by sia una colonna e basta
        query = models.User.query.select_from(models.User).order_by(text("{} desc".format(order_by)))
    else:
        query = models.User.query.select_from(models.User).order_by(order_by)
    if n is not None:
        query = query.limit(int(n))
    return query.all()


def get(userid):
    return models.User.query.get(userid)


def get_all():
    return models.User.query.all()


def signup(username: str, password: str):
    if models.User.query.filter(models.User.username == username).all():
        raise DuplicateUserError
    user = models.User(username, password.encode("utf-8"))
    db.session.add(user)
    db.session.commit()
    return


def login(username: str, password: str):
    user = models.User.query.filter(models.User.username == username.encode("utf-8")).first()
    if user is None or not user.check_password(password):
        print("wrong password", flush=True)
        raise BadCredentialsError
    return jwt.encode({"id": user.id}, jwt_key, algorithm="HS256")
