from nicegui import app, ui

from database import *

from datetime import datetime, timedelta, date

import os
C = os.path.abspath(os.path.dirname(__file__))

db.bind(provider='sqlite', filename=os.path.join(C, 'database.sqlite'), create_db=True)
db.generate_mapping(create_tables=True)

users = [{
    "id": "gabriel",
    "nom": "Gabriel",
    "role": "reception",
    "pass": "1234"
}, {
    "id": "sadiya",
    "nom": "Sadiya",
    "role": "menage",
    "pass": "1234"
}, {
    "id": "rosalina",
    "nom": "Rosalina",
    "role": "menage",
    "pass": "1234"
}]

@ui.page("/")
def main():
    if not (userId := app.storage.user.get("user", False)):
        ui.navigate.to("/login")
    else:
        for user in users:
            if user["id"] == userId:
                link = f"/{user['role']}"
                ui.navigate.to(link)

@ui.page("/login")
def login():
    def connect(user, link):
        app.storage.user["user"] = user
        ui.navigate.to(link)

    ui.label("Utilisateur ?")
    with ui.row():
        for user in users:
            link = f"/{user['role']}"
            ui.button(user["nom"],
                      on_click=lambda user=user, link=link: connect(user["id"], link))

def header(accueil=True):
    user = app.storage.user.get("user", "Error")

    def disconnect():
        app.storage.user["user"] = False
        ui.navigate.to("/")

    @db_session
    def arrive(fin=False):
        Pointage(auteur=user, fin=fin, dt=datetime.now())
        ui.notify(f"Vous êtes {'arrivé' if not fin else 'parti'} à {datetime.now()}")

    def depart():
        arrive(fin=True)

    pointages = select(p for p in Pointage if p.dt.date() == datetime.today().date())

    if accueil:
        ui.button("Accueil", on_click=lambda: ui.navigate.to("/"))
        with ui.row():
            ui.label(f"Bonjour, {user}")
            ui.button("Deconnexion", on_click=disconnect)
        with ui.row():
            ui.button("Arrivé", on_click=arrive)
            ui.button("Depart", on_click=depart)
            [ui.label(f"{pointage.dt.isoformat()}") for pointage in pointages if pointage.auteur == user]
    else:
        ui.button("retour Accueil", on_click=lambda: ui.navigate.to("/"))
    


@ui.page("/reception")
def reception():
    user = app.storage.user.get("user", "Error")
    header()
    ui.button("Chambre pour ménage", on_click=lambda: ui.navigate.to(f"/reception/menage"))

@ui.page("/reception/menage")
@ui.page("/reception/menage/")
@ui.page("/reception/menage/{dateStr}")
def receptionMenage(dateStr=False):
    user = app.storage.user.get("user", "Error")

    if dateStr:
        dateTarget = datetime.strptime(dateStr, "%Y-%m-%d").date()
    else:
        ui.navigate.to(f'/reception/menage/{(date.today() + timedelta(days=1)).strftime("%Y-%m-%d")}')
        return

    # Init dict for init display
    chambres = {etage * 100 + numero : False 
                for etage in range(2, 6)
                for numero in range(1, 9)}
    chambres_notes = {etage * 100 + numero : "" 
                        for etage in range(2, 6)
                        for numero in range(1, 9)}
    menages = select(menage for menage in ListMenage
                     if menage.date == dateTarget)

    # Fill dict for init display
    for menage in menages:
        if menage.verifier:
            res = "?"
        elif menage.recouchePlus:
            res = "+"
        elif menage.recouche:
            res = "R"
        else:
            res = True
        chambres[menage.chambre.numero] = res
        chambres_notes[menage.chambre.numero] = menage.note

    @db_session
    def submit(chambre:int, value, note=False):
        value = value.value
        queryRoom = (menage for menage in ListMenage
                        if menage.date == dateTarget
                        and menage.chambre.numero == chambre)
        if (not value) and (not note):
            delete(queryRoom)
        elif value:
            # Si il n’existe pas, on le crée
            menage = select(queryRoom)
            if len(menage) == 0:
                ListMenage(date=dateTarget,
                           chambre=Chambre[chambre],
                           recouche = (value == "R"),
                           recouchePlus = (value == "+"),
                           verifier = (value == "?"),
                           auteur=user,
                           note = value if note else "")
            elif len(menage) == 1 and not note:
                menage = menage.first()
                menage.recouche = (value == "R")
                menage.recouchePlus = (value == "+")
                menage.verifier = (value == "?")
            elif len(menage) == 1 and note:
                menage = menage.first()
                menage.note = value
            else:
                raise(f"Plusieurs Occurence de la chambre {chambre} le {dateTarget}")

    # DISPLAY
    header(accueil=False)

    with ui.input('Date', value=dateStr).on_value_change(lambda e: ui.navigate.to(f"/reception/menage/{e.value}")) as datet:
        with ui.menu().props('no-parent-event') as menu:
            with ui.date().bind_value(datet):
                with ui.row().classes('justify-end'):
                    ui.button('Close', on_click=menu.close).props('flat')
        with datet.add_slot('append'):
            ui.icon('edit_calendar').on('click', menu.open).classes('cursor-pointer')


    with ui.row():
        for etage in range(2, 6):
            with ui.column():
                for i in range(1, 9):
                    chambre = etage * 100 + i
                    with ui.row():
                        ui.toggle({False: "X", True: chambre, "R": "R", "+": "R+", "?": "?"},
                                  value=chambres[chambre],
                                  on_change=lambda value, chambre=chambre:
                                    submit(chambre, value))
                        ui.input("Note",
                                 value=chambres_notes[chambre],
                                 on_change=lambda value, chambre=chambre:
                                    submit(chambre, value, note=True))

@ui.page("/menage")
def menage():
    user = app.storage.user.get("user", "Error")
    header()
    ui.button("Ménage", on_click=lambda: ui.navigate.to(f"/menage/menage"))

@ui.page("/menage/menage")
@ui.page("/menage/menage/")
@ui.page("/menage/menage/{dateStr}")
def menageMenage(dateStr=False):
    user = app.storage.user.get("user", "Error")

    if dateStr:
        dateTarget = datetime.strptime(dateStr, "%Y-%m-%d").date()
    else:
        ui.navigate.to(f'/menage/menage/{date.today().strftime("%Y-%m-%d")}')
        return
    
    menages = select(menage for menage in ListMenage
                        if menage.date == dateTarget)\
                .order_by(lambda x: x.chambre.numero)
    
    # DISPLAY
    header(accueil=False)

    with ui.input('Date', value=dateStr).on_value_change(lambda e: ui.navigate.to(f"/menage/menage/{e.value}")) as datet:
        with ui.menu().props('no-parent-event') as menu:
            with ui.date().bind_value(datet):
                with ui.row().classes('justify-end'):
                    ui.button('Close', on_click=menu.close).props('flat')
        with datet.add_slot('append'):
            ui.icon('edit_calendar').on('click', menu.open).classes('cursor-pointer')

    for menage in menages:
        ui.button(f"""{menage.chambre.numero}
                  {"R" if menage.recouche else ""}
                  {"R+" if menage.recouchePlus else ""}
                  {"?" if menage.verifier else ""}
                  {menage.note}""")


if __name__ == "__main__":
    ui.run(
        storage_secret= 'aurisetnaruaruiealudieauinrasuireastuiraranrui',
        title= "Hôtel Panorama Grasse",
        host= "0.0.0.0",
        port= 8083,
        show= False
    )

ui.run(
        storage_secret= 'aurisetnaruaruiealudieauinrasuireastuiraranrui',
        title= "Hôtel Panorama Grasse",
        host= "0.0.0.0",
        port= 8083,
        show= False
    )