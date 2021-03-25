from _utils import redis_db, db, models
from redis import WatchError
from _routes import matchmaking


class UserAddedTwiceError(Exception):
    pass


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
        sid = redis_db.get("sid for user "+str(user)).decode("utf-8")
        print("avvisando il sid")
        print(sid)
        matchmaking.communicate_match_id(sid, match)

    @staticmethod
    def create_match(user1: int, user2: int):
        """
        crea Match in DB e notifica gli utenti che giocheranno insieme
        :param user1:
        :param user2:
        :return:
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
        creating_match = False
        try:
            p = redis_db.pipeline()
            p.watch("public_queue")
            cur_queue = p.get("public_queue")
            p.multi()
            print(cur_queue, flush=True)
            if cur_queue is None:
                p.set("public_queue", str(user) + " ")
            else:
                creating_match = True
                print("cur_queue not empty", flush=True)
                users_in_queue = cur_queue.decode('utf-8').split()
                if str(user) in users_in_queue:
                    raise UserAddedTwiceError
                matched_user = int(users_in_queue[0])
                users_in_queue.pop(0)
                if len(users_in_queue) == 0:
                    p.delete("public_queue")
                else:
                    p.set(' '.join(users_in_queue))
            p.execute()
            redis_db.set("user for sid " + sid, user)
            redis_db.set("sid for user " + str(user), sid)
            if creating_match:
                MMController.create_match(matched_user, user)
        except WatchError:
            """
            tutta sta cosa di watch serve per evitare
            race condition nel caso di aggiunte in
            contemporanea di più utenti
            """
            MMController.add_to_public_queue(user, sid)
            print("watch error", flush=True)
        except UserAddedTwiceError:
            pass

    @staticmethod
    def remove_from_public_queue(user: int):
        try:
            p = redis_db.pipeline()

            p.watch("public_queue")
            queue = p.get("public_queue").decode("utf-8")
            print(queue)
            users_in_queue = queue.split()
            users_in_queue.remove(str(user))
            p.multi()
            p.set("public_queue", ' '.join(users_in_queue))
            p.execute()
        except WatchError:
            MMController.remove_from_public_queue(user)

    @staticmethod
    def remove_sid(sid: str):
        """
        Rimuovere l'utente collegato dal sid specificato
        dalla coda in cui è presente, se è presente
        in una coda.
        :param sid: SID da rimuovere dalla coda giusta
        """
        try:
            p = redis_db.pipeline()
            p.watch("public_queue")
            public_queue = redis.get()
            users_in_queue = None if public_queue is None else public_queue.decode("utf-8").split()
            if users_in_queue is not None and user in users_in_queue:
            # togliamo dalla queue pubblica
            else:
            # vediamo la queue privata
        except

    @staticmethod
    def add_to_private_queue(user: int, sid: str):
        redis_db.append("private_queue", str(user) + " ")
        redis_db.set("user for sid " + sid, user)
        redis_db.set("sid for user " + str(user), sid)

    @staticmethod
    def play_with_friends(user: int, sid: str, friend: int):
        try:
            p = redis_db.pipeline()
            p.watch("private_queue")
            cur_queue = p.get("private_queue")
            if cur_queue is None:
                raise UserAloneLikeADogError
            p.multi()
            users_in_queue = cur_queue.decode('utf-8').split()
            if not str(friend) in users_in_queue:
                raise UserAloneLikeADogError
            redis_db.set("user for sid " + sid, user)
            redis_db.set("sid for user " + str(user), sid)
            users_in_queue.remove(str(friend))
            p.set("private_queue", ' '.join(users_in_queue))
            p.execute()
            MMController.create_match(friend, user)
        except UserAloneLikeADogError:
            pass
        except WatchError:
            MMController.play_with_friends(user, sid,  friend)
            print("watch error", flush=True)
