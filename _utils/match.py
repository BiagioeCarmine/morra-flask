from _utils import redis_db

"""
Cose di utilità per far funzionare le route di /match.
"""


def set_roba(matchid, userid, hand, prediction):
    # prendi il match con id id e vedi se id è player1 o player2
    redis_db.hset("match {} player {}".format(matchid, 1), mapping={'hand': hand, 'prediction': prediction})
    # TODO:fare roba

