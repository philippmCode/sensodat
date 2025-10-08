from pyecore.ecore import EPackage, EClass, EAttribute, EReference, EString, EBoolean, EFloat


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
    ObservationScope = EClass('ObservationScope')
    ObservedMeasure = EClass('ObservedMeasure')
    Measure = EClass('Measure')
    Measurement = EClass('Measurement')
    Element = EClass('Element')
    Attribute = EClass('Attribute')

    # Fügen Sie diese Zeilen im Abschnitt "Klassen" oder direkt danach hinzu:

    # inheritance
    Measure.eSuperTypes.append(AbstractMeasureElement)

    # Attributes
    Observation.eStructuralFeatures.extend([
        EAttribute('observer', EString, upper=1),
        EAttribute('tool', EString, upper=1),
        EAttribute('whenObserved', EFloat, upper=1)  # as time is defined as seconds past
    ])

    ObservationScope.eStructuralFeatures.append(EAttribute('scopeUri', EString))

    Measure.eStructuralFeatures.extend([
        EAttribute('name', EString),
        EAttribute('measureLabelFormat', EString, upper=1),
        EAttribute('measurementLabelFormat', EString, upper=1),
        EAttribute('visible', EBoolean, upper=1, default_value=True),
        EAttribute('source', EString, upper=1),
        EAttribute('scale', EString, upper=1),
        EAttribute('customScale', EString, upper=1)
    ])

    Measurement.eStructuralFeatures.extend([
        EAttribute('breakValue', EString, upper=1),
        EAttribute('error', EString, upper=1)
    ])

    # references
    Observation.eStructuralFeatures.append(
        EReference('requestedMeasures', AbstractMeasureElement, upper=-1)
    )

    Observation.eStructuralFeatures.extend([
        EReference('scopes', ObservationScope, upper=-1, containment=True),
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
        EReference('measurand', Element)
    )

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
        ObservationScope,
        ObservedMeasure,
        Measure,
        Measurement,
        Element,
        Attribute
    ])

    # register the package globally
    from pyecore.resources import global_registry
    global_registry[smm.nsURI] = smm

    print('✅ smm_metamodel done.')

    return smm
