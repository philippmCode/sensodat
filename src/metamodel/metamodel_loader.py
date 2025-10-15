# main.py

# Import the required functions from separate scripts
from pyecore.resources import ResourceSet, URI

from metamodel.populate_smm_metamodel import visualize_model_instances
from metamodel.smm_metamodel import visualize_metamodel
from smm_metamodel import create_smm_metamodel
from populate_smm_metamodel import get_mongodb_data, populate_smm_model

if __name__ == "__main__":

    # 1. Define the Metamodel and load it into memory
    print("Starting metamodel definition...")
    # Calls the function to create and return the SMM EPackage instance
    smm_model = create_smm_metamodel()

    if not smm_model:
        print("❌ Metamodel could not be created. Aborting.")
        exit(1)
    else:
        print(f"✅ Metamodel '{smm_model.name}' successfully created.")

    # 2. Load the data
    print("Loading data from MongoDB...")
    # Retrieves the raw simulation data frames
    simulation_data = get_mongodb_data()

    if not simulation_data:
        print("❌ No data loaded. Aborting.")
    else:
        print(f"Reading {len(simulation_data)} frames.")

        # 3. Call the method for model population
        print("Starting model population...")
        # Maps the raw data (frames) to SMM model instances (Observations, MeasuredData, etc.)
        model_instance_data, measure_instances = populate_smm_model(smm_model, simulation_data)

        # 4. Result Check
        print(f"\n✅ Process complete. {len(model_instance_data)} Observation instances were created.")

        if model_instance_data:
            first_obs = model_instance_data[0]

            # ==========================================================
            # 5. XMI SAVING (NEW BLOCK)
            # ==========================================================
            print("\nStarting XMI persistence...")
            # Create a ResourceSet to manage models/resources
            rset = ResourceSet()
            # Define the output URI (file name)
            output_uri = URI("smm_simulation_output.xmi")
            # Create a new resource for the output file
            resource = rset.create_resource(output_uri)

            # Add all Observation instances (the primary model data) to the resource contents
            resource.contents.extend(model_instance_data)

            # Add all unique Measure instances (the definitions) to the resource contents
            resource.contents.extend(measure_instances.values())

            # Save the file (serializes the model instances to XMI)
            resource.save()
            print(f"✅ Model successfully saved")

            visualize_metamodel(smm_model)
            visualize_model_instances(model_instance_data)