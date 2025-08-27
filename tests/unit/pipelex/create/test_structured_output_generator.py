"""Tests for structured output generator."""

from typing import Dict

from pipelex import pretty_print
from pipelex.core.concepts.concept_blueprint import ConceptStructureBlueprint, ConceptStructureBlueprintFieldType, ConceptStructureBlueprintType
from pipelex.core.concepts.concept_factory import ConceptFactory
from pipelex.create.structured_output_generator import StructureGenerator


class TestStructureGenerator:
    def test_simple_structure_generation(self):
        """Test generation of a simple structure with basic fields."""
        structure_blueprint = {
            "name": ConceptStructureBlueprint(definition="Name field", type=ConceptStructureBlueprintFieldType.TEXT, required=True),
            "age": ConceptStructureBlueprint(definition="Age field", type=ConceptStructureBlueprintFieldType.INTEGER, required=False),
            "active": ConceptStructureBlueprint(
                definition="Active status", type=ConceptStructureBlueprintFieldType.BOOLEAN, required=False, default_value=True
            ),
        }

        result = StructureGenerator().generate_from_structure_blueprint("TestModel", structure_blueprint)

        pretty_print(structure_blueprint, title="Source Blueprint")
        pretty_print(result, title="Generated Result")

        # Check the complete generated structure
        expected_result = (
            "from enum import Enum\n"
            "from pipelex.core.stuffs.stuff_content import StructuredContent\n"
            "from pydantic import Field\n"
            "from typing import Optional, List, Dict, Any, Literal\n"
            "\n\n"
            "class TestModel(StructuredContent):\n"
            '    """Generated TestModel class"""\n'
            "\n"
            '    name: str = Field(..., description="Name field")\n'
            '    age: Optional[int] = Field(default=None, description="Age field")\n'
            '    active: Optional[bool] = Field(default=True, description="Active status")\n'
        )
        assert result == expected_result

    def test_complex_types_generation(self):
        """Test generation with complex types like lists and dicts."""
        structure_blueprint = {
            "tags": ConceptStructureBlueprint(
                definition="List of tags", type=ConceptStructureBlueprintFieldType.LIST, item_type="text", required=False
            ),
            "metadata": ConceptStructureBlueprint(
                definition="Metadata dictionary", type=ConceptStructureBlueprintFieldType.DICT, key_type="text", value_type="text", required=False
            ),
            "scores": ConceptStructureBlueprint(
                definition="List of scores", type=ConceptStructureBlueprintFieldType.LIST, item_type="number", required=True
            ),
        }

        result = StructureGenerator().generate_from_structure_blueprint("ComplexModel", structure_blueprint)

        pretty_print(structure_blueprint, title="Source Blueprint")
        pretty_print(result, title="Generated Result")

        # Check the complete generated structure
        expected_result = (
            "from enum import Enum\n"
            "from pipelex.core.stuffs.stuff_content import StructuredContent\n"
            "from pydantic import Field\n"
            "from typing import Optional, List, Dict, Any, Literal\n"
            "\n\n"
            "class ComplexModel(StructuredContent):\n"
            '    """Generated ComplexModel class"""\n'
            "\n"
            '    tags: Optional[List[str]] = Field(default=None, description="List of tags")\n'
            '    metadata: Optional[Dict[str, str]] = Field(default=None, description="Metadata dictionary")\n'
            '    scores: List[float] = Field(..., description="List of scores")\n'
        )
        assert result == expected_result

    def test_choices_generation(self):
        """Test generation with inline choices (Literal type)."""
        structure_blueprint = {
            "name": ConceptStructureBlueprint(definition="Product name", type=ConceptStructureBlueprintFieldType.TEXT, required=False),
            "category": ConceptStructureBlueprint(definition="Product category", choices=["electronics", "clothing", "food", "books"], required=True),
            "size": ConceptStructureBlueprint(definition="Size of the product", choices=["XS", "S", "M", "L", "XL"], required=False),
        }

        result = StructureGenerator().generate_from_structure_blueprint("Product", structure_blueprint)

        pretty_print(structure_blueprint, title="Source Blueprint")
        pretty_print(result, title="Generated Result")

        # Check the complete generated structure with Literal types
        expected_result = (
            "from enum import Enum\n"
            "from pipelex.core.stuffs.stuff_content import StructuredContent\n"
            "from pydantic import Field\n"
            "from typing import Optional, List, Dict, Any, Literal\n"
            "\n\n"
            "class Product(StructuredContent):\n"
            '    """Generated Product class"""\n'
            "\n"
            '    name: Optional[str] = Field(default=None, description="Product name")\n'
            "    category: Literal['electronics', 'clothing', 'food', 'books'] = Field(..., description=\"Product category\")\n"
            "    size: Optional[Literal['XS', 'S', 'M', 'L', 'XL']] = Field(default=None, description=\"Size of the product\")\n"
        )
        assert result == expected_result

    def test_empty_structure(self):
        """Test generation of structure with no fields."""
        structure_blueprint: Dict[str, ConceptStructureBlueprint] = {}

        result = StructureGenerator().generate_from_structure_blueprint("EmptyModel", structure_blueprint)

        pretty_print(structure_blueprint, title="Source Blueprint")
        pretty_print(result, title="Generated Result")

        # Check the complete generated structure for empty model
        expected_result = (
            "from enum import Enum\n"
            "from pipelex.core.stuffs.stuff_content import StructuredContent\n"
            "from pydantic import Field\n"
            "from typing import Optional, List, Dict, Any, Literal\n"
            "\n\n"
            "class EmptyModel(StructuredContent):\n"
            '    """Generated EmptyModel class"""\n'
            "\n"
            "    pass\n"
        )
        assert result == expected_result

    def test_concept_get_structure_method(self):
        """Test the get_structure method on Concept class."""
        structure_blueprint = {
            "title": ConceptStructureBlueprint(definition="Document title", type=ConceptStructureBlueprintFieldType.TEXT, required=True),
            "page_count": ConceptStructureBlueprint(definition="Number of pages", type=ConceptStructureBlueprintFieldType.INTEGER, required=False),
        }

        result = StructureGenerator().generate_from_structure_blueprint("DocumentInfo", structure_blueprint)

        pretty_print(structure_blueprint, title="Source Blueprint")
        pretty_print(result, title="Generated Result")

        # Check the complete generated structure
        expected_result = (
            "from enum import Enum\n"
            "from pipelex.core.stuffs.stuff_content import StructuredContent\n"
            "from pydantic import Field\n"
            "from typing import Optional, List, Dict, Any, Literal\n"
            "\n\n"
            "class DocumentInfo(StructuredContent):\n"
            '    """Generated DocumentInfo class"""\n'
            "\n"
            '    title: str = Field(..., description="Document title")\n'
            '    page_count: Optional[int] = Field(default=None, description="Number of pages")\n'
        )
        assert result == expected_result

    def test_generate_from_blueprint_dict_function(self):
        """Test the convenience function for generating from blueprint dict."""
        structure_blueprint = {
            "value": ConceptStructureBlueprint(definition="Test value", type=ConceptStructureBlueprintFieldType.TEXT, required=True)
        }

        result = StructureGenerator().generate_from_structure_blueprint("ConvenienceTest", structure_blueprint)

        pretty_print(structure_blueprint, title="Source Blueprint")
        pretty_print(result, title="Generated Result")

        # Check the complete generated structure
        expected_result = (
            "from enum import Enum\n"
            "from pipelex.core.stuffs.stuff_content import StructuredContent\n"
            "from pydantic import Field\n"
            "from typing import Optional, List, Dict, Any, Literal\n"
            "\n\n"
            "class ConvenienceTest(StructuredContent):\n"
            '    """Generated ConvenienceTest class"""\n'
            "\n"
            '    value: str = Field(..., description="Test value")\n'
        )
        assert result == expected_result

    def test_all_field_types(self):
        """Test that all field types are properly handled."""
        structure_blueprint = {
            "text_field": ConceptStructureBlueprint(definition="Text field", type=ConceptStructureBlueprintFieldType.TEXT, required=False),
            "number_field": ConceptStructureBlueprint(definition="Number field", type=ConceptStructureBlueprintFieldType.NUMBER, required=False),
            "integer_field": ConceptStructureBlueprint(definition="Integer field", type=ConceptStructureBlueprintFieldType.INTEGER, required=False),
            "boolean_field": ConceptStructureBlueprint(definition="Boolean field", type=ConceptStructureBlueprintFieldType.BOOLEAN, required=False),
            "list_field": ConceptStructureBlueprint(
                definition="List field", type=ConceptStructureBlueprintFieldType.LIST, item_type="text", required=False
            ),
            "dict_field": ConceptStructureBlueprint(
                definition="Dict field", type=ConceptStructureBlueprintFieldType.DICT, key_type="text", value_type="integer", required=False
            ),
        }

        result = StructureGenerator().generate_from_structure_blueprint("TypeMappingTest", structure_blueprint)

        pretty_print(structure_blueprint, title="Source Blueprint")
        pretty_print(result, title="Generated Result")

        # Check the complete generated structure with all field types
        expected_result = (
            "from enum import Enum\n"
            "from pipelex.core.stuffs.stuff_content import StructuredContent\n"
            "from pydantic import Field\n"
            "from typing import Optional, List, Dict, Any, Literal\n"
            "\n\n"
            "class TypeMappingTest(StructuredContent):\n"
            '    """Generated TypeMappingTest class"""\n'
            "\n"
            '    text_field: Optional[str] = Field(default=None, description="Text field")\n'
            '    number_field: Optional[float] = Field(default=None, description="Number field")\n'
            '    integer_field: Optional[int] = Field(default=None, description="Integer field")\n'
            '    boolean_field: Optional[bool] = Field(default=None, description="Boolean field")\n'
            '    list_field: Optional[List[str]] = Field(default=None, description="List field")\n'
            '    dict_field: Optional[Dict[str, int]] = Field(default=None, description="Dict field")\n'
        )
        assert result == expected_result

    def test_required_vs_optional_fields(self):
        """Test that fields can be marked as required vs optional."""
        structure_blueprint = {
            "title": ConceptStructureBlueprint(definition="Required title", type=ConceptStructureBlueprintFieldType.TEXT, required=True),
            "optional_field": ConceptStructureBlueprint(definition="Optional field", type=ConceptStructureBlueprintFieldType.TEXT, required=False),
        }

        result = StructureGenerator().generate_from_structure_blueprint("RequiredFieldsModel", structure_blueprint)

        pretty_print(structure_blueprint, title="Source Blueprint")
        pretty_print(result, title="Generated Result")

        # Check the complete generated structure with required vs optional fields
        expected_result = (
            "from enum import Enum\n"
            "from pipelex.core.stuffs.stuff_content import StructuredContent\n"
            "from pydantic import Field\n"
            "from typing import Optional, List, Dict, Any, Literal\n"
            "\n\n"
            "class RequiredFieldsModel(StructuredContent):\n"
            '    """Generated RequiredFieldsModel class"""\n'
            "\n"
            '    title: str = Field(..., description="Required title")\n'
            '    optional_field: Optional[str] = Field(default=None, description="Optional field")\n'
        )
        assert result == expected_result

    def test_default_values(self):
        """Test fields with default values."""
        structure_blueprint = {
            "name": ConceptStructureBlueprint(
                definition="Person name", type=ConceptStructureBlueprintFieldType.TEXT, required=False, default_value="Anonymous"
            ),
            "age": ConceptStructureBlueprint(
                definition="Person age", type=ConceptStructureBlueprintFieldType.INTEGER, required=False, default_value=0
            ),
            "active": ConceptStructureBlueprint(
                definition="Is active", type=ConceptStructureBlueprintFieldType.BOOLEAN, required=False, default_value=True
            ),
        }

        result = StructureGenerator().generate_from_structure_blueprint("PersonWithDefaults", structure_blueprint)

        pretty_print(structure_blueprint, title="Source Blueprint")
        pretty_print(result, title="Generated Result")

        # Check the complete generated structure with default values
        expected_result = (
            "from enum import Enum\n"
            "from pipelex.core.stuffs.stuff_content import StructuredContent\n"
            "from pydantic import Field\n"
            "from typing import Optional, List, Dict, Any, Literal\n"
            "\n\n"
            "class PersonWithDefaults(StructuredContent):\n"
            '    """Generated PersonWithDefaults class"""\n'
            "\n"
            '    name: Optional[str] = Field(default="Anonymous", description="Person name")\n'
            '    age: Optional[int] = Field(default=0, description="Person age")\n'
            '    active: Optional[bool] = Field(default=True, description="Is active")\n'
        )
        assert result == expected_result

    def test_nested_list_types(self):
        """Test nested list types with different item types."""
        structure_blueprint = {
            "text_list": ConceptStructureBlueprint(
                definition="List of text items", type=ConceptStructureBlueprintFieldType.LIST, item_type="text", required=False
            ),
            "number_list": ConceptStructureBlueprint(
                definition="List of numbers", type=ConceptStructureBlueprintFieldType.LIST, item_type="number", required=True
            ),
            "integer_list": ConceptStructureBlueprint(
                definition="List of integers", type=ConceptStructureBlueprintFieldType.LIST, item_type="integer", required=False
            ),
        }

        result = StructureGenerator().generate_from_structure_blueprint("ListTypesModel", structure_blueprint)

        pretty_print(structure_blueprint, title="Source Blueprint")
        pretty_print(result, title="Generated Result")

        # Check the complete generated structure with nested list types
        expected_result = (
            "from enum import Enum\n"
            "from pipelex.core.stuffs.stuff_content import StructuredContent\n"
            "from pydantic import Field\n"
            "from typing import Optional, List, Dict, Any, Literal\n"
            "\n\n"
            "class ListTypesModel(StructuredContent):\n"
            '    """Generated ListTypesModel class"""\n'
            "\n"
            '    text_list: Optional[List[str]] = Field(default=None, description="List of text items")\n'
            '    number_list: List[float] = Field(..., description="List of numbers")\n'
            '    integer_list: Optional[List[int]] = Field(default=None, description="List of integers")\n'
        )
        assert result == expected_result

    def test_nested_dict_types(self):
        """Test nested dict types with different key/value combinations."""
        structure_blueprint = {
            "string_to_string": ConceptStructureBlueprint(
                definition="String to string mapping",
                type=ConceptStructureBlueprintFieldType.DICT,
                key_type="text",
                value_type="text",
                required=False,
            ),
            "string_to_number": ConceptStructureBlueprint(
                definition="String to number mapping",
                type=ConceptStructureBlueprintFieldType.DICT,
                key_type="text",
                value_type="number",
                required=True,
            ),
            "string_to_integer": ConceptStructureBlueprint(
                definition="String to integer mapping",
                type=ConceptStructureBlueprintFieldType.DICT,
                key_type="text",
                value_type="integer",
                required=False,
            ),
        }

        result = StructureGenerator().generate_from_structure_blueprint("DictTypesModel", structure_blueprint)

        pretty_print(structure_blueprint, title="Source Blueprint")
        pretty_print(result, title="Generated Result")

        # Check the complete generated structure with nested dict types
        expected_result = (
            "from enum import Enum\n"
            "from pipelex.core.stuffs.stuff_content import StructuredContent\n"
            "from pydantic import Field\n"
            "from typing import Optional, List, Dict, Any, Literal\n"
            "\n\n"
            "class DictTypesModel(StructuredContent):\n"
            '    """Generated DictTypesModel class"""\n'
            "\n"
            '    string_to_string: Optional[Dict[str, str]] = Field(default=None, description="String to string mapping")\n'
            '    string_to_number: Dict[str, float] = Field(..., description="String to number mapping")\n'
            '    string_to_integer: Optional[Dict[str, int]] = Field(default=None, description="String to integer mapping")\n'
        )
        assert result == expected_result

    def test_mixed_complexity_structure(self):
        """Test a structure with mixed complexity - simple and complex types together."""
        structure_blueprint = {
            "id": ConceptStructureBlueprint(definition="Unique identifier", type=ConceptStructureBlueprintFieldType.INTEGER, required=True),
            "name": ConceptStructureBlueprint(definition="Display name", type=ConceptStructureBlueprintFieldType.TEXT, required=True),
            "tags": ConceptStructureBlueprint(
                definition="Associated tags", type=ConceptStructureBlueprintFieldType.LIST, item_type="text", required=False
            ),
            "metadata": ConceptStructureBlueprint(
                definition="Additional metadata", type=ConceptStructureBlueprintFieldType.DICT, key_type="text", value_type="text", required=False
            ),
            "active": ConceptStructureBlueprint(
                definition="Whether item is active", type=ConceptStructureBlueprintFieldType.BOOLEAN, required=False, default_value=True
            ),
            "priority": ConceptStructureBlueprint(
                definition="Priority level", choices=["low", "medium", "high", "urgent"], required=False, default_value="medium"
            ),
        }

        result = StructureGenerator().generate_from_structure_blueprint("ComplexItem", structure_blueprint)

        pretty_print(structure_blueprint, title="Source Blueprint")
        pretty_print(result, title="Generated Result")

        # Check the complete generated structure with mixed complexity
        expected_result = (
            "from enum import Enum\n"
            "from pipelex.core.stuffs.stuff_content import StructuredContent\n"
            "from pydantic import Field\n"
            "from typing import Optional, List, Dict, Any, Literal\n"
            "\n\n"
            "class ComplexItem(StructuredContent):\n"
            '    """Generated ComplexItem class"""\n'
            "\n"
            '    id: int = Field(..., description="Unique identifier")\n'
            '    name: str = Field(..., description="Display name")\n'
            '    tags: Optional[List[str]] = Field(default=None, description="Associated tags")\n'
            '    metadata: Optional[Dict[str, str]] = Field(default=None, description="Additional metadata")\n'
            '    active: Optional[bool] = Field(default=True, description="Whether item is active")\n'
            "    priority: Optional[Literal['low', 'medium', 'high', 'urgent']] = Field(default=\"medium\", description=\"Priority level\")\n"
        )
        assert result == expected_result

    def test_mixed_structure_blueprint_normalization(self):
        """Test that mixed structure blueprints (strings and ConceptStructureBlueprint objects) are properly normalized."""
        # Create a mixed structure blueprint similar to what would come from TOML parsing
        mixed_structure_blueprint: Dict[str, ConceptStructureBlueprintType] = {
            "name": "The name of the person",  # Simple string definition
            "age": ConceptStructureBlueprint(definition="The age of the person", type=ConceptStructureBlueprintFieldType.NUMBER, required=True),
            "birthdate": ConceptStructureBlueprint(
                definition="The birthdate of the person", type=ConceptStructureBlueprintFieldType.DATE, required=True
            ),
        }

        normalized_structure = ConceptFactory.normalize_structure_blueprint(mixed_structure_blueprint)

        result = StructureGenerator().generate_from_structure_blueprint("PersonInfo", normalized_structure)

        pretty_print(mixed_structure_blueprint, title="Source Mixed Blueprint")
        pretty_print(normalized_structure, title="Normalized Blueprint")
        pretty_print(result, title="Generated Result")

        # Check the complete generated structure with mixed field types
        expected_result = (
            "from datetime import datetime\n"
            "from enum import Enum\n"
            "from pipelex.core.stuffs.stuff_content import StructuredContent\n"
            "from pydantic import Field\n"
            "from typing import Optional, List, Dict, Any, Literal\n"
            "\n\n"
            "class PersonInfo(StructuredContent):\n"
            '    """Generated PersonInfo class"""\n'
            "\n"
            '    name: str = Field(..., description="The name of the person")\n'
            '    age: float = Field(..., description="The age of the person")\n'
            '    birthdate: datetime = Field(..., description="The birthdate of the person")\n'
        )
        assert result == expected_result

        # Verify that the string was properly converted to ConceptStructureBlueprint
        assert isinstance(normalized_structure["name"], ConceptStructureBlueprint)
        assert normalized_structure["name"].definition == "The name of the person"
        assert normalized_structure["name"].type == ConceptStructureBlueprintFieldType.TEXT
        assert normalized_structure["name"].required

    def test_code_validation_success(self):
        """Test that valid generated code passes validation."""
        structure_blueprint = {
            "name": ConceptStructureBlueprint(definition="Name field", type=ConceptStructureBlueprintFieldType.TEXT, required=True),
        }

        generator = StructureGenerator()
        result = generator.generate_from_structure_blueprint("ValidTestModel", structure_blueprint)

        # The generation should succeed (validation happens internally)
        assert "class ValidTestModel(StructuredContent):" in result

        # Test validation directly
        assert generator.validate_generated_code(result, "ValidTestModel") is True

    def test_code_validation_syntax_error(self):
        """Test that invalid syntax fails validation."""
        generator = StructureGenerator()
        invalid_code = """
from pydantic import Field
from pipelex.core.stuffs.stuff_content import StructuredContent

class InvalidModel(StructuredContent):
    name: str = Field(..., description="Name field"  # Missing closing parenthesis
"""

        assert generator.validate_generated_code(invalid_code, "InvalidModel") is False

    def test_code_validation_missing_class(self):
        """Test that code without the expected class fails validation."""
        generator = StructureGenerator()
        code_without_expected_class = """
from pydantic import Field
from pipelex.core.stuffs.stuff_content import StructuredContent

class WrongClassName(StructuredContent):
    name: str = Field(..., description="Name field")
"""

        assert generator.validate_generated_code(code_without_expected_class, "ExpectedClassName") is False
