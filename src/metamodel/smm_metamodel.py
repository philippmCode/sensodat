from pyecore.ecore import EPackage, EClass, EAttribute, EReference, EString, EBoolean, EFloat
from pyecore.resources import global_registry
from graphviz import Digraph


def create_smm_metamodel():
    """
    Programmatically defines the Software Measurement Metamodel (SMM)
    using pyecore and registers it globally.

    :return: The defined EPackage instance ('smm').
    """

    smm = EPackage('smm', nsuri='http://example.org/smm', prefix='smm')

    # Classes
    Observation = EClass('Observation')
    ObservedMeasure = EClass('ObservedMeasure')
    Measure = EClass('Measure')
    Measurement = EClass('Measurement')
    Attribute = EClass('Attribute')

    # Attributes
    Observation.eStructuralFeatures.extend([
        EAttribute('whenObserved', EFloat, upper=1)  # as time is defined as seconds past
    ])

    Measure.eStructuralFeatures.extend([
        EAttribute('name', EString),
        EAttribute('source', EString, upper=1),
    ])

    Observation.eStructuralFeatures.extend([
        EReference('observedMeasures', ObservedMeasure, upper=-1, containment=True)
    ])

    ObservedMeasure.eStructuralFeatures.extend([
        EReference('measure', Measure, containment=True),
        EReference('measurements', Measurement, upper=-1, containment=True)
    ])

    Attribute.eStructuralFeatures.extend([
        EAttribute('tag', EString),
        EAttribute('value', EString)
    ])

    Measurement.eStructuralFeatures.append(
        EReference('attributes', Attribute, upper=-1, containment=True)
    )

    Measurement.eStructuralFeatures.append(
        EReference('observedMeasure', ObservedMeasure)
    )

    # register classes within the package
    smm.eClassifiers.extend([
        Observation,
        ObservedMeasure,
        Measure,
        Measurement,
        Attribute
    ])

    # register the package globally
    from pyecore.resources import global_registry
    global_registry[smm.nsURI] = smm

    print('✅ smm_metamodel done.')

    return smm

def visualize_metamodel(epackage):
    dot = Digraph(comment=epackage.name, format='pdf')
    dot.attr(rankdir='BT')  # Klassenhierarchie von oben nach unten

    # Knoten für jede Klasse
    for cls in epackage.eClassifiers:
        if isinstance(cls, EClass):
            # Attribute extrahieren
            attrs = [f'{a.name}: {a.eType.name}' for a in cls.eStructuralFeatures if isinstance(a, EAttribute)]
            attr_text = '\l'.join(attrs) + ('\l' if attrs else '')

            # Klassenname (kursiv, wenn abstrakt)
            cls_name = f"<i>{cls.name}</i>" if getattr(cls, 'abstract', False) or cls.name.lower().startswith('abstract') else cls.name

            # Label als UML-typisches Klassendiagramm
            label = f'{{{cls_name}|{attr_text}}}'
            dot.node(cls.name, label=label, shape='record')

    # Kanten für Vererbungen
    for cls in epackage.eClassifiers:
        if isinstance(cls, EClass):
            for parent in cls.eSuperTypes:
                dot.edge(parent.name, cls.name, arrowhead='onormal')

    # Kanten für Referenzen
    for cls in epackage.eClassifiers:
        if isinstance(cls, EClass):
            for ref in cls.eReferences:
                target_name = ref.eType.name
                dot.edge(cls.name, target_name, label=ref.name, style='dashed')

    # Rendern
    dot.render('smm_metamodel.gv', view=True)
    print("✅ UML-ähnliches Diagramm erstellt: smm_metamodel.gv.pdf")



