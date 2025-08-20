from pymongo import MongoClient
from pymongo.server_api import ServerApi
import pprint

uri = "mongodb://msr:fooBar@localhost:27017/?authMechanism=DEFAULT"
client = MongoClient(uri, server_api=ServerApi('1'))
db = client.get_database('sdc_sim_data')

# Alle Collections anzeigen
print("Collections:", db.list_collection_names())

# Ein Dokument vollständig anzeigen
collection = db['campaign_2_frenetic']
doc = collection.find_one()
#pprint.pprint(doc)
