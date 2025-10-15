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
    AbstractMeasureElement = EClass('AbstractMeasureElement')
    Observation = EClass('Observation')
    ObservedMeasure = EClass('ObservedMeasure')
    Measure = EClass('Measure')
    Measurement = EClass('Measurement')
    Attribute = EClass('Attribute')

    # Fügen Sie diese Zeilen im Abschnitt "Klassen" oder direkt danach hinzu:

    # inheritance
    Measure.eSuperTypes.append(AbstractMeasureElement)

    # Attributes
    Observation.eStructuralFeatures.extend([
        EAttribute('whenObserved', EFloat, upper=1)  # as time is defined as seconds past
    ])

    Measure.eStructuralFeatures.extend([
        EAttribute('name', EString),
        EAttribute('source', EString, upper=1),
    ])

    # references
    Observation.eStructuralFeatures.append(
        EReference('requestedMeasures', AbstractMeasureElement, upper=-1)
    )

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
        AbstractMeasureElement,
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
    dot = Digraph(comment=epackage.name)

    # Knoten für jede Klasse
    for cls in epackage.eClassifiers:
        if isinstance(cls, EClass):
            attrs = [f'{a.name}: {a.eType.name}' for a in cls.eStructuralFeatures if isinstance(a, EAttribute)]
            label = f'{cls.name}\n' + '\n'.join(attrs)
            dot.node(cls.name, label=label, shape='box')

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

    dot.render('smm_metamodel.gv', view=True)  # erzeugt und öffnet die Datei
    print("✅ Diagramm erstellt: smm_metamodel.gv.pdf")


