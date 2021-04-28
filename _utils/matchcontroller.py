import datetime

import eventlet

from _utils import models, redis, consts, db


class BadMoveError(Exception):
    pass


class Move:
    def __init__(self, hand: int, prediction: int):
        """
        :param hand: 1<=5
        :param prediction: 2<=10
        """
        if hand < 1 or hand > 5 or prediction < 2 or prediction > 10:
            raise BadMoveError
        self.hand = hand
        self.prediction = prediction


class MatchController:
    """
    Funzionamento: quando viene creata una partita si chiama start(), che aspetta un po' per vedere se entrambi
    gli utenti sono pronti a giocare (se hanno ricevuto l'informazione che una partita è stata cretata) e,quando
    viene il momento per iniziare la partita, chiama start_match, che a sua volta chiama play_round,
    che prende le mosse dei due giocatori con get_player_$_move e decide a chi assegnare punti. Se per due round
    i due giocatori non rispondono con una mossa, la partita viene terminata anticipatamente (chiamando end_match).
    In caso contrario, dopo aver impostato i punti e valutato se la partita è finita, chiama set_round_results
    che mette tutto su redis e rende possibile ai client di ottenere quei dati, per poi chiamare next_round,
    che quando arriverà il momento del prossimo round chiamerà di nuovo play_round.
    """
    def __init__(self, match: models.Match, app):
        self.match = match
        self.app = app
        self.skipped_rounds = 0
        print("creata partita", flush=True)

    def set_round_results(self, move1, move2, next_round_start):
        print("Impostiamo risultati round")
        name = "match {} round result".format(self.match.id)
        if move1 is not None:
            redis.redis_db.hset(name, "hand1", move1.hand)
            redis.redis_db.hset(name, "prediction1", move1.prediction)
        if move2 is not None:
            redis.redis_db.hset(name, "hand2", move2.hand)
            redis.redis_db.hset(name, "prediction2", move2.prediction)
        redis.redis_db.hset(name, "cur_points1", self.match.    punti1)
        redis.redis_db.hset(name, "cur_points2", self.match.punti2)
        redis.redis_db.hset(name,
                            "next_round_start", "over" if next_round_start is None else next_round_start.isoformat())

    def start(self):
        """
        Entry point della partita
        """
        eventlet.sleep((self.match.start_time - datetime.datetime.now()).seconds
                       - (consts.MATCH_START_DELAY-consts.ROUND_MOVE_WAIT_SECONDS))
        # deal with match confirmation
        if redis.redis_db.get("match for user " + str(self.match.userid1)) is None and \
                redis.redis_db.get("match for user " + str(self.match.userid2)) is None:
            with self.app.app_context():
                db.engine.execute("UPDATE Matches SET confirmed=TRUE WHERE id={}".format(self.match.id))
               # self.match.confirmed = True
               # db.session.commit()
            eventlet.sleep((self.match.start_time - datetime.datetime.now()).seconds)
            print("iniziata partita", flush=True)
            self.start_match()
        else:
            print("partita annullata", flush=True)
            return

    def next_round(self, start_time):
        """
        Move to the next round
        """
        redis.redis_db.delete("match {} player 1".format(self.match.id))
        redis.redis_db.delete("match {} player 2".format(self.match.id))
        eventlet.sleep((start_time - datetime.datetime.now().replace(tzinfo=datetime.timezone.utc)).seconds)
        self.play_round()

    def get_player_1_move(self):
        """
        Ottieni la mossa effettuata dal giocatore 1
        per il turno corrente
        """
        hand = redis.redis_db.hget("match {} player 1".format(self.match.id), "hand")
        prediction = redis.redis_db.hget("match {} player 1".format(self.match.id), "prediction")
        if hand is None or prediction is None:
            return None
        return Move(int(hand.decode("utf-8")),
                    int(prediction.decode("utf-8")))

    def get_player_2_move(self) -> Move:
        """
        Ottieni la mossa effettuata dal giocatore 2
        per il turno corrente
        """
        hand = redis.redis_db.hget("match {} player 2".format(self.match.id), "hand")
        prediction = redis.redis_db.hget("match {} player 2".format(self.match.id), "prediction")
        if hand is None or prediction is None:
            return None
        return Move(int(hand.decode("utf-8")),
                    int(prediction.decode("utf-8")))

    def start_match(self):
        """
        Funzione chiamata quando deve iniziare
        una partita
        """
        self.play_round()

    def end_match(self):
        """
        Fai finire la partita (suggerimento: chiama match.notify_match_over()
        """
        print("*tanti saluti dal thread ausiliario della partita {}, finita {} a {}*"
              .format(self.match.id, self.match.punti1, self.match.punti2))
        pass

    def play_round(self):
        """
        TODO: implementare una sorta di grace time, che crea una finestra temporale in cui inviare i risultati invece che un istante
        """
        move1 = self.get_player_1_move()
        move2 = self.get_player_2_move()

        if move1 is None and move2 is None:
            print("Non ci sono state mosse questo round")
            if self.skipped_rounds == 0:
                print("è la prima volta che succede")
                self.skipped_rounds += 1
                next_round_start = datetime.datetime.now().replace(tzinfo=datetime.timezone.utc) +\
                                   datetime.timedelta(seconds=consts.ROUND_MOVE_WAIT_SECONDS)
                self.set_round_results(None, None, next_round_start)
                return self.next_round(next_round_start)
            else:
                print("terminiamo anticipatamente la partita")
                return self.end_match()

        if move1 is None:
            with self.app.app_context():
                self.match.increment_2()
                db.session.commit()
        elif move2 is None:
            with self.app.app_context():
                self.match.increment_1()
                db.session.commit()
        else:
            result = move1.hand + move2.hand

            if move2 is None or (move1.prediction == result and move2.prediction != result):
                with self.app.app_context():
                    self.match.increment_1()
                    db.session.commit()
            if move1 is None or (move2.prediction == result and move1.prediction != result):
                with self.app.app_context():
                    self.match.increment_2()
                    db.session.commit()

        match_over = False
        if self.match.punti1 == 12:
            with self.app.app_context():
                self.match.user1.increment_wins()
                db.session.commit()
            match_over = True
        elif self.match.punti2 == 12:
            with self.app.app_context():
                self.match.user2.increment_wins()
                db.session.commit()
            match_over = True

        next_round_start = None if match_over\
            else datetime.datetime.now().replace(tzinfo=datetime.timezone.utc)+\
                 datetime.timedelta(seconds=consts.ROUND_MOVE_WAIT_SECONDS)
        self.set_round_results(move1, move2, next_round_start)

        if match_over:
            return self.end_match()

        self.next_round(next_round_start)
