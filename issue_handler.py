from tabulate import tabulate
from datetime import datetime
import os
import random
import string
import json

# ------------------------------------ Konfiguration ------------------------------------ #
# Allgemeine Konfigurationseinstellungen
configuration = {
    "priority": [ "low", "medium", "high" ],
    "type": ["bug", "feature", "improvement"],
    "default_type": "bug",
    "workflow": {
        "open": ["working", "rejected"],
        "working": ["rejected", "testing", "resolved"],
        "testing": ["working", "resolved"],
    }
}

# Grundstruktur von einem Vorgang
issue_structure = {
    "id": None,
    "status": "open",
    "type": None,
    "summary": None,
    "description": None,
    "priority": "medium",
    "created_by": None,
    "created_at": None
}

# ------------------------------------ Konfiguration ------------------------------------ #

# Initialisieren von dem Datenverzeichnis
# path          Daten-Oberverzeichnis
def initialize_bugtracker(path):

    # Existiert in dem angeben Verzeichnis bereits ein .mbt Datenordner?
    if not os.path.isdir(os.path.join(path, ".mbt")) and not os.path.exists(os.path.join(path, ".mbt")):
        try:
            os.mkdir(os.path.join(path, ".mbt"))
        except OSError as e:
            print(str(e)+"Verzeichnis .mbt konnte nicht erstellt werden")
            return False

        print("MBT wurde erfolgreich initialisiert")
        return True
    else:
        print("Initialisierung fehlgeschlagen: Verzeichnis .mbt existiert bereits")
        return False



# Erzeugen von einem neuen Vorgang
# summary       Titel des Vorgangs
# description   Beschreibung des Vorgangs
# type          Vorgangstyp
# path          Daten-Oberverzeichnis
def new_issue(summary, description, type, path):
    full_path=os.path.join(path, ".mbt")

    # Existiert das Datenverzeichnis und ist es beschreibbar?
    if os.path.isdir(full_path) and os.access(path, os.W_OK):

        # Erzeuge solange eine Vorgang-ID bis keine Kollision im Datenverzeichnis auftritt
        while True:
            new_id = generateID(10)

            if not os.path.isfile(os.path.join(full_path, new_id)):
                break

        # Setzen der Felder
        issue_structure['id']=new_id
        issue_structure['summary']=summary
        issue_structure['description']=description
        issue_structure['created_at']=datetime.now().strftime('%d-%m-%Y %H:%M')

        # Fallunterscheidung fuer den Vorgangstyp es wird der default_type gesetzt falls beim Aufruf kein Typ
        # uebergeben wurde
        if type==None:
            issue_structure['type'] = configuration['default_type']
        else:
            if type in configuration['type']:
                issue_structure['type'] = type
            else:
                print("Ungüeltiger Vorgangstyp, gueltige Werte sind: " + ', '.join(configuration['type']))
                return False

        try:
            with open(os.path.join(full_path, new_id), 'w') as fh:
                json.dump(issue_structure, fh)
        except:
            print("Der Vorgang konnte nicht erstellt werden")
            return False

        print("Es wurde ein neues Ticket mit der ID: \""+new_id+"\" erstellt")
        return True
    else:
        print("Das Verzeichnis "+path+" existiert nicht oder ist nicht schreibbar")
        return False



# Anzeigen von einem vorhandenen Vorgang
# id            Vorgangs-ID
# path          Daten-Oberverzeichnis
def show_issue(id, path):
    # Liste der Titel und Vorgangs-Felder
    fields=[['id', 'ID'],
            ['status', 'Status'],
            ['summary','Titel'],
            ['description', 'Beschreibung'],
            ['priority','Prioritaet'],
            ['created_by', 'Erstellt von'],
            ['created_at', 'Erstellt am']]

    issue_details = []
    full_path = os.path.join(path, ".mbt")

    # Existiert das Datenverzeichnis und ist es lesbar?
    if os.path.isdir(full_path) and os.access(path, os.R_OK):

        # Existiert der uebergebene Vorgang (Dateiname == ID) und ist er lesbar?
        if os.path.isfile(os.path.join(full_path, id)) and os.access(os.path.join(full_path, id), os.R_OK):
            try:
                with open(os.path.join(full_path, id)) as fh:
                    issue = json.load(fh)
            except OSError as e:
                print(str(e)+" Vorgang "+id+" konnte nicht gelesen werden")
                return False

            for i in fields:
                if i[0] in issue:
                    field_name = i[1]+" ("+i[0]+"): "
                    if issue[i[0]] != None:
                        issue_details.extend([[field_name, issue[i[0]]]])
                    else:
                        issue_details.extend([[field_name, "---"]])

            print(tabulate(issue_details))
            return True
        else:
            print("Der Vorgang existiert nicht oder ist nicht lesbar")
            return False
    else:
        print("Das Verzeichnis " + path + " existiert nicht oder ist nicht schreibbar")
        return False



# Bearbeiten von einem vorhandenen Vorgang
# id            Vorgangs-ID
# key           Feldname der geaendert werden soll
# value         neuer Wert fuer das Feld
# path          Daten-Oberverzeichnis
def edit_issue(id, key, value, path):
    # Liste der bearbeitbarer Felder
    modifiable = ['summary', 'description', 'priority' ]
    full_path = os.path.join(path, ".mbt")

    # Falls die Prioritaet geaendert werden soll, liegt der neue Wert im gueltigen Bereich?
    if key == 'priority' and value not in configuration['priority']:
        print("Fuer priority sind nur die Werte hight, medium, low gueltig")
        return False

    # Ist das uebergebene Feld bearbeitbar?
    if key in modifiable:

        # Existiert das Daten-Verzeichnis und ist es schreibbar?
        if os.path.isdir(full_path) and os.access(path, os.W_OK):

            # Existiert der Vorgang (Vorgangs-ID == Dateiname) und ist er sowohl les- als auch schreibbar?
            if os.path.isfile(os.path.join(full_path, id)) and os.access(os.path.join(full_path, id), os.W_OK) and os.access(os.path.join(full_path, id), os.R_OK):

                try:
                    with open(os.path.join(full_path, id)) as fh:
                        issue = json.load(fh)
                except OSError as e:
                    print("Vorgang " + id + " konnte nicht gelesen werden")
                    return False

                issue[key]=value

                try:
                    with open(os.path.join(full_path, id), 'w') as fh:
                        json.dump(issue, fh)
                except OSError as e:
                    print"Vorgang " + id + " konnte nicht geschrieben werden")
                    return False

                print("Vorgang "+id+" wurde erfolgreich aktualisiert")
                return False
            else:
                print("Der Vorgang existiert nicht oder ist nicht lesbar")
                return False
        else:
            print("Das Verzeichnis "+path+" existiert nicht oder ist nicht schreibbar")
            return False
    else:
        print("Es sind nur folgende Felder bearbeitbar: "+', '.join(modifiable))
        return False



# Auflisten aller Vorgaenge
# path          Daten-Oberverzeichnis
def list_issue(path):
    full_path = os.path.join(path, ".mbt")
    issues_list = []

    # Existiert das Daten-Verzeichnis und ist es lesbar?
    if os.path.isdir(full_path) and os.access(path, os.R_OK):
        for f in os.listdir(full_path):
            try:
                with open(os.path.join(full_path, f)) as fh:
                     issue = json.load(fh)
            except:
                continue

            if len(issue['summary']) > 20:
                summary = issue['summary'][:17]+"..."
            else:
                summary = issue['summary']

            issues_list.extend([[issue['id'], summary, issue['type'], issue['status']]])

        print(tabulate(issues_list, headers=['ID', 'Titel', 'Type', 'Status']))
        return False

    else:
        print("Ticket-Verzeichnis ist nicht lesbar")
        return True



# Aendern von dem Status eines Vorgangs
# id            Vorgangs-ID
# status        Neuer Status des Vorgangs
# path          Daten-Oberverzeichnis
def status_issue(id, status, path):
    full_path = os.path.join(path, ".mbt")

    # Existiert das Daten-Oberverzeichnis und ist es beschreibbar?
    if os.path.isdir(full_path) and os.access(path, os.W_OK):

        # Existiert der Vorgang (Vorgangs-ID == Datename) und ist die Datei les- und schreibbar?
        if os.path.isfile(os.path.join(full_path, id)) and os.access(os.path.join(full_path, id), os.W_OK) and os.access(os.path.join(full_path, id), os.R_OK):

            try:
                with open(os.path.join(full_path, id)) as fh:
                    issue = json.load(fh)
            except:
                print("Der Vorgang konnte nicht gelesen werden")
                return False

            # hat der Vorgang einen gueltigen Status
            if issue['status'] in configuration['workflow']:

                # Existiert eine Transition in den uebergebenen Status?
                if status in configuration['workflow'][issue['status']]:
                    issue['status']=status

                    try:
                        with open(os.path.join(full_path, id), 'w') as fh:
                            json.dump(issue, fh)
                    except:
                        print("Der Vorgang konnte nicht aktualisiert werden")
                        return False

                    print("Vorgang wurde erfolgreich aktualisiert")
                    return True
                else:
                    print("Ungueltiger Zielzustand, erlaubt sind nur: "+', '.join(configuration['workflow'][issue['status']]))
                    return False
            else:
                print("Der Vorgang hat einen ungueltigen Zustand")
                return False

        else:
            print("Der Vorgang existiert nicht oder ist nicht lesbar")
            return False
    else:
        print("Das Verzeichnis " + path + " existiert nicht oder ist nicht schreibbar")
        return False



# Erzeugen von einem zufaelligen String
# n             Laenge des Strings der erzeugt werden soll
def generateID(n):
    return ''.join([random.choice(string.ascii_uppercase + string.digits + string.ascii_lowercase ) for i in range(n)])


