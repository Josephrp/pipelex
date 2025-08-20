"""Integration tests for inline structure definitions in concepts."""

from typing import Dict

import pytest

from pipelex.core.concepts.concept_blueprint import (
    ConceptBlueprint,
    ConceptStructureBlueprint,
    ConceptStructureBlueprintFieldType,
    ConceptStructureBlueprintType,
)
from pipelex.core.concepts.concept_factory import ConceptFactory
from pipelex.core.stuffs.stuff_content import StructuredContent
from pipelex.exceptions import StructureClassError
from pipelex.hub import get_class_registry


class TestInlineStructureConcepts:
    """Test inline structure definitions in concept blueprints."""

    def test_inline_structure_definition_creation(self):
        """Test that concepts with inline structure definitions are created correctly."""
        # Define inline structure with mixed syntax
        inline_structure: Dict[str, ConceptStructureBlueprintType] = {
            "dominant_feature": ConceptStructureBlueprint(
                type=ConceptStructureBlueprintFieldType.TEXT, definition="The most important feature", required=False
            ),
            "visual_elements": ConceptStructureBlueprint(
                type=ConceptStructureBlueprintFieldType.TEXT, definition="Key visual elements", required=False
            ),
            "composition": ConceptStructureBlueprint(
                type=ConceptStructureBlueprintFieldType.TEXT, definition="Analysis of the image composition", required=False
            ),
            "color_palette": ConceptStructureBlueprint(
                type=ConceptStructureBlueprintFieldType.TEXT, definition="Description of the main colors", required=False
            ),
            "mood_atmosphere": "The overall mood or atmosphere",
        }

        # Create concept blueprint with inline structure
        blueprint = ConceptBlueprint(definition="Analysis of a photo's visual content", structure=inline_structure)

        # Create concept from blueprint
        concept = ConceptFactory.make_concept_from_blueprint(domain="test_domain", code="TestFeatureAnalysis", concept_blueprint=blueprint)

        # Verify concept properties
        assert concept.code == "test_domain.TestFeatureAnalysis"
        assert concept.definition == "Analysis of a photo's visual content"
        assert concept.structure_class_name == "TestFeatureAnalysis"
        assert concept.domain == "test_domain"

        # Verify the generated class is registered and accessible
        assert get_class_registry().has_class("TestFeatureAnalysis")
        generated_class = get_class_registry().get_required_subclass("TestFeatureAnalysis", StructuredContent)

        # Verify class structure
        assert issubclass(generated_class, StructuredContent)
        assert generated_class.__name__ == "TestFeatureAnalysis"

        # Test instantiation of generated class
        instance = generated_class(
            dominant_feature="A bright red car",  # pyright: ignore[reportCallIssue]
            visual_elements="Car, road, trees, sky",  # pyright: ignore[reportCallIssue]
            composition="Central composition with car in focus",  # pyright: ignore[reportCallIssue]
            color_palette="Red, green, blue, white",  # pyright: ignore[reportCallIssue]
        )

        assert instance.dominant_feature == "A bright red car"  # type: ignore
        assert instance.visual_elements == "Car, road, trees, sky"  # type: ignore
        assert instance.composition == "Central composition with car in focus"  # type: ignore
        assert instance.color_palette == "Red, green, blue, white"  # type: ignore
        assert instance.mood_atmosphere is None  # type: ignore

    def test_string_reference_structure_definition(self):
        """Test that string reference structure definitions still work."""
        # Create blueprint with string reference
        blueprint = ConceptBlueprint(definition="Test with string reference", structure="TextContent")

        # Create concept from blueprint
        concept = ConceptFactory.make_concept_from_blueprint(domain="test_domain", code="TestStringRef", concept_blueprint=blueprint)

        # Verify concept properties
        assert concept.code == "test_domain.TestStringRef"
        assert concept.definition == "Test with string reference"
        assert concept.structure_class_name == "TextContent"

    def test_auto_detection_structure(self):
        """Test auto-detection when no structure is specified."""
        # Create blueprint without structure
        blueprint = ConceptBlueprint(definition="Test auto-detection")

        # Create concept from blueprint
        concept = ConceptFactory.make_concept_from_blueprint(domain="test_domain", code="TestAutoDetect", concept_blueprint=blueprint)

        # Should default to TextContent since TestAutoDetect is not a registered class
        assert concept.structure_class_name == "TextContent"

    def test_inline_structure_with_complex_types(self):
        """Test inline structure with complex field types."""
        inline_structure: Dict[str, ConceptStructureBlueprintType] = {
            "title": ConceptStructureBlueprint(type=ConceptStructureBlueprintFieldType.TEXT, definition="Document title"),
            "tags": ConceptStructureBlueprint(
                type=ConceptStructureBlueprintFieldType.LIST,
                item_type=ConceptStructureBlueprintFieldType.TEXT,
                definition="List of tags",
                required=False,
            ),
            "metadata": ConceptStructureBlueprint(
                type=ConceptStructureBlueprintFieldType.DICT,
                key_type=ConceptStructureBlueprintFieldType.TEXT,
                value_type=ConceptStructureBlueprintFieldType.TEXT,
                definition="Metadata dictionary",
                required=False,
            ),
            "priority": ConceptStructureBlueprint(choices=["low", "medium", "high"], definition="Priority level", required=False),
            "page_count": ConceptStructureBlueprint(type=ConceptStructureBlueprintFieldType.INTEGER, definition="Number of pages", required=False),
            "is_active": ConceptStructureBlueprint(
                type=ConceptStructureBlueprintFieldType.BOOLEAN, definition="Whether document is active", required=False
            ),
        }

        blueprint = ConceptBlueprint(definition="Complex document structure", structure=inline_structure)

        concept = ConceptFactory.make_concept_from_blueprint(domain="test_domain", code="ComplexDocument", concept_blueprint=blueprint)

        # Verify concept creation
        assert concept.code == "test_domain.ComplexDocument"
        assert concept.structure_class_name == "ComplexDocument"

        # Verify the generated class works
        generated_class = get_class_registry().get_required_subclass("ComplexDocument", StructuredContent)

        # Test instantiation with complex types
        instance = generated_class(
            title="Test Document",
            tags=["test", "document"],
            metadata={"author": "Test Author", "version": "1.0"},
            priority="high",
            page_count=42,
            is_active=True,
        )

        assert instance.title == "Test Document"
        assert instance.tags == ["test", "document"]
        assert instance.metadata == {"author": "Test Author", "version": "1.0"}
        assert instance.priority == "high"
        assert instance.page_count == 42
        assert instance.is_active is True

    def test_invalid_string_reference_raises_error(self):
        """Test that invalid string references raise appropriate errors."""
        with pytest.raises(
            StructureClassError,
            match="Structure class 'NonExistentClass' set for concept 'TestInvalidRef' in domain 'test_domain' is \
not a registered subclass of StuffContent",
        ):
            _ = ConceptFactory.make_concept_from_blueprint(
                domain="test_domain",
                code="TestInvalidRef",
                concept_blueprint=ConceptBlueprint(definition="Test invalid reference", structure="NonExistentClass"),
            )

    def test_multiple_inline_structures_do_not_conflict(self):
        """Test that multiple inline structures with same field names don't conflict."""
        # First structure
        structure1: Dict[str, ConceptStructureBlueprintType] = {
            "name": ConceptStructureBlueprint(type=ConceptStructureBlueprintFieldType.TEXT, definition="Person name"),
            "age": ConceptStructureBlueprint(type=ConceptStructureBlueprintFieldType.INTEGER, definition="Person age", required=False),
        }

        blueprint1 = ConceptBlueprint(definition="Person information", structure=structure1)
        concept1 = ConceptFactory.make_concept_from_blueprint(domain="test_domain", code="Person", concept_blueprint=blueprint1)

        # Second structure with same field names but different context
        structure2: Dict[str, ConceptStructureBlueprintType] = {
            "name": "Product name",
            "age": ConceptStructureBlueprint(type=ConceptStructureBlueprintFieldType.INTEGER, definition="Product age in days", required=False),
        }

        blueprint2 = ConceptBlueprint(definition="Product information", structure=structure2)
        concept2 = ConceptFactory.make_concept_from_blueprint(domain="test_domain", code="Product", concept_blueprint=blueprint2)

        # Both should be created successfully
        assert concept1.structure_class_name == "Person"
        assert concept2.structure_class_name == "Product"

        # Both classes should be registered and independent
        person_class = get_class_registry().get_required_subclass("Person", StructuredContent)
        product_class = get_class_registry().get_required_subclass("Product", StructuredContent)

        assert person_class != product_class

        # Test instances are independent
        person = person_class(name="John Doe", age=30)
        product = product_class(name="Widget", age=365)

        assert person.name == "John Doe"
        assert product.name == "Widget"
        assert person.age == 30
        assert product.age == 365
