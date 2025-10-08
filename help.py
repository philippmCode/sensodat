from pyecore.resources import ResourceSet, URI
from pathlib import Path
from pyecore.ecore import EPackage

folder = Path(__file__).resolve().parent / 'data' / 'models'
rset = ResourceSet()

# pyecore eigenes Ecore-Metamodel ist schon eingebaut
# Wir registrieren SMM direkt darauf
smm_res = rset.get_resource(URI(str(folder / 'SMM.cmof')))
smm_metamodel = smm_res.contents[0]

# nsURI setzen, falls None
if smm_metamodel.nsURI is None:
    smm_metamodel.nsURI = 'http://smm/2017'  # Beispiel-URI

rset.metamodel_registry[smm_metamodel.nsURI] = smm_metamodel

print("Metamodel geladen:", smm_metamodel)
