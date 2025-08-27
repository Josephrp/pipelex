"""Test PipelexInterpreter input serialization for the two main cases."""

from typing import Any

import pytest

from pipelex.core.interpreter import PipelexInterpreter
from pipelex.core.pipes.pipe_input_spec_blueprint import InputRequirementBlueprint


class TestPipelexInterpreterInputSpec:
    """Test input serialization for both simple strings and InputRequirementBlueprint objects."""

    def test_inputs_to_toml_string_simple_strings(self):
        """Test converting simple string inputs to TOML format like { text = "Text", topic = "Text" }."""
        # Simple string inputs (like "Text")
        simple_inputs = {"text": "Text", "topic": "Text"}

        result = PipelexInterpreter.inputs_to_toml_string(simple_inputs)

        expected = '{ text = "Text", topic = "Text" }'
        assert result == expected

    def test_inputs_to_toml_string_input_requirement_blueprints(self):
        """Test converting InputRequirementBlueprint inputs to TOML format like { text = { concept = "Text", multiplicity = 1 } }."""
        # InputRequirementBlueprint inputs
        complex_inputs = {
            "text": InputRequirementBlueprint(concept="Text", multiplicity=1),
            "problem": InputRequirementBlueprint(concept="Text"),  # multiplicity=None
            "documents": InputRequirementBlueprint(concept="Text", multiplicity=True),
            "query": InputRequirementBlueprint(concept="Text", multiplicity=False),
        }

        result = PipelexInterpreter.inputs_to_toml_string(complex_inputs)

        expected = (
            '{ text = { concept = "Text", multiplicity = 1 }, problem = { concept = "Text" }, '
            'documents = { concept = "Text", multiplicity = true }, query = { concept = "Text", multiplicity = false } }'
        )
        assert result == expected

    @pytest.mark.parametrize(
        "input_req,expected",
        [
            # Test with just concept (multiplicity=None should not be included)
            (InputRequirementBlueprint(concept="Text"), {"concept": "Text"}),
            # Test with concept and multiplicity=1
            (InputRequirementBlueprint(concept="Text", multiplicity=1), {"concept": "Text", "multiplicity": 1}),
            # Test with concept and multiplicity=True
            (InputRequirementBlueprint(concept="Text", multiplicity=True), {"concept": "Text", "multiplicity": True}),
            # Test with concept and multiplicity=False
            (InputRequirementBlueprint(concept="Text", multiplicity=False), {"concept": "Text", "multiplicity": False}),
            # Test with different concept
            (InputRequirementBlueprint(concept="Image", multiplicity=5), {"concept": "Image", "multiplicity": 5}),
        ],
    )
    def test_serialize_input_requirement(self, input_req: InputRequirementBlueprint, expected: dict[str, Any]):
        """Test serializing a single InputRequirementBlueprint with various multiplicity values."""
        result = PipelexInterpreter.serialize_input_requirement(input_req)
        assert result == expected
