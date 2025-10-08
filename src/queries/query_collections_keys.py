from pymongo import MongoClient
from pymongo.server_api import ServerApi
from pprint import pprint

# --- MongoDB Connection and Setup ---
# The MongoDB connection URI
uri = "mongodb://msr:fooBar@localhost:27017/?authMechanism=DEFAULT"
client = MongoClient(uri, server_api=ServerApi('1'))

# Select the target database and collection (campaign)
DB_NAME = 'sdc_sim_data'
COLLECTION_NAME = 'campaign_2_frenetic'
db = client.get_database(DB_NAME)
collection = db[COLLECTION_NAME]

try:
    client.admin.command('ping')
    print("MongoDB connection successful.")
except Exception as e:
    print(f"Error during MongoDB connection: {e}")
    exit()

# --- Key Collection Sets ---
# Initialize sets to store unique keys found across ALL documents in the campaign.
unique_doc_keys = set()
unique_execution_keys = set()
unique_simulation_keys = set()

document_count = 0
key_analysis_limit = 1000  # Safety limit for simulation_data analysis

print("-" * 70)
print(f"Starting comprehensive key analysis for campaign: {COLLECTION_NAME}")
print("-" * 70)

# --- Iterate Over All Documents in the Campaign ---
# Find all documents. Using a cursor is memory-efficient.
for doc in collection.find():
    document_count += 1

    # A. Level 0: Top-Level Document Keys
    # Add all keys found in the current document to the set
    unique_doc_keys.update(doc.keys())

    # B. Level 1: Keys within 'execution_data'
    execution_data = doc.get("execution_data")
    if isinstance(execution_data, dict):
        unique_execution_keys.update(execution_data.keys())

        # C. Level 2: Keys within a 'simulation_data' entry
        simulation_data = execution_data.get("simulation_data")

        # Only analyze a sample of entries for performance reasons
        if document_count <= key_analysis_limit and isinstance(simulation_data, list):
            # Check the keys of every entry in the simulation_data array
            for entry in simulation_data:
                if isinstance(entry, dict):
                    unique_simulation_keys.update(entry.keys())

# --- Final Results Output ---

print(f"Total documents analyzed in {COLLECTION_NAME}: {document_count}")
print("\n" + "#" * 70)
print("FINAL UNIQUE KEY STRUCTURE FOUND ACROSS ALL DOCUMENTS")
print("#" * 70)

print("\nA. Top-Level Unique Keys (Folders) in the Campaign Documents:")
pprint(sorted(list(unique_doc_keys)))

print("\nB. Unique Keys (Folders) within 'execution_data':")
pprint(sorted(list(unique_execution_keys)))

# Note: This set contains keys from all simulation_data entries across all documents analyzed.
print("\nC. Unique Keys (Folders) within a single 'simulation_data' entry:")
pprint(sorted(list(unique_simulation_keys)))

print("-" * 70)