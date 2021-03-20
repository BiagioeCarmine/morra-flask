from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from sqlalchemy.ext.declarative import declarative_base

"""
Veloce guida a SQLAlchemy.

SQLAlchemy è un ORM, quindi fondamentalmente
non dobbiamo usare l'SQL direttamente per "parlare"
col DB, quindi facciamo una via di mezzo tra Django
REST Framework e fare tutto a mano.

Adesso se vedi l'engine è impostato su un file
SQLite, che è una tipologia di DMBS "lite", come
dice il nome: in pratica invece di collegarsi
ad un DB "vero" tipo MySQL legge e scrive su un
file sul PC che esegue il backend, ma è solo una
cosa di prova, infatti il file lo chiamo test.db.

Fa tutto da solo, tu non devi fare niente, esegui
il server e quello si crea il file.

Poi quando spostiamo tutto sul server decentemente
impostiamo MySQL, ma intanto è meglio che facciamo
così, almeno ci possiamo mettere a fare cumedia sul
db e poi quando passiamo alla versione "production"
non c'è la merda che facciamo testando tutto.

SQLAlchemy crea da solo le tabelle e tutto, e poi per
manipolare elementi dal DB bisogna
importare questo file (from _utils import db)
e poi usare la session così per aggiungere una cosa
(spiego meglio cos'è la cosa in models.py):

db.session.add(cosa)
db.session.commit()

così per avere tutte le cose di un dato modello
(i modelli sono le classi in models.py, ad
esempio User):

User.query.all()

oppure filtrato per qualcosa come con:

User.query.filter(User.username == username)

Ad esempio puoi eliminare l'utente chiamato Grimos10
scrivendo:

User.query.filter(User.id == "Grimos10").delete().
db.session.commit()

In pratica è molto semplice. Il resto della roba
in questo file serve per far funzionare tutto.
"""


engine = create_engine('sqlite:///test.db')

session = scoped_session(sessionmaker(autocommit=True, autoflush=False, bind=engine))

Base = declarative_base()
Base.query = session.query_property()


def init_db():
    import _utils.models
    Base.metadata.create_all(bind=engine)
