from pony.orm import *
from datetime import datetime, date

db = Database()

class ListMenage(db.Entity):
    date = Required(date)
    chambre = Required("Chambre")
    recouche = Required(bool, default=False)
    recouchePlus = Required(bool, default=False)
    verifier = Required(bool, default=False)
    note = Optional(str)
    auteur = Required(str)

class Chambre(db.Entity):
    numero = PrimaryKey(int)
    menages = Set(ListMenage)
    signalements = Set("Signalement")

class Signalement(db.Entity):
    chambre = Required(Chambre)
    date = Required(datetime, 6)
    raison = Required(str)
    auteur = Required(str)
    resolu = Required(bool, default=False)
    resoluPar = Optional(str)
    photo = Optional(str)


class Pointage(db.Entity):
    dt = Required(datetime)
    auteur = Required(str)
    fin = Required(bool)


