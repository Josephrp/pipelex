from datetime import datetime
from typing import List, Literal, Optional

from pydantic import BaseModel, Field, field_validator
from pytest import FixtureRequest

from pipelex.core.stuffs.stuff_content import ListContent, StructuredContent, TextContent
from pipelex.tools.typing.type_inspector import get_type_structure
from pipelex.types import StrEnum


# Test Enums
class DocumentType(StrEnum):
    INVOICE = "INVOICE"
    RECEIPT = "RECEIPT"


class Priority(StrEnum):
    HIGH = "HIGH"
    LOW = "LOW"


class MusicGenre(StrEnum):
    """Available music genres."""

    CLASSICAL = "classical"
    JAZZ = "jazz"
    ROCK = "rock"
    ELECTRONIC = "electronic"
    WORLD = "world"


# Simple Content Classes
class SimpleTextContent(TextContent):
    """A simple text content class"""

    pass


class MusicCategoryContent(StructuredContent):
    """A content class with a Literal field for music genres."""

    category: Literal[
        MusicGenre.CLASSICAL,
        MusicGenre.JAZZ,
        MusicGenre.ROCK,
        MusicGenre.ELECTRONIC,
        MusicGenre.WORLD,
    ] = Field(description="The genre of music")


class SimpleStructuredContent(StructuredContent):
    """A simple structured content with primitive types"""

    name: str
    age: int
    active: bool


# Enum Content Classes
class DocumentTypeContent(StructuredContent):
    """Content with enum type"""

    document_type: DocumentType


# Nested Content Classes
class AddressContent(StructuredContent):
    """Nested address content"""

    street: str
    city: str
    country: str


class PersonContent(StructuredContent):
    """Complex nested content with various types"""

    name: str
    age: int
    address: AddressContent = Field(description="Address of the person")
    documents: List[DocumentTypeContent]
    priority: Optional[Priority] = None


class ComplexListContent(ListContent[PersonContent]):
    """List content with complex items"""

    items: List[PersonContent]


class GanttTaskDetails(StructuredContent):
    """Do not include timezone in the dates."""

    name: str
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None

    @field_validator("start_date", "end_date")
    @classmethod
    def remove_tzinfo(cls, v: Optional[datetime]) -> Optional[datetime]:
        if v is not None:
            return v.replace(tzinfo=None)
        return v


class Milestone(StructuredContent):
    name: str
    date: Optional[datetime]

    @field_validator("date")
    @classmethod
    def remove_tzinfo(cls, v: Optional[datetime]) -> Optional[datetime]:
        if v is not None:
            return v.replace(tzinfo=None)
        return v


class GanttChart(StructuredContent):
    tasks: Optional[List[GanttTaskDetails]] = None
    milestones: Optional[List[Milestone]] = None


class TestTypeInspector:
    """Tests for the type inspector functionality"""

    def test_simple_text_content(self, request: FixtureRequest):
        """Test structure of simple text content"""
        result = get_type_structure(SimpleTextContent)
        expected = [
            "class SimpleTextContent(TextContent):",
            '    """A simple text content class"""',
            "    # Inherits from TextContent",
            "    # No additional fields",
        ]
        assert result == expected, f"Expected:\n{''.join(expected)}\n\nGot:\n{''.join(result)}"

    def test_simple_structured_content(self, request: FixtureRequest):
        """Test structure of simple structured content"""
        result = get_type_structure(SimpleStructuredContent)
        expected = [
            "class SimpleStructuredContent(StructuredContent):",
            '    """A simple structured content with primitive types"""',
            "    name: str",
            "    age: int",
            "    active: bool",
        ]
        assert result == expected, f"Expected:\n{''.join(expected)}\n\nGot:\n{''.join(result)}"

    def test_enum_content(self, request: FixtureRequest):
        """Test structure of content with enum"""
        result = get_type_structure(DocumentTypeContent)
        expected = [
            "class DocumentTypeContent(StructuredContent):",
            '    """Content with enum type"""',
            "    document_type: DocumentType",
            "",
            "class DocumentType(StrEnum):",
            '    INVOICE = "INVOICE"',
            '    RECEIPT = "RECEIPT"',
        ]
        assert result == expected, f"Expected:\n{''.join(expected)}\n\nGot:\n{''.join(result)}"

    def test_nested_content(self, request: FixtureRequest):
        """Test structure of nested content"""
        result = get_type_structure(PersonContent)
        expected = [
            "class PersonContent(StructuredContent):",
            '    """Complex nested content with various types"""',
            "    name: str",
            "    age: int",
            "    address: AddressContent  # Address of the person",
            "    documents: List[DocumentTypeContent]",
            "    priority: Optional[Priority] = None",
            "",
            "class AddressContent(StructuredContent):",
            '    """Nested address content"""',
            "    street: str",
            "    city: str",
            "    country: str",
            "",
            "class DocumentTypeContent(StructuredContent):",
            '    """Content with enum type"""',
            "    document_type: DocumentType",
            "",
            "class DocumentType(StrEnum):",
            '    INVOICE = "INVOICE"',
            '    RECEIPT = "RECEIPT"',
            "",
            "class Priority(StrEnum):",
            '    HIGH = "HIGH"',
            '    LOW = "LOW"',
        ]
        assert result == expected, f"Expected:\n{''.join(expected)}\n\nGot:\n{''.join(result)}"

    def test_list_content(self, request: FixtureRequest):
        """Test structure of list content"""
        result = get_type_structure(ComplexListContent)
        expected = [
            "class ComplexListContent(ListContent[PersonContent]):",
            '    """List content with complex items"""',
            "    items: List[PersonContent]",
            "",
            "class PersonContent(StructuredContent):",
            '    """Complex nested content with various types"""',
            "    name: str",
            "    age: int",
            "    address: AddressContent  # Address of the person",
            "    documents: List[DocumentTypeContent]",
            "    priority: Optional[Priority] = None",
            "",
            "class AddressContent(StructuredContent):",
            '    """Nested address content"""',
            "    street: str",
            "    city: str",
            "    country: str",
            "",
            "class DocumentTypeContent(StructuredContent):",
            '    """Content with enum type"""',
            "    document_type: DocumentType",
            "",
            "class DocumentType(StrEnum):",
            '    INVOICE = "INVOICE"',
            '    RECEIPT = "RECEIPT"',
            "",
            "class Priority(StrEnum):",
            '    HIGH = "HIGH"',
            '    LOW = "LOW"',
        ]
        assert result == expected, f"Expected:\n{''.join(expected)}\n\nGot:\n{''.join(result)}"

    def test_model_with_field_description(self, request: FixtureRequest):
        """Test structure of a model with field descriptions"""

        class Person(BaseModel):
            name: str
            age: int

        class Employee(Person):
            job: str = Field(description="Job title, must be lowercase")

        result = get_type_structure(Employee)
        expected = [
            "class Employee(Person):",
            "    job: str  # Job title, must be lowercase",
            "",
            "class Person(BaseModel):",
            "    name: str",
            "    age: int",
        ]
        assert result == expected, f"Expected:\n{''.join(expected)}\n\nGot:\n{''.join(result)}"

    def test_model_with_docstring_and_field_description(self, request: FixtureRequest):
        """Test structure of a model with both docstring and field descriptions"""

        class TaskContent(StructuredContent):
            """A task content model that represents a single task.

            This model is used to store task information including its title,
            description, and status.
            """

            title: str = Field(description="The title of the task")
            description: str = Field(description="Detailed description of what needs to be done")
            is_completed: bool = Field(False, description="Whether the task is completed")

        result = get_type_structure(TaskContent)
        expected = [
            "class TaskContent(StructuredContent):",
            '    """A task content model that represents a single task.',
            "",
            "    This model is used to store task information including its title,",
            "    description, and status.",
            '    """',
            "    title: str  # The title of the task",
            "    description: str  # Detailed description of what needs to be done",
            "    is_completed: bool = False  # Whether the task is completed",
        ]
        assert result == expected, f"Expected:\n{''.join(expected)}\n\nGot:\n{''.join(result)}"

    def test_literal_field_content(self, request: FixtureRequest):
        """Test structure of content with Literal field"""
        result = get_type_structure(MusicCategoryContent)
        expected = [
            "class MusicCategoryContent(StructuredContent):",
            '    """A content class with a Literal field for music genres."""',
            "    category: Literal[",
            '        "classical",',
            '        "jazz",',
            '        "rock",',
            '        "electronic",',
            '        "world",',
            "    ]  # The genre of music",
            "",
            "class MusicGenre(StrEnum):",
            '    """Available music genres."""',
            '    CLASSICAL = "classical"',
            '    JAZZ = "jazz"',
            '    ROCK = "rock"',
            '    ELECTRONIC = "electronic"',
            '    WORLD = "world"',
        ]
        assert result == expected, f"Expected:\n{''.join(expected)}\n\nGot:\n{''.join(result)}"

    def test_gantt_chart_content(self, request: FixtureRequest):
        """Test structure of Gantt chart content with datetime validators"""

        result = get_type_structure(GanttChart, base_class=StructuredContent)
        expected = [
            "class GanttChart(StructuredContent):",
            "    tasks: Optional[List[GanttTaskDetails]] = None",
            "    milestones: Optional[List[Milestone]] = None",
            "",
            "class GanttTaskDetails(StructuredContent):",
            '    """Do not include timezone in the dates."""',
            "    name: str",
            "    start_date: Optional[datetime] = None",
            "    end_date: Optional[datetime] = None",
            "",
            "class Milestone(StructuredContent):",
            "    name: str",
            "    date: Optional[datetime] = None",
        ]
        assert result == expected, f"Expected:\n{''.join(expected)}\n\nGot:\n{''.join(result)}"
