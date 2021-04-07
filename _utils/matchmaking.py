import datetime

import eventlet
from redis import WatchError

from _utils import redis, db, models, matchcontroller

"""
Nuova architettura matchmaking senza usare socket.

Ho scritto tutto sul README quindi non necessita di grandi introduzioni.
"""


def URI_for_match(match):
    return "https://morra.carminezacc.com/matches/" + str(match)


class PubQueueResult:
    def __init__(self, match_created, match_id=None):
        self.match_created = match_created
        self.match_id = match_id


class UserAloneLikeADogError(Exception):
    pass


def deal_with_match_confirmation(match: models.Match):
    if redis.redis_db.get("match for user " + str(match.userid1)) is None and \
            redis.redis_db.get("match for user " + str(match.userid2)) is None:
        match.confirmed = True
        db.session.commit()


def get_queue_status(user: int):
    match = redis.redis_db.get("match for user " + str(user))
    redis.redis_db.delete("match for user " + str(user))
    return None if match is None else URI_for_match(match.decode("utf-8"))


def notify_match_created(user: int, match: int):
    """
    Chiama la funzione corrispondente del gestore del
    socket per avvisare un utente che è stata creata
    una partita in cui giocherà.
    :param user: ID dell'utente da avvisare
    :param match: ID della partita da comunicare
    """
    redis.redis_db.set("match for user " + str(user), match)


def create_match(user1: int, user2: int):
    """
    Crea Match in DB e notifica gli utenti che giocheranno insieme.
    :param user1: ID di uno degli utenti
    :param user2: ID dell'altro utente
    """
    print("creating match between {} and {}".format(user1, user2), flush=True)
    # fra 10 sec inizia la partita
    match = models.Match(user1, user2, datetime.datetime.now() + datetime.timedelta(seconds=15))
    print(match, flush=True)
    db.session.add(match)
    db.session.commit()
    print("Matches", flush=True)
    print(models.Match.query.all(), flush=True)
    notify_match_created(user1, match.id)
    notify_match_created(user2, match.id)
    print("notified", flush=True)
    eventlet.spawn(matchcontroller.MatchController(match).start)
    return match


def add_to_public_queue(user: int):
    """
    Aggiungiamo l'utente alla coda pubblica
    :param user: ID dell'utente da aggiungere
    """
    try:
        print("aggiungendo a public queue", flush=True)
        p = redis.redis_db.pipeline()
        p.watch("public_queue")
        if p.sismember("public_queue", str(user)):
            return False, None  # utente già in coda
        queue_length = p.scard("public_queue")
        p.multi()
        if queue_length != 0:
            print("lunghezza coda diversa da 0", flush=True)
            # c'è un altro utente in coda, creiamo la partita!
            p.spop("public_queue")  # prendiamo un utente a caso dalla coda
            matched_user = p.execute()[0].decode("utf-8")
            print("stiamo per creare la partita", flush=True)
            return True, create_match(user, int(matched_user))
        else:
            # non c'è nessuno in coda, aggiungiamo l'utente alla coda
            p.sadd("public_queue", str(user))
            p.execute()
            return False, None

    except WatchError:
        """
        tutta sta cosa di watch serve per evitare
        race condition nel caso di aggiunte in
        contemporanea di più utenti
        """
        print("watch error", flush=True)
        return add_to_public_queue(user)


def add_to_private_queue(user: int):
    """
    Aggiungere un utente alla coda privata.
    :param user: ID dell'utente da aggiungere
    :param sid: Session ID del socket a cui l'utente è connesso
    """
    redis.redis_db.sadd("private_queue", str(user))


def play_with_friend(user: int, friend: int):
    """
    Far giocare un utente con un utente specifico
    se l'utente richiesto è nella coda privata.
    :param user: ID dell'utente che effettua la richiesta
    :param sid: Sesion ID del socekt a cui l'utente richiedente è connesso
    :param friend: ID dell'utente con cui l'utente richiedente vuole giocare
    """
    friend_str = str(friend)
    try:
        p = redis.redis_db.pipeline()
        p.watch("private_queue")
        if not p.sismember("private_queue", friend_str):
            # amico non in coda: avviseremo!
            raise UserAloneLikeADogError
        # l'amico è in coda: togliamolo e creiamo la partita!
        p.multi()
        p.srem("private_queue", friend_str)
        p.execute()
        return create_match(user, friend)
    except WatchError:
        play_with_friend(user, friend)
        print("watch error", flush=True)


def get_public_queue():
    pb = redis.redis_db.smembers("public_queue")
    return [models.User.query.get(int(user)) for user in pb]


def get_private_queue():
    pr = redis.redis_db.smembers("private_queue")
    return [models.User.query.get(int(user)) for user in pr]
