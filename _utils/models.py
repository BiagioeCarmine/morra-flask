import datetime

from bcrypt import hashpw, gensalt, checkpw
from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Boolean, Computed
from sqlalchemy.orm import relationship

from _utils import consts, db

"""
Moedlli di dato che usiamo nell'app.
"""


class User(db.Model):
    """
    Modello di utente della nostra app.
    """

    __tablename__ = 'Users'
    id = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String(30), unique=True)
    password = Column(String(60))
    admin = Column(Boolean)
    vittorie = Column(Integer)
    sconfitte = Column(Integer)
    punteggio = Column(Integer, Computed('3 * vittorie-sconfitte', persisted=False))

    def __init__(self, username, password):
        """

        :param username: NOT UTF-8 ENCODED
        :param password: UTF-8 ENCODED
        """
        self.username = username
        self.password = hashpw(password, gensalt(consts.BCRYPT_SALT_ROUNDS))
        self.vittorie = 0
        self.sconfitte = 0
        self.admin = False

    def check_password(self, password):
        """

        :param password: UTF-8 encoded password
        :return: True if password matches hash, False if not
        """
        """
        MySQL, a differenza di quanto pensi PyCharm,
        restituisce una stringa decodificata come hash
        della password, quindi va encode-ata per far
        contento bcrypt che vuole le cose in UTF-8
        """
        return checkpw(password.encode("utf-8"), self.password.encode("utf-8"))

    def jsonify(self):
        """
        Non è repr o str perché altrimenti non potremmo restituire un dict, e restituendo
        una stringa il risultato finale nelle liste non è JSON valido. Si elimina l'hash della
        password perché non siamo così poco attenti con i dati degli utenti, si elimina admin
        perché per il momento non serve a niente e non ha senso esporre quel valore, e si elimina
        _sa_instance_state perché è una cosa interna di SQLAlchemy.
        """
        d = self.__dict__.copy()
        del d["_sa_instance_state"]
        del d["password"]
        del d["admin"]
        return d

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

    def increment_wins(self):
        self.vittorie += 1

    def increment_losses(self):
        self.sconfitte += 1


class Match(db.Model):
    __tablename__ = 'Matches'
    id = Column(Integer, primary_key=True, autoincrement=True)
    confirmed = Column(Boolean, nullable=False)
    finished = Column(Boolean, nullable=False)
    userid1 = Column(Integer, ForeignKey('Users.id'), nullable=False)
    userid2 = Column(Integer, ForeignKey('Users.id'), nullable=False)
    punti1 = Column(Integer, nullable=False)
    punti2 = Column(Integer, nullable=False)
    confirmation_time = Column(DateTime)
    start_time = Column(DateTime, nullable=False)
    first_round_results = Column(DateTime, nullable=False)
    user1 = relationship("User", foreign_keys=userid1)
    user2 = relationship("User", foreign_keys=userid2)

    def __init__(self, userid1, userid2, confirmation_time, start_time):
        self.punti1 = 0
        self.punti2 = 0
        self.confirmation_time = confirmation_time
        self.start_time = start_time
        self.first_round_results = start_time + datetime.timedelta(seconds=consts.EXTRA_WAIT_SECONDS)
        self.userid1 = userid1
        self.userid2 = userid2
        self.confirmed = False
        self.finished = False

    def increment_1(self):
        self.punti1 += 1

    def increment_2(self):
        self.punti2 += 1

    def confirm(self):
        self.confirmed = True

    def jsonify(self):
        """
        Non è repr o str perché altrimenti non potremmo restituire un dict, e restituendo
        una stringa il risultato finale nelle liste non è JSON valido. Si elimina
        _sa_instance_state perché è una cosa interna di SQLAlchemy. Vanno sistemate
        le date per restituire un formato appropriato.
        """
        d = self.__dict__.copy()
        del d["_sa_instance_state"]
        d["start_time"] = self.start_time.replace(tzinfo=datetime.timezone.utc).isoformat()
        d["confirmation_time"] = d["start_time"] if self.confirmation_time is None else self.confirmation_time.replace(tzinfo=datetime.timezone.utc).isoformat()
        d["first_round_results"] = self.first_round_results.replace(tzinfo=datetime.timezone.utc).isoformat()
        return d
