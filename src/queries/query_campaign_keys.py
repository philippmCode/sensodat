from pymongo import MongoClient
from pymongo.server_api import ServerApi
from pprint import pprint

# finds out the folder (key) names in the MongoDB document structure
# MongoDB connection
uri = "mongodb://msr:fooBar@localhost:27017/?authMechanism=DEFAULT"
client = MongoClient(uri, server_api=ServerApi('1'))
db = client.get_database('sdc_sim_data')
collection = db['campaign_2_frenetic']

doc = collection.find_one()

if doc:
    print("-" * 50)
    print(f"Analyse der Struktur des Dokuments mit ID: {doc.get('_id')}")
    print("-" * 50)

    # A. Ebene 0: Dokument-Schlüssel (Oberste Ebene)
    print("A. Schlüssel (Ordner) auf der obersten Dokument-Ebene:")
    pprint(list(doc.keys()))
    print("-" * 50)

    # B. Ebene 1: execution_data-Schlüssel
    execution_data = doc.get("execution_data", {})
    if execution_data:
        print("B. Schlüssel (Ordner) innerhalb von 'execution_data':")
        pprint(list(execution_data.keys()))
    else:
        print("B. 'execution_data' ist nicht vorhanden oder leer.")
    print("-" * 50)

    # C. Ebene 2: simulation_data-Schlüssel (Innere Listenelemente)
    simulation_data = execution_data.get("simulation_data", [])

    # Da simulation_data ein Array (Liste) ist, analysieren wir das ERSTE Element davon.
    if simulation_data and isinstance(simulation_data, list) and len(simulation_data) > 0:
        first_sim_entry = simulation_data[0]

        print(f"C. Schlüssel (Ordner) innerhalb eines 'simulation_data'-Eintrags (Listenlänge: {len(simulation_data)}):")

        # Prüfen, ob das erste Element ein Dictionary ist
        if isinstance(first_sim_entry, dict):
            pprint(list(first_sim_entry.keys()))
        else:
            print(f"  Das erste Element in 'simulation_data' ist kein Dictionary, sondern vom Typ: {type(first_sim_entry)}")
    else:
        print("C. 'simulation_data' ist nicht vorhanden, leer oder kein Array.")

else:
    print("-" * 50)
    print("Kein Dokument in der Kollektion gefunden.")