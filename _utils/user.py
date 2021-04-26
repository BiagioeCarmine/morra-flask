from _utils import models, db, consts

import os
import jwt
"""
Cose di utilità per gestire gli utenti
"""

key_from_env = os.getenv("JWT_KEY")
jwt_key = consts.JWT_TEST_KEY if key_from_env is None else key_from_env


class DuplicateUserError(Exception):
    pass


class BadCredentialsError(Exception):
    pass


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
