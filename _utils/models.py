from bcrypt import hashpw, gensalt, checkpw
from sqlalchemy import Column, Integer, String
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
    username = Column(String(255), unique=True)
    password = Column(String(255))
    vittorie = Column(Integer)
    sconfitte = Column(Integer)
    punteggio = Column(Integer)

    def __init__(self, username, password):
        self.username = username
        self.password = hashpw(password, gensalt(consts.BCRYPT_SALT_ROUNDS))
        self.vittorie = 0
        self.sconfitte = 0
        self.punteggio = 0

    def check_password(self, password):
        return checkpw(password, self.password)

