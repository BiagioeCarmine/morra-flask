from _utils import redis_db, db, models
from redis import WatchError
from _routes import matchmaking

class UserAloneLikeADogError(Exception):
    pass


class MMController:
    """
    potremmo avere requisiti più complessi
    man mano che aggiungiamo modalità diverse,
    ma per il momento essendo che facciamo solo
    1v1 in pratica dobbiamo tenerci da parte
    quelli che vogliono giocare con gli amici
    e farli giocare solo quando si collega un
    loro amico, invece per gli altri si tiene
    un valore in redis che, se non succede niente
    di anomalo, dovrebbe essere al massimo un
    utente quando partiamo con solo l'1v1
    """
    @staticmethod
    def notify_match_created(user: int, match: int):
        """
        Chiama la funzione corrispondente del gestore del
        socket per avvisare un utente che è stata cretata
        una partita in cui giocherà.
        :param user: ID dell'utente da avvisare
        :param match: ID della partita da comunicare
        """
        sid = redis_db.get("sid for user "+str(user)).decode("utf-8")
        print("avvisando il sid")
        print(sid)
        matchmaking.communicate_match_id(sid, match)

    @staticmethod
    def create_match(user1: int, user2: int):
        """
        Crea Match in DB e notifica gli utenti che giocheranno insieme.
        :param user1: ID di uno degli utenti
        :param user2: ID dell'altro utente
        """
        print("creating match between {} and {}".format(user1, user2), flush=True)
        match = models.Match(user1, user2)
        print(match, flush=True)
        db.session.add(match)
        db.session.commit()
        print("Matches", flush=True)
        print(models.Match.query.all(), flush=True)
        MMController.notify_match_created(user1, match.id)
        MMController.notify_match_created(user2, match.id)
        print("notified", flush=True)

    @staticmethod
    def add_to_public_queue(user: int, sid: str):
        """
        Aggiungiamo l'utente alla coda pubblica
        :param user: ID dell'utente da aggiungere
        :param sid: Session ID del socket a cui l'utente è collegato
        """
        try:
            p = redis_db.pipeline()
            p.watch("public_queue")
            if p.sismember("public_queue", str(user)):
                return  # utente già in coda
            redis_db.set("user for sid " + sid, user)
            redis_db.set("sid for user " + str(user), sid)
            queue_length = p.scard("public_queue")
            p.multi()
            if queue_length != 0:
                # c'è un altro utente in coda, creiamo la partita!
                matched_user = p.spop("public_queue").decode("utf-8")  # prendiamo un utente a caso dalla coda
                MMController.create_match(user, int(matched_user))
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
            MMController.add_to_public_queue(user, sid)
            print("watch error", flush=True)

    @staticmethod
    def remove_sid(sid: str):
        """
        Rimuovere l'utente collegato dal sid specificato
        dalla coda in cui è presente, se è presente
        in una coda.
        :param sid: SID da rimuovere dalla coda giusta
        """

        """
        NOTA: ovviamente vedi che sta cosa si può semplificare tantissimo
        se vedi in particolare come si usa redis_db.srem(key, value)
        https://redis.io/commands/srem
        
        Tutti i comandi per i set iniziano per s e sono documentati
        qua https://redis.io/commands#set
        """
        user = redis_db.get("user for sid " + sid).decode("utf-8")
        redis_db.srem("public_queue", user)
        redis_db.srem("private_queue", user)

    @staticmethod
    def add_to_private_queue(user: int, sid: str):
        """
        Aggiungere un utente alla coda privata.
        :param user: ID dell'utente da aggiungere
        :param sid: Session ID del socket a cui l'utente è connesso
        """
        redis_db.sadd("private_queue", str(user))
        redis_db.set("user for sid " + sid, user)
        redis_db.set("sid for user " + str(user), sid)

    @staticmethod
    def play_with_friends(user: int, sid: str, friend: int):
        """
        Far giocare un utente con un utente specifico
        se l'utente richiesto è nella coda privata.
        :param user: ID dell'utente che effettua la richiesta
        :param sid: Sesion ID del socekt a cui l'utente richiedente è connesso
        :param friend: ID dell'utente con cui l'utente richiedente vuole giocare
        """
        friend_str = str(friend)
        try:
            p = redis_db.pipeline()
            p.watch("private_queue")
            if not p.sismember("private_queue", friend_str):
                # amico non in coda: avviseremo!
                raise UserAloneLikeADogError
            # l'amico è in coda: togliamolo e creiamo la partita!
            p.multi()
            p.srem("private_queue", friend_str)
            p.execute()
            redis_db.set("user for sid " + sid, user)
            redis_db.set("sid for user " + str(user), sid)
            MMController.create_match(user, friend)
        except WatchError:
            MMController.play_with_friends(user, sid,  friend)
            print("watch error", flush=True)

    @staticmethod
    def get_public_queue():
        pb = redis_db.smembers("public_queue")
        return [models.User.query.get(int(id)) for user in pb]

    @staticmethod
    def get_private_queue():
        pr = redis_db.smembers("private_queue")
        return [models.User.query.get(int(id)) for user in pr]
