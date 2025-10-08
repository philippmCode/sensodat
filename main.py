from src.metamodel.metamodel_loader import load_smm_metamodel

metamodel, rset = load_smm_metamodel()
print("Loaded metamodel:", metamodel.name)
