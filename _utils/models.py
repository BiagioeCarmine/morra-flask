from bcrypt import hashpw, gensalt, checkpw
from sqlalchemy import Column, Integer, String, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from _utils import db, consts

"""
Qua vanno tutti i modelli di dato
che useremo nell'app.

Prima di leggere questa leggi l'introduzione
ad SQLAlchemy che ho scritto in db.py.

Per il momento ho scritto la classe User,
poi aggiungere Match e poi eventualmente
altre cose che ci serviranno per l'app.
"""


class User(db.Base):
    """
    Modello di utente della nostra app.

    Vittorie, sconfitte e punteggio vengono
    inizializzati a 0, sinceramente al momento
    il punteggio non so come possiamo calcolarlo
    in una maniera sensata, ma possiamo vedere
    su Internet qualche metodo serio tipo l'Elo
    che usano per gli scacchi (e qualcuno dice su
    csgo pure), altrimenti ci inventiamo noi una
    cosa a capocchia.

    Poi lo implementiamo stesso qua dentro oppure in
    users.py, come ci viene comodo faremo.

    Ho già sistemato l'hashing della password,
    l'unica cosa è che ci saranno da fare un po'
    di prove sul server quale valore di BCRYPT_SALT_ROUNDS
    va bene, fondamentalmente all'aumentare di quel numero
    cresce esponenzialmente il tempo che ci mette
    a fare l'hash ma migliora la sicurezza. Adesso è 10
    e spero vada bene ma quei VPS gratis o economici
    spesso fanno così schifo che tutto può essere che è
    troppo e quindi la gente ci mette 10 anni ogni volta
    per registrarsi o accedere.

    Fondamentalmente l'utente si crea chiamando normalmente
    il costruttore, poi tipo nella route login useremo
    check_password che fa controllare a bcrypt se gli
    hash corrispondono.

    L'oggetto che si ottiene dal costruttore di questa classe
    è la cosa di cui parlavo in db.py.
    """

    __tablename__ = 'Users'
    id = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String(30), unique=True)
    password = Column(String(60))
    vittorie = Column(Integer)
    sconfitte = Column(Integer)
    punteggio = Column(Integer)

    def __init__(self, username, password):
        """

        :param username: NOT UTF-8 ENCODED
        :param password: UTF-8 ENCODED
        """
        self.username = username
        self.password = hashpw(password, gensalt(consts.BCRYPT_SALT_ROUNDS))
        self.vittorie = 0
        self.sconfitte = 0
        self.punteggio = 0

    def check_password(self, password):
        """

        :param password: UTF-8 encoded password
        :return: True if password matches hash, False if not
        """
        return checkpw(password, self.password)

    def jsonify(self):
        return {
            "id": self.id,
            "username": self.username,
            "vittorie": self.vittorie,
            "sconfitte": self.sconfitte,
            "punteggio": self.punteggio
        }

    @staticmethod
    def validate_password(password: str):
        """
        La password è valida se è lunga tra i 5 e i 50 caratteri e composta solo
        da caratteri stampabili. Si potrebbe usare una regex in futuro ma
        per il momento lo faccio a mano.

        :param password: password to validate, MUST'NT BE UTF-8 ENCODED
        :return: True if the password is valid, False if it isn't
        """
        if password is None:
            return False

        password_len = len(password)
        if password_len < 5 or password_len > 50:
            return False

        for char in password:
            if not char.isprintable():
                return False
        return True

    @staticmethod
    def validate_username(username: str):
        """
        Il nome utente è valido se composto solo da lettere
        o numeri, e se è lungo almeno 3 caratteri e al
        massimo 30

        :param username: username to validate, MUST'NT BE UTF-8 ENCODED
        :return: True if the username is valid, False if it isn't
        """
        if username is None:
            return False

        username_len = len(username)
        if username_len < 3 or username_len > 30:
            return False

        for char in username:
            if not char.isalnum():
                return False
        return True

    def incremento_vittorie(self):
        self.vittorie += 1

    def incremento_sconfitte(self):
        self.sconfitte += 1


class Match(db.Base):
    __tablename__ = 'Matches'
    id = Column(Integer, primary_key=True, autoincrement=True)
    userid1 = Column(Integer, ForeignKey('Users.id'), nullable=False)
    userid2 = Column(Integer, ForeignKey('Users.id'), nullable=False)
    punti1 = Column(Integer, nullable=False)
    punti2 = Column(Integer, nullable=False)
    start_time = Column(DateTime, nullable=False)
    user1 = relationship("User", foreign_keys=userid1)
    user2 = relationship("User", foreign_keys=userid2)

    def __init__(self, userid1, userid2, start_time):
        self.punti1 = 0
        self.punti2 = 0
        self.start_time = start_time
        self.userid1 = userid1
        self.userid2 = userid2

    def incremento_punti1(self):
        self.punti1 += 1

    def incremento_punti2(self):
        self.punti2 += 1

    def jsonify(self):
        return {
            "id": self.id,
            "userid1": self.userid1,
            "userid2": self.userid2,
            "punti1": self.punti1,
            "punti2": self.punti2
        }
