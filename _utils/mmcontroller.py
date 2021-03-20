from _utils import redis_db, db, models
from redis import WatchError

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
    def create_match(user1: int, user2: int):
        """
        crea Match in DB e notifica gli utenti che giocheranno insieme
        :param user1:
        :param user2:
        :return:
        """
        match = models.Match(user1, user2)
        db.session.add(match)

    @staticmethod
    def add_to_public_queue(user: int):
        try:
            p = redis_db.pipeline()
            p.watch("public_queue")
            cur_queue = p.get("public_queue")
            if cur_queue is None:
                redis_db.append(str(user) + " ")
            else:
                users_in_queue = cur_queue.decode('utf-8').split()
                matched_user = int(users_in_queue[0])
                MMController.create_match(matched_user, user)
                users_in_queue.remove(matched_user)
                if len(users_in_queue) == 0:
                    p.delete("public_queue")
                else:
                    p.set(' '.join(users_in_queue))
            p.execute()
        except WatchError:
            """
            tutta sta cosa di watch serve per evitare
            race condition nel caso di aggiunte in
            contemporanea di più utenti
            """
            MMController.add_to_public_queue(user)

    @staticmethod
    def remove_from_public_queue(user: int):
        try:
            p = redis_db.pipeline()

            p.watch("public_queue")
            queue = p.get("public_queue")
            users_in_queue = queue.split()
            users_in_queue.remove(str(user))
            p.set("public_queue", ' '.join(users_in_queue))
            p.execute()
        except WatchError:
            MMController.remove_from_public_queue(user)
