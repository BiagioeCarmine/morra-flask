from _utils import redis, models
from _routes import matches

"""
Cose di utilità per far funzionare le route di /match.
"""


def set_move(matchid, userid, hand, prediction):
    m_id = models.Match.query.get(matchid)
    if userid == m_id.userid1:
        redis.redis_db.hset("match {} player {}".format(matchid, 1),
                            mapping={'hand': hand, 'prediction': prediction})
    elif userid == m_id.userid2:
        redis.redis_db.hset("match {} player {}".format(matchid, 2),
                            mapping={'hand': hand, 'prediction': prediction})


def notify_match_over(match: models.Match):
    """
    Avvisa entrambi gli utenti del match
    che la partita è finita.
    usando matches.communicate_match_over(sid)

    Ricordati che serve il sid che sta in Redis (sid for user...)
    # TODO:fai sta cosa Biagio
    :param match: la partita in questione
    """
    pass
