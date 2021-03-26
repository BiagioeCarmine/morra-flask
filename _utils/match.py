from _utils import redis, models

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
