from pymongo import MongoClient
from pymongo.server_api import ServerApi
import matplotlib.pyplot as plt

# MongoDB connection
uri = "mongodb://msr:fooBar@localhost:27017/?authMechanism=DEFAULT"
client = MongoClient(uri, server_api=ServerApi('1'))
db = client.get_database('sdc_sim_data')
collection = db['campaign_2_frenetic']

# find one document
doc = collection.find_one()
execution_data = doc.get("execution_data", {})
simulation_data = execution_data.get("simulation_data", [])

print("Type of simulation_data:", type(simulation_data))
print("Length of simulation_data:", len(simulation_data))

if len(simulation_data) > 0:
    print("First item keys:", simulation_data[0].keys())

# all wheels: FL, FR, RL, RR
times = []
brake_core = {"FL": [], "FR": [], "RL": [], "RR": []}
brake_surface = {"FL": [], "FR": [], "RL": [], "RR": []}

# collect data
for frame in simulation_data:
    sensors = frame.get("sensors", {}).get("_data", {})
    wheel_thermals = sensors.get("wheelThermals", {})

    times.append(frame.get("time"))
    for wheel in ["FL", "FR", "RL", "RR"]:
        if wheel in wheel_thermals:
            data = wheel_thermals[wheel]
            brake_core[wheel].append(data.get("brakeCoreTemperature"))
            brake_surface[wheel].append(data.get("brakeSurfaceTemperature"))

# plotting
plt.figure(figsize=(12, 6))

for wheel in ["FL", "FR", "RL", "RR"]:
    plt.plot(times, brake_core[wheel], label=f"Core {wheel}")
    plt.plot(times, brake_surface[wheel], label=f"Surface {wheel}", linestyle='--')

plt.xlabel("Time [s]")
plt.ylabel("Temperature [°C]")
plt.title("Brake Core and Surface Temperatures for All Wheels")
plt.legend()
plt.grid(True)
plt.show()
