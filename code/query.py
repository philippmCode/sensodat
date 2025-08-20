from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi

uri = "mongodb://msr:fooBar@localhost:27017/?authMechanism=DEFAULT"
client = MongoClient(uri, server_api=ServerApi('1'))
db = client.get_database('sdc_sim_data')

query_passing = \
    {
        "OpenDRIVE.header.sdc_test_info.@test_outcome": "PASS"
    }
nr_passing_tests = db['campaign_2_frenetic'] \
    .count_documents(filter=query_passing)

print(nr_passing_tests)