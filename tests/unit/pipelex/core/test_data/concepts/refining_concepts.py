"""Refining concept test cases."""

from pipelex.core.bundles.pipelex_bundle_blueprint import PipelexBundleBlueprint
from pipelex.core.concepts.concept_blueprint import ConceptBlueprint

CONCEPTS_WITH_REFINES = (
    "concepts_with_refines",
    """domain = "refining_concepts"
definition = "Domain with concepts that refine others"

[concept]
Concept1 = "A concept1"
Concept2 = "A concept2"

[concept.Concept3]
definition = "A concept3"
refines = "Concept2"
""",
    PipelexBundleBlueprint(
        domain="refining_concepts",
        definition="Domain with concepts that refine others",
        concept={
            "Concept1": "A concept1",
            "Concept2": "A concept2",
            "Concept3": ConceptBlueprint(definition="A concept3", refines="Concept2"),
        },
    ),
)

# Export all refining concept test cases
REFINING_CONCEPT_TEST_CASES = [
    CONCEPTS_WITH_REFINES,
]
