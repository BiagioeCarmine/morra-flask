import datetime
import eventlet

from _utils import redis, db, models, matchcontroller
from redis import WatchError
from _routes import matchmaking


class UserAloneLikeADogError(Exception):
    pass


def notify_match_created(user: int, match: int):
    """
    Chiama la funzione corrispondente del gestore del
    socket per avvisare un utente che è stata cretata
    una partita in cui giocherà.
    :param user: ID dell'utente da avvisare
    :param match: ID della partita da comunicare
    """
    sid = redis.redis_db.get("sid for user "+str(user)).decode("utf-8")
    print("avvisando il sid")
    print(sid)
    matchmaking.communicate_match_id(sid, match)


def create_match(user1: int, user2: int):
    """
    Crea Match in DB e notifica gli utenti che giocheranno insieme.
    :param user1: ID di uno degli utenti
    :param user2: ID dell'altro utente
    """
    print("creating match between {} and {}".format(user1, user2), flush=True)
    # fra 10 sec inizia la partita
    match = models.Match(user1, user2, datetime.datetime.now()+datetime.timedelta(seconds=15))
    print(match, flush=True)
    db.session.add(match)
    db.session.commit()
    print("Matches", flush=True)
    print(models.Match.query.all(), flush=True)
    notify_match_created(user1, match.id)
    notify_match_created(user2, match.id)
    print("notified", flush=True)
    eventlet.spawn(matchcontroller.MatchController(match).start)


def add_to_public_queue(user: int, sid: str):
    """
    Aggiungiamo l'utente alla coda pubblica
    :param user: ID dell'utente da aggiungere
    :param sid: Session ID del socket a cui l'utente è collegato
    """
    remove_sid(sid)
    try:
        print("aggiungendo a public queue", flush=True)
        p = redis.redis_db.pipeline()
        p.watch("public_queue")
        if p.sismember("public_queue", str(user)):
            return  # utente già in coda
        redis.redis_db.set("user for sid " + sid, user)
        redis.redis_db.set("sid for user " + str(user), sid)
        queue_length = p.scard("public_queue")
        p.multi()
        if queue_length != 0:
            print("lunghezza coda diversa da 0", flush=True)
            # c'è un altro utente in coda, creiamo la partita!
            p.spop("public_queue")  # prendiamo un utente a caso dalla coda
            matched_user = p.execute()[0].decode("utf-8")
            print("stiamo per creare la partita", flush=True)
            create_match(user, int(matched_user))
        else:
            # non c'è nessuno in coda, aggiungiamo l'utente alla coda
            p.sadd("public_queue", str(user))
            p.execute()

    except WatchError:
        """
        tutta sta cosa di watch serve per evitare
        race condition nel caso di aggiunte in
        contemporanea di più utenti
        """
        print("watch error", flush=True)
        add_to_public_queue(user, sid)


def remove_sid(sid: str):
    """
    Rimuovere l'utente collegato dal sid specificato
    dalla coda in cui è presente, se è presente
    in una coda.
    :param sid: SID da rimuovere dalla coda giusta
    """
    try:
        user = redis.redis_db.get("user for sid " + sid).decode("utf-8")
        redis.redis_db.srem("public_queue", user)
        redis.redis_db.srem("private_queue", user)
    except AttributeError:
        pass

def add_to_private_queue(user: int, sid: str):
    """
    Aggiungere un utente alla coda privata.
    :param user: ID dell'utente da aggiungere
    :param sid: Session ID del socket a cui l'utente è connesso
    """
    remove_sid(sid)
    redis.redis_db.sadd("private_queue", str(user))
    redis.redis_db.set("user for sid " + sid, user)
    redis.redis_db.set("sid for user " + str(user), sid)


def play_with_friends(user: int, sid: str, friend: int):
    """
    Far giocare un utente con un utente specifico
    se l'utente richiesto è nella coda privata.
    :param user: ID dell'utente che effettua la richiesta
    :param sid: Sesion ID del socekt a cui l'utente richiedente è connesso
    :param friend: ID dell'utente con cui l'utente richiedente vuole giocare
    """
    remove_sid(sid)
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
        redis.redis_db.set("user for sid " + sid, user)
        redis.redis_db.set("sid for user " + str(user), sid)
        create_match(user, friend)
    except WatchError:
        play_with_friends(user, sid,  friend)
        print("watch error", flush=True)


def get_public_queue():
    pb = redis.redis_db.smembers("public_queue")
    return [models.User.query.get(int(user)) for user in pb]


def get_private_queue():
    pr = redis.redis_db.smembers("private_queue")
    return [models.User.query.get(int(user)) for user in pr]
