"""Tests for structured output generator."""

import pytest

from pipelex import pretty_print
from pipelex.create.structured_output_generator import (
    FieldType,
    StructuredOutputGenerator,
    generate_structured_outputs_from_toml_string,
)


class TestStructuredOutputGenerator:
    def test_simple_schema_generation(self):
        """Test generation of a simple schema with basic fields."""
        toml_content = """
[schema.TestModel]
definition = "A test model"

[schema.TestModel.fields]
name = { type = "text", definition = "Name field", required = true }
age = { type = "integer", definition = "Age field" }
active = { type = "boolean", definition = "Active status", default = true }
"""

        generator = StructuredOutputGenerator()
        result = generator.generate_from_toml(toml_content)

        pretty_print(toml_content, title="Source TOML")
        pretty_print(result, title="Generated Result")

        # Check that basic structure is correct
        assert "from typing import Optional" in result
        assert "from pipelex.core.stuff_content import StructuredContent" in result
        assert "from pydantic import Field" in result
        assert "class TestModel(StructuredContent):" in result
        assert '"""A test model"""' in result
        assert 'name: str = Field(..., description="Name field")' in result
        assert 'age: Optional[int] = Field(default=None, description="Age field")' in result
        assert 'active: Optional[bool] = Field(default=True, description="Active status")' in result

    def test_simplified_field_syntax(self):
        """Test the simplified field syntax where a field is just a string definition."""
        toml_content = """
[schema.SimpleModel]
definition = "A model with simplified field syntax"

[schema.SimpleModel.fields]
dominant_feature = "The most important or dominant feature in the image"
simple_text = "Just some text"
"""

        generator = StructuredOutputGenerator()
        result = generator.generate_from_toml(toml_content)

        pretty_print(toml_content, title="Source TOML")
        pretty_print(result, title="Generated Result")

        assert 'dominant_feature: Optional[str] = Field(default=None, description="The most important or dominant feature in the image")' in result
        assert 'simple_text: Optional[str] = Field(default=None, description="Just some text")' in result

    def test_complex_types_generation(self):
        """Test generation with complex types like lists and dicts."""
        toml_content = """
[schema.ComplexModel]
definition = "A model with complex types"

[schema.ComplexModel.fields]
tags = { type = "list", item_type = "text", definition = "List of tags" }
metadata = { type = "dict", key_type = "text", value_type = "text", definition = "Metadata dictionary" }
scores = { type = "list", item_type = "number", definition = "List of scores", required = true }
"""

        generator = StructuredOutputGenerator()
        result = generator.generate_from_toml(toml_content)

        pretty_print(toml_content, title="Source TOML")
        pretty_print(result, title="Generated Result")

        assert 'tags: Optional[List[str]] = Field(default=None, description="List of tags")' in result
        assert 'metadata: Optional[Dict[str, str]] = Field(default=None, description="Metadata dictionary")' in result
        assert 'scores: List[float] = Field(..., description="List of scores")' in result

    def test_multiple_schemas(self):
        """Test generation of multiple schemas in one TOML."""
        toml_content = """
[schema.FirstModel]
definition = "First model"

[schema.FirstModel.fields]
title = { type = "text", definition = "Title", required = true }

[schema.SecondModel]  
definition = "Second model"

[schema.SecondModel.fields]
content = { type = "text", definition = "Content" }
"""

        generator = StructuredOutputGenerator()
        result = generator.generate_from_toml(toml_content)

        pretty_print(toml_content, title="Source TOML")
        pretty_print(result, title="Generated Result")

        assert "class FirstModel(StructuredContent):" in result
        assert "class SecondModel(StructuredContent):" in result
        assert '"""First model"""' in result
        assert '"""Second model"""' in result

    def test_empty_schema(self):
        """Test generation of schema with no fields."""
        toml_content = """
[schema.EmptyModel]
definition = "An empty model"
"""

        generator = StructuredOutputGenerator()
        result = generator.generate_from_toml(toml_content)

        pretty_print(toml_content, title="Source TOML")
        pretty_print(result, title="Generated Result")

        assert "class EmptyModel(StructuredContent):" in result
        assert '"""An empty model"""' in result
        assert "pass" in result

    def test_required_field_syntax(self):
        """Test that fields can be marked as required."""
        toml_content = """
[schema.RequiredFieldsModel]
definition = "Model with required fields"

[schema.RequiredFieldsModel.fields]
title = { type = "text", definition = "Required title", required = true }
optional_field = { type = "text", definition = "Optional field" }
"""

        generator = StructuredOutputGenerator()
        result = generator.generate_from_toml(toml_content)

        pretty_print(toml_content, title="Source TOML")
        pretty_print(result, title="Generated Result")

        assert 'title: str = Field(..., description="Required title")' in result
        assert 'optional_field: Optional[str] = Field(default=None, description="Optional field")' in result

    def test_custom_types(self):
        """Test handling of custom/unknown types."""
        toml_content = """
[schema.CustomTypeModel]
definition = "Model with custom types"

[schema.CustomTypeModel.fields]
custom_field = { type = "CustomClass", definition = "Custom class field" }
"""

        generator = StructuredOutputGenerator()
        result = generator.generate_from_toml(toml_content)

        pretty_print(toml_content, title="Source TOML")
        pretty_print(result, title="Generated Result")

        assert 'custom_field: Optional[CustomClass] = Field(default=None, description="Custom class field")' in result

    def test_missing_schema_section_raises_error(self):
        """Test that missing schema section raises appropriate error."""
        toml_content = """
[other_section]
value = "test"
"""

        generator = StructuredOutputGenerator()

        pretty_print(toml_content, title="Source TOML (should raise error)")

        with pytest.raises(ValueError, match="TOML must contain a 'schema' section"):
            generator.generate_from_toml(toml_content)

    def test_generate_from_string_convenience_function(self):
        """Test the convenience function for generating from string."""
        toml_content = """
[schema.ConvenienceTest]
definition = "Test convenience function"

[schema.ConvenienceTest.fields]
value = { type = "text", definition = "Test value", required = true }
"""

        result = generate_structured_outputs_from_toml_string(toml_content)

        pretty_print(toml_content, title="Source TOML")
        pretty_print(result, title="Generated Result")

        assert "class ConvenienceTest(StructuredContent):" in result
        assert 'value: str = Field(..., description="Test value")' in result

    def test_field_type_enum_usage(self):
        """Test that FieldType enum values are properly handled."""
        toml_content = """
[schema.TypeMappingTest]
definition = "Test all type mappings"

[schema.TypeMappingTest.fields]
text_field = { type = "text", definition = "Text field" }
number_field = { type = "number", definition = "Number field" }
integer_field = { type = "integer", definition = "Integer field" }
boolean_field = { type = "boolean", definition = "Boolean field" }
list_field = { type = "list", item_type = "text", definition = "List field" }
dict_field = { type = "dict", key_type = "text", value_type = "integer", definition = "Dict field" }
"""

        generator = StructuredOutputGenerator()
        result = generator.generate_from_toml(toml_content)

        pretty_print(toml_content, title="Source TOML")
        pretty_print(result, title="Generated Result")

        assert "text_field: Optional[str]" in result
        assert "number_field: Optional[float]" in result
        assert "integer_field: Optional[int]" in result
        assert "boolean_field: Optional[bool]" in result
        assert "list_field: Optional[List[str]]" in result
        assert "dict_field: Optional[Dict[str, int]]" in result

    def test_mixed_field_syntax(self):
        """Test mixing simplified syntax with full field definitions."""
        toml_content = """
[schema.MixedSyntaxModel]
definition = "Model with mixed field syntax"

[schema.MixedSyntaxModel.fields]
# Simplified syntax
simple_description = "A simple text description"
# Full syntax
complex_field = { type = "integer", definition = "A complex field", required = true }
another_simple = "Another simple field"
"""

        generator = StructuredOutputGenerator()
        result = generator.generate_from_toml(toml_content)

        pretty_print(toml_content, title="Source TOML")
        pretty_print(result, title="Generated Result")

        assert 'simple_description: Optional[str] = Field(default=None, description="A simple text description")' in result
        assert 'complex_field: int = Field(..., description="A complex field")' in result
        assert 'another_simple: Optional[str] = Field(default=None, description="Another simple field")' in result
