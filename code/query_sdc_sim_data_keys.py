from pymongo import MongoClient
from pymongo.server_api import ServerApi

# --- MongoDB-Verbindung und Setup ---
uri = "mongodb://msr:fooBar@localhost:27017/?authMechanism=DEFAULT"
client = MongoClient(uri, server_api=ServerApi('1'))

# Wählen Sie die Datenbank aus, die Sie untersuchen möchten
db_name = 'sdc_sim_data'
db = client.get_database(db_name)

try:
    client.admin.command('ping')
    print("MongoDB-Verbindung erfolgreich.")
except Exception as e:
    print(f"Fehler bei der MongoDB-Verbindung: {e}")
    exit()

# --- Abrufen der Kollektionsnamen (Ihre "Ordner") ---

print("-" * 50)
print(f"Abrufen der Kollektionen in der Datenbank '{db_name}'...")

# Dies ist der entscheidende Befehl: Er listet alle Kollektionen der Datenbank auf.
collection_names = db.list_collection_names()

if collection_names:
    print(f"Die folgenden Kollektionen ('Ordner') sind in '{db_name}' enthalten:")

    # Sortieren Sie die Namen der Übersichtlichkeit halber
    collection_names.sort()

    for name in collection_names:
        print(f"- {name}")
else:
    print(f"Die Datenbank '{db_name}' enthält keine Kollektionen.")

print("-" * 50)