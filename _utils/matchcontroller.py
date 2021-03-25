from _utils import models, db, redis_db
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
    def communicate_end_of_match(self):
        """
        Avvisa che la partita è finita
        """
        pass

    def next_round(self):
        """
        Move to the next round
        """
        pass

    def get_player_1_move(self) -> Move:
        """
        Ottieni la mossa effettuata dal giocatore 1
        per il turno corrente
        TODO: implement this
        """
        pass

    def get_player_2_move(self) -> Move:
        """
        Ottieni la mossa effettuata dal giocatore 2
        per il turno corrente
        TODO: implement this
        """
        pass

    def __init__(self, match_id: int):
        self.match = models.Match.query.get(match_id)
        eventlet.sleep((self.match.start_time - datetime.now()).seconds)
        self.start_match()

    def start_match(self):
        """
        Funzione chiamata quando deve iniziare
        una partita
        """
        self.play_round()

    def play_round(self):
        move1 = self.get_player_1_move()
        move2 = self.get_player_2_move()

        result = move1.hand + move2.hand

        if move1.prediction == result and move2.prediction != result:
            self.match.increment_1()
        if move2.prediction == result and move1.prediction != result:
            self.match.increment_2()

        match_over = False
        if models.Match.punti1 == 12:
            self.match.user1.increment_wins()
            match_over = True
        elif models.Match.punti2 == 12:
            self.match.user2.increment_wins()
            match_over = True

        db.session.commit()

        if match_over:
            return self.communicate_end_of_match()

        self.next_round()
