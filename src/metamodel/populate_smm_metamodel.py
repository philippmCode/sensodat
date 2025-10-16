from collections import defaultdict

from pymongo import MongoClient
from pymongo.server_api import ServerApi
from graphviz import Digraph

# MongoDB connection string: assumes user 'msr' with password 'fooBar' on localhost:27017
MONGO_URI = "mongodb://msr:fooBar@localhost:27017/?authMechanism=DEFAULT"


def get_mongodb_data():
    """
    Establishes the MongoDB connection and retrieves the raw simulation data.

    Reads the first document and extracts the time-series sensor data from the
    nested 'execution_data' field (representing the raw M0 data).

    :return: A list of dictionaries containing simulation frames, or an empty list
             if an error occurs.
    """
    try:
        # Connect to MongoDB client
        client = MongoClient(MONGO_URI, server_api=ServerApi('1'))
        # Get the database named 'sdc_sim_data'
        db = client.get_database('sdc_sim_data')
        # Get the collection named 'campaign_2_frenetic'
        collection = db['campaign_2_frenetic']

        # Retrieve the first document from the collection
        doc = collection.find_one()
        # Extract 'execution_data', defaulting to an empty dict
        execution_data = doc.get("execution_data", {})
        # Extract 'simulation_data' (the list of time-series frames), defaulting to an empty list
        simulation_data = execution_data.get("simulation_data", [])
        return simulation_data
    except Exception as e:
        # Print the error if the connection or data retrieval fails
        print(f"Error while loading MongoDB data: {e}")
        return []


def populate_smm_model(smm_package, simulation_data):
    """
    Creates an SMM model instance from arbitrary sensor data frames (M0 data).

    It maps each time-series frame to an SMM Observation and the sensor values
    within it to ObservedMeasures and Measurements.

    :param smm_package: The loaded SMM meta-model package containing the EClasses.
    :param simulation_data: The list of raw simulation data frames (time-series).
    :return: A tuple containing:
             - all_observations (list): List of created SMM Observation instances.
             - measures_cache (dict): Dictionary mapping measure names to created SMM Measure instances.
    """

    # Load required classes from the SMM package
    Measure = smm_package.getEClassifier('Measure')
    Observation = smm_package.getEClassifier('Observation')
    ObservedMeasure = smm_package.getEClassifier('ObservedMeasure')
    Measurement = smm_package.getEClassifier('Measurement')
    Attribute = smm_package.getEClassifier('Attribute')

    all_observations = []
    # Cache to store unique Measure instances and reuse them across different frames
    measures_cache = {}

    # Helper function: Cache or create a new Measure instance
    def get_or_create_measure(name, source='Simulated Sensor', scale=''):
        """Retrieves an existing Measure instance or creates a new one if it doesn't exist."""
        if name not in measures_cache:
            # Create a new Measure instance and cache it
            measures_cache[name] = Measure(name=name, source=source, scale=scale)
        return measures_cache[name]

    # Process each simulation frame (time-series entry)
    for frame in simulation_data:
        # Extract the time value for 'whenObserved'
        time_value = float(frame.get("time", 0.0))
        # Extract the sensor data
        sensors = frame.get("sensors", {}).get("_data", {})

        # Create a new SMM Observation instance for the current time frame
        current_observation = Observation(
            observer='SDC-Simulator',
            tool='sdc_sim',
            whenObserved=time_value
        )

        # Iterate over all sensor values in the frame
        for sensor_name, sensor_value in sensors.items():
            # Handle 'wheelThermals' which has a nested dictionary structure (wheel -> temp_type -> value)
            if sensor_name == "wheelThermals" and isinstance(sensor_value, dict):
                for wheel, data in sensor_value.items():
                    for temp_type, temp_val in data.items():
                        if temp_val is None:
                            continue

                        # Create a unique Measure name based on temp type and wheel
                        measure = get_or_create_measure(f"{temp_type}_{wheel}")

                        # Create a Measurement instance
                        measurement = Measurement()

                        # Add contextual data as SMM Attributes to the Measurement
                        measurement.attributes.append(
                            Attribute(tag="wheel", value=wheel)
                        )
                        measurement.attributes.append(
                            Attribute(tag="type", value=temp_type)
                        )
                        # Store the actual sensor value as an Attribute
                        measurement.attributes.append(
                            Attribute(tag="value", value=str(temp_val))
                        )

                        # Link the Measure and the Measurement via ObservedMeasure
                        observed_measure = ObservedMeasure(measure=measure)
                        observed_measure.measurements.append(measurement)

                        # Add the ObservedMeasure to the current Observation
                        current_observation.observedMeasures.append(observed_measure)

            # Handle normal sensor data (flat structure)
            elif isinstance(sensor_value, (int, float, bool, str)):
                # Get or create the Measure instance using the sensor name
                measure = get_or_create_measure(sensor_name)

                # Create Measurement instance (breakValue='' is often used for simple measurements)
                measurement = Measurement(breakValue='')

                # Link Measure and Measurement
                observed_measure = ObservedMeasure(measure=measure)
                observed_measure.measurements.append(measurement)

                # Add the ObservedMeasure to the Observation
                current_observation.observedMeasures.append(observed_measure)

                # Store the actual sensor value as an Attribute on the Measurement
                attribute = Attribute(tag=sensor_name, value=str(sensor_value))
                measurement.attributes.append(attribute)

            else:
                # Skip sensor values with unsupported or unexpected structures
                continue

        all_observations.append(current_observation)

    return all_observations, measures_cache

import random

def visualize_model_instances(observations, limit_measurements=15, max_measures=3):
    dot = Digraph(comment="SMM Model Instances")

    # Vordefinierte Measure-Knoten
    measure_nodes = {
        "temperature": "Measure: Temperature",
        "speed": "Measure: Speed"
    }
    for key, label in measure_nodes.items():
        dot.node(f"measure_{key}", label, shape="box", style="filled", color="lightblue")

    om_to_measurements = defaultdict(list)
    obs_map = {}

    for obs in observations:
        for om in getattr(obs, "observedMeasures", []):
            om_name = getattr(om.measure, "name", "").lower()
            for m in getattr(om, "measurements", []):
                attr_text = " ".join(f"{getattr(a, 'tag', '').lower()} {getattr(a, 'value', '').lower()}"
                                     for a in getattr(m, "attributes", []))
                combined_text = f"{om_name} {attr_text}"
                if "_temperature" in combined_text or "speed" in combined_text:
                    om_to_measurements[om].append(m)
                    obs_map[m] = (obs, om)

    selected_oms = random.sample(list(om_to_measurements.keys()), min(max_measures, len(om_to_measurements)))
    selected_measurements = []
    remaining = limit_measurements
    for om in selected_oms:
        ms = om_to_measurements[om]
        if len(ms) > remaining:
            ms = random.sample(ms, remaining)
        selected_measurements.extend(ms)
        remaining -= len(ms)
        if remaining <= 0:
            break

    drawn_obs = set()
    drawn_oms = set()

    for m in selected_measurements:
        obs, om = obs_map[m]

        if obs not in drawn_obs:
            observer = getattr(obs, "observer", "")
            when_observed = getattr(obs, "whenObserved", "")
            dot.node(f"obs_{id(obs)}", f"Observation\nobserver={observer}\nwhenObserved={when_observed}",
                     shape="box", style="filled", color="lightgray")
            drawn_obs.add(obs)

        # ObservedMeasure als Ellipse
        if om not in drawn_oms:
            om_name = getattr(om.measure, "name", "")
            dot.node(f"om_{id(om)}", f"ObservedMeasure",
                     shape="ellipse", color="black", width="1.5")
            dot.edge(f"obs_{id(obs)}", f"om_{id(om)}")
            drawn_oms.add(om)

            # Verbindung zu Measures
            om_text = om_name.lower()
            for a in getattr(m, "attributes", []):
                om_text += f" {getattr(a,'tag','').lower()} {getattr(a,'value','').lower()}"
            for key in measure_nodes.keys():
                if key in om_text:
                    dot.edge(f"om_{id(om)}", f"measure_{key}", color="blue", style="bold")

        # Measurement als Ellipse
        dot.node(f"m_{id(m)}", "Measurement", shape="ellipse", color="black", width="1.2")
        dot.edge(f"om_{id(om)}", f"m_{id(m)}")

        for a in getattr(m, "attributes", []):
            tag = getattr(a, "tag", "")
            value = getattr(a, "value", "")
            dot.node(f"a_{id(a)}", f"Attribute\n{tag}: {value}", shape="ellipse", color="black")
            dot.edge(f"m_{id(m)}", f"a_{id(a)}", style="dotted")

    dot.render("smm_model_instances.gv", view=True)
    print("✅ Model visualization saved as 'smm_model_instances.gv'")
