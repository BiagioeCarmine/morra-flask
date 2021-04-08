import datetime

import eventlet
from redis import WatchError

from _utils import redis, db, models, matchcontroller, consts

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


class FriendNotOnlineError(Exception):
    pass


def check_user_poll(user: int, last_poll: datetime, next_poll: datetime):
    """
    Una maniera alternativa di fare sta cosa però con dei secondi extra
    sarebbe quella di rimandare la decisione a X secondi nel futuro
    se e solo se il client fails to poll in time (non mi viene in italiano atm).
    """
    eventlet.sleep(next_poll - datetime.datetime.now() + consts.EXTRA_WAIT_SECONDS)
    cur_poll = redis.redis_db.get("user {} last poll".format(user)).decode("utf-8")
    if datetime.datetime.fromisoformat(cur_poll) == last_poll:
        # il client ci sta ghostando! l'utente si sarà stancato di aspettare...
        redis.redis_db.srem("private_queue", str(user))
        redis.redis_db.srem("public_queue", str(user))


def get_queue_status(user: int):
    """
    Unica funzione che deve toccare user {} last poll.
    Quando questa funzione viene chiamata, aggiorniamo quel valore,
    che tiene traccia di quando l'ultima volta l'utente ha fatto
    una richiesta per chiedere se è stata trovata una partita.

    Se non c'è una partita pronta per l'utente la funzione deve
    fare in modo tale che check_user_poll in futuro controlli che
    effettivamente il client stia continuando a fare richieste.
    :param user: ID utente che richiede lo stato
    """
    cur_poll = datetime.datetime.now()
    redis.redis_db.set("user {} last poll".format(user), str(cur_poll.isoformat()))
    match = redis.redis_db.get("match for user " + str(user))
    redis.redis_db.delete("match for user " + str(user))
    if match is None:
        next_poll = datetime.datetime.now() + datetime.timedelta(seconds=consts.QUEUE_STATUS_POLL_SECONDS)
        eventlet.spawn(check_user_poll, user, cur_poll, next_poll)
        return {
            "created": False,
            "pollBefore": next_poll.isoformat(),
            "pollAt": "https://morra.carminezacc.com/mm/queue_status"
        }
    return {
        "created": True,
        "match": URI_for_match(match.decode("utf-8"))
    }


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
    match = models.Match(user1, user2, datetime.datetime.now() + datetime.timedelta(seconds=consts.MATCH_START_DELAY))
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
        if p.sismember("public_queue", str(user)) or p.sismember("private_queue", str(user)):
            p.unwatch()
            return False, get_queue_status(user)  # utente già in coda
        queue_length = p.scard("public_queue")
        p.multi()
        if queue_length != 0:
            print("lunghezza coda diversa da 0", flush=True)
            # c'è un altro utente in coda, creiamo la partita!
            p.spop("public_queue")  # prendiamo un utente a caso dalla coda
            matched_user = p.execute()[0].decode("utf-8")
            print("stiamo per creare la partita", flush=True)
            p.unwatch()
            return True, create_match(user, int(matched_user))
        else:
            # non c'è nessuno in coda, aggiungiamo l'utente alla coda
            p.sadd("public_queue", str(user))
            p.execute()
            p.unwatch()
            return False, get_queue_status(user)

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
    """
    redis.redis_db.sadd("private_queue", str(user))
    return get_queue_status(user)


def play_with_friend(user: int, friend: int):
    """
    Far giocare un utente con un utente specifico
    se l'utente richiesto è nella coda privata.
    :param user: ID dell'utente che effettua la richiesta
    :param friend: ID dell'utente con cui l'utente richiedente vuole giocare
    """
    friend_str = str(friend)
    try:
        p = redis.redis_db.pipeline()
        p.watch("private_queue")
        if not p.sismember("private_queue", friend_str):
            # amico non in coda: avviseremo!
            raise FriendNotOnlineError
        # l'amico è in coda: togliamolo e creiamo la partita!
        p.multi()
        p.srem("private_queue", friend_str)
        p.execute()
        return create_match(user, friend)
    except WatchError:
        print("watch error", flush=True)
        return play_with_friend(user, friend)


def get_public_queue():
    pb = redis.redis_db.smembers("public_queue")
    return [models.User.query.get(int(user)) for user in pb]


def get_private_queue():
    pr = redis.redis_db.smembers("private_queue")
    return [models.User.query.get(int(user)) for user in pr]
