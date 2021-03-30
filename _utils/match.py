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
    :param match: la partita in questione
    """
    sid1 = redis.redis_db.get("sid for user " + str(match.user1)).decode("utf-8")
    matches.communicate_match_over(sid1)
    sid2 = redis.redis_db.get("sid for user " + str(match.user2)).decode("utf-8")
    matches.communicate_match_over(sid2)
