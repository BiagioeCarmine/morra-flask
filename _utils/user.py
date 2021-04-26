from _utils import models, db
"""
Cose di utilità per gestire gli utenti
"""


class DuplicateUserError(Exception):
    pass


def get(userid):
    return models.User.query.get(userid)


def get_all():
    return models.User.query.all()


def signup(username, password):
    if models.User.query.filter(models.User.username == request.form['username']).all():
        raise DuplicateUserError
    user = models.User(username, password.encode("utf-8"))
    db.session.add(user)
    db.session.commit()
    return

def login(username, password):
    user = models.User.query.filter(models.User.username == request.form['username'].encode("utf-8")).first()
