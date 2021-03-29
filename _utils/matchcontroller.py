from _utils import models, db, redis
import eventlet
import datetime


class Move:
    def __init__(self, hand: int, prediction: int):
        """
        :param hand: 1<=5
        :param prediction: 2<=10
        """
        self.hand = hand
        self.prediction = prediction


class MatchController:
    """
    TODO: decidere canale di comunicazione, implementare
    IDEA: route che poi mette su Redis le mosse,
    tenendo due valori in Redis per ogni partita,
    poi quando c'è un nuovo turno si resettano i campi
    e si aspetta il tempo di attesa.

    Alla fine del tempo di attesa, si legge da Redis l'ultimo valore del turno,
    ricordarsi di considerare il caso in cui uno o entrambi
    non hanno mandato un cazzo.
    """
    def __init__(self, match: models.Match):
        self.match = match
        print("creata partita", flush=True)

    def start(self):
        eventlet.sleep((self.match.start_time - datetime.datetime.now()).seconds)
        print("iniziata partita", flush=True)
        self.start_match()

    def next_round(self):
        """
        Move to the next round

        """
        redis.redis_db.delete("match {} player 1".format(self.match.id))
        redis.redis_db.delete("match {} player 2".format(self.match.id))
        eventlet.sleep(10)
        self.play_round()
        pass

    def get_player_1_move(self):
        """
        Ottieni la mossa effettuata dal giocatore 1
        per il turno corrente
        TODO: implement this
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
        TODO: implement this
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

    def play_round(self):
        move1 = self.get_player_1_move()
        move2 = self.get_player_2_move()

        if move1 is None and move2 is None:
            # TODO:come lo gestiamo?
            return

        if move1 is None:
            
        elif move2 is None:

        else:
            result = move1.hand + move2.hand

            if move2 is None or (move1.prediction == result and move2.prediction != result):
                self.match.increment_1()
            if move1 is None or (move2.prediction == result and move1.prediction != result):
                self.match.increment_2()

        match_over = False
        if self.match.punti1 == 12:
            self.match.user1.increment_wins()
            match_over = True
        elif self.match.punti2 == 12:
            self.match.user2.increment_wins()
            match_over = True

        db.session.commit()

        if match_over:
            # TODO: che si fa?
            pass

        self.next_round()
