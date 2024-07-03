from database import *
import os
C = os.path.abspath(os.path.dirname(__file__))

db.bind(provider='sqlite', filename=os.path.join(C, 'database.sqlite'), create_db=True)
db.generate_mapping(create_tables=True)

with db_session:
    for etage in range(2, 6):
        for numero in range(1, 9):
                Chambre(numero=etage*100+numero) 