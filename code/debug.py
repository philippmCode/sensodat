from pymongo import MongoClient
from pymongo.server_api import ServerApi
import pprint

uri = "mongodb://msr:fooBar@localhost:27017/?authMechanism=DEFAULT"
client = MongoClient(uri, server_api=ServerApi('1'))
db = client.get_database('sdc_sim_data')
collection = db['campaign_2_frenetic']

# nur mal 5 Dokumente inspizieren
for i, doc in enumerate(collection.find().limit(5)):
    print(f"--- Dokument {i} ---")
    pprint.pprint(doc.keys())
