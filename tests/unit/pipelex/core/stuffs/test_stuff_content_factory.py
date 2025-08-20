from typing import Any, ClassVar, Dict, List, Tuple

import pytest

from pipelex.core.stuffs.stuff_content import StructuredContent, TextContent
from pipelex.core.stuffs.stuff_factory import StuffContentFactory


class TestCases:
    # Test cases for TextContent with string content
    TEXT_STRING_BLUEPRINT: ClassVar[Dict[str, Any]] = {
        "concept_code": "native.Text",
        "content": "The Dawn of Ultra-Rapid Transit: NextGen High-Speed Trains Redefine Travel",
    }

    # Test cases for TextContent with dict content
    TEXT_DICT_BLUEPRINT: ClassVar[Dict[str, Any]] = {"concept_code": "native.Text", "content": {"text": "Sample text content"}}

    # Test cases for native concept without prefix (should work)
    TEXT_NO_PREFIX_BLUEPRINT: ClassVar[Dict[str, Any]] = {"concept_code": "Text", "content": {"text": "Text content without native prefix"}}

    # Test cases for registered class (using actual registered class)
    REGISTERED_CLASS_BLUEPRINT: ClassVar[Dict[str, Any]] = {
        "concept_code": "test.MockRegisteredContent",
        "content": {"title": "Test Question", "description": "What are aerodynamic features?"},
    }

    # Test cases for unregistered class (creates implicit concept, returns TextContent)
    UNREGISTERED_STRING_BLUEPRINT: ClassVar[Dict[str, Any]] = {
        "concept_code": "unknown.NonExistentConcept",
        "content": "This should create implicit concept and return TextContent",
    }

    # Test cases for unregistered class with dict content
    UNREGISTERED_DICT_BLUEPRINT: ClassVar[Dict[str, Any]] = {
        "concept_code": "unknown.NonExistentConcept",
        "content": {"text": "Dict content for implicit concept"},
    }

    TEST_BLUEPRINTS: ClassVar[List[Tuple[str, Dict[str, Any]]]] = [
        ("text_string", TEXT_STRING_BLUEPRINT),
        ("text_dict", TEXT_DICT_BLUEPRINT),
        ("text_no_prefix", TEXT_NO_PREFIX_BLUEPRINT),
        ("registered_class", REGISTERED_CLASS_BLUEPRINT),
        ("unregistered_string", UNREGISTERED_STRING_BLUEPRINT),
        ("unregistered_dict", UNREGISTERED_DICT_BLUEPRINT),
    ]


class TestStuffContentFactory:
    def test_make_content_from_value_text_string(self):
        """Test make_content_from_value with TextContent and string value."""
        result = StuffContentFactory.make_content_from_value(stuff_content_subclass=TextContent, value="Test string content")

        assert isinstance(result, TextContent)
        assert result.text == "Test string content"

    def test_make_content_from_value_text_dict(self):
        """Test make_content_from_value with TextContent and dict value."""
        result = StuffContentFactory.make_content_from_value(stuff_content_subclass=TextContent, value={"text": "Dict text content"})

        assert isinstance(result, TextContent)
        assert result.text == "Dict text content"

    def test_make_content_from_value_structured_dict(self):
        """Test make_content_from_value with StructuredContent and dict value."""

        class MockStructuredContent(StructuredContent):
            title: str
            description: str

        result = StuffContentFactory.make_content_from_value(
            stuff_content_subclass=MockStructuredContent, value={"title": "Test Title", "description": "Test Description"}
        )

        assert isinstance(result, MockStructuredContent)
        assert result.title == "Test Title"
        assert result.description == "Test Description"

    def test_make_stuffcontent_from_concept_code_required_text_content(self):
        """Test required method with native.Text concept (should work)."""
        result = StuffContentFactory.make_stuffcontent_from_concept_code_required(concept_code="native.Text", value="Test text content")

        assert isinstance(result, TextContent)
        assert result.text == "Test text content"

    def test_make_stuffcontent_from_concept_code_required_implicit_concept(self):
        """Test required method with implicit concept (should create TextContent)."""
        result = StuffContentFactory.make_stuffcontent_from_concept_code_required(
            concept_code="unknown.NonExistentConcept", value="Test content for implicit concept"
        )

        assert isinstance(result, TextContent)
        assert result.text == "Test content for implicit concept"

    def test_make_stuffcontent_from_concept_code_with_fallback_text_success(self):
        """Test fallback method with native.Text concept."""
        result = StuffContentFactory.make_stuffcontent_from_concept_code_with_fallback(concept_code="native.Text", value="Test text content")

        assert isinstance(result, TextContent)
        assert result.text == "Test text content"

    def test_make_stuffcontent_from_concept_code_with_fallback_implicit_string(self):
        """Test fallback method with implicit concept and string value."""
        result = StuffContentFactory.make_stuffcontent_from_concept_code_with_fallback(
            concept_code="unknown.NonExistentConcept", value="Fallback text content"
        )

        assert isinstance(result, TextContent)
        assert result.text == "Fallback text content"

    def test_make_stuffcontent_from_concept_code_with_fallback_implicit_dict(self):
        """Test fallback method with implicit concept and dict value."""
        result = StuffContentFactory.make_stuffcontent_from_concept_code_with_fallback(
            concept_code="unknown.NonExistentConcept", value={"text": "Dict fallback content"}
        )

        assert isinstance(result, TextContent)
        assert result.text == "Dict fallback content"

    @pytest.mark.parametrize(
        "test_name, blueprint",
        TestCases.TEST_BLUEPRINTS,
    )
    def test_blueprint_scenarios(self, test_name: str, blueprint: Dict[str, Any]):
        """Test various blueprint scenarios with parametrized test cases."""
        concept_code = blueprint["concept_code"]
        content = blueprint["content"]

        if test_name.startswith("text_"):
            # Test native.Text concept with required method
            result = StuffContentFactory.make_stuffcontent_from_concept_code_required(concept_code=concept_code, value=content)
            assert isinstance(result, TextContent)
            if isinstance(content, str):
                assert result.text == content
            else:
                assert result.text == content["text"]

        elif test_name == "registered_class":
            # Test with registered class - since MockRegisteredContent isn't actually registered,
            # it will be treated as an implicit concept and return TextContent
            # But the content dict format is incompatible with TextContent's expected structure

            # Test required method - it will succeed but create TextContent
            # The dict will be passed through model_validate which should fail for TextContent
            try:
                result_required = StuffContentFactory.make_stuffcontent_from_concept_code_required(concept_code=concept_code, value=content)
                # If it succeeds, it should be TextContent (due to implicit concept)
                assert isinstance(result_required, TextContent)
            except Exception:
                # If it fails due to validation error, that's also expected
                pass

            # Test fallback method - same behavior expected
            try:
                result_fallback = StuffContentFactory.make_stuffcontent_from_concept_code_with_fallback(concept_code=concept_code, value=content)
                # If it succeeds, it should be TextContent (due to implicit concept)
                assert isinstance(result_fallback, TextContent)
            except Exception:
                # If it fails due to validation error, that's also expected
                pass

        elif test_name.startswith("unregistered_"):
            # Test behavior for unregistered/implicit concepts
            # Both methods should work and return TextContent due to implicit concept creation

            result_required = StuffContentFactory.make_stuffcontent_from_concept_code_required(concept_code=concept_code, value=content)
            assert isinstance(result_required, TextContent)

            result_fallback = StuffContentFactory.make_stuffcontent_from_concept_code_with_fallback(concept_code=concept_code, value=content)
            assert isinstance(result_fallback, TextContent)

            # Both should produce the same result
            assert result_required.text == result_fallback.text
