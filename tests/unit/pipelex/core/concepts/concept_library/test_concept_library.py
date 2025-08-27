from pipelex.core.concepts.concept_blueprint import ConceptBlueprint
from pipelex.core.concepts.concept_factory import ConceptFactory
from pipelex.core.concepts.concept_native import NATIVE_CONCEPTS_DATA, NativeConceptEnum
from pipelex.hub import get_concept_provider


class TestConceptLibrary:
    def test_is_image_concept(self):
        concept_library = get_concept_provider()
        native_image_concept = ConceptFactory.make_native_concept(native_concept_data=NATIVE_CONCEPTS_DATA[NativeConceptEnum.IMAGE])

        concept_1 = ConceptFactory.make_from_blueprint(
            domain="test",
            concept_code="TestConcept",
            blueprint=ConceptBlueprint(
                definition="Lorem Ipsum",
                structure="ImageContent",
            ),
        )

        concept_2 = ConceptFactory.make_from_blueprint(
            domain="test",
            concept_code="TestConcept2",
            blueprint=ConceptBlueprint(
                definition="Lorem Ipsum",
                refines="native.Image",
            ),
        )
        concept_3 = ConceptFactory.make_from_blueprint(
            domain="test",
            concept_code="TestConcept2",
            blueprint=ConceptBlueprint(
                definition="Lorem Ipsum",
                refines="Image",
            ),
        )

        concept_4 = ConceptFactory.make_from_blueprint(
            domain="test",
            concept_code="TestConcept4",
            blueprint=ConceptBlueprint(
                definition="Lorem Ipsum",
                structure="ImageContent",
            ),
        )

        concept_5 = ConceptFactory.make_from_blueprint(
            domain="test",
            concept_code="TestConcept5",
            blueprint=ConceptBlueprint(
                definition="Lorem Ipsum",
                structure="TextContent",
            ),
        )

        concept_6 = ConceptFactory.make_from_blueprint(
            domain="test",
            concept_code="TestConcept6",
            blueprint=ConceptBlueprint(
                definition="Lorem Ipsum",
                structure="PDFContent",
            ),
        )

        assert concept_library.is_image_concept(concept=native_image_concept) is True
        assert concept_library.is_image_concept(concept=concept_1) is True
        assert concept_library.is_image_concept(concept=concept_2) is True
        assert concept_library.is_image_concept(concept=concept_3) is True
        assert concept_library.is_image_concept(concept=concept_4) is True
        assert concept_library.is_image_concept(concept=concept_5) is False
        assert concept_library.is_image_concept(concept=concept_6) is False
