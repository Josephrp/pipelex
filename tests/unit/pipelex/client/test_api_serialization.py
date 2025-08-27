import json
from datetime import datetime
from decimal import Decimal
from enum import Enum
from typing import Any, Dict, List, Optional

import pytest
from pydantic import BaseModel

from pipelex.client.api_serializer import ApiSerializer
from pipelex.core.concepts.concept_factory import ConceptFactory
from pipelex.core.concepts.concept_native import NATIVE_CONCEPTS_DATA, NativeConceptEnum
from pipelex.core.memory.working_memory import WorkingMemory
from pipelex.core.memory.working_memory_factory import WorkingMemoryFactory
from pipelex.core.stuffs.stuff_content import NumberContent, TextContent
from pipelex.core.stuffs.stuff_factory import StuffFactory
from tests.test_pipelines.datetime import DateTimeEvent


# Test models for complex scenarios
class Priority(Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


class TaskStatus(BaseModel):
    is_complete: bool
    completion_date: Optional[datetime] = None
    notes: List[str] = []


class ComplexTask(BaseModel):
    task_id: str
    title: str
    priority: Priority
    status: TaskStatus
    due_dates: List[datetime]
    metadata: Dict[str, Any]
    score: Optional[Decimal] = None


class Project(BaseModel):
    name: str
    created_at: datetime
    tasks: List[ComplexTask]
    settings: Dict[str, Any]


class TestApiSerialization:
    """Test API-specific serialization with kajson, datetime formatting, and cleanup."""

    @pytest.fixture
    def datetime_content_memory(self) -> WorkingMemory:
        """Create WorkingMemory with datetime content."""
        datetime_event = DateTimeEvent(
            event_name="Project Kickoff Meeting",
            start_time=datetime(2024, 1, 15, 10, 0, 0),
            end_time=datetime(2024, 1, 15, 11, 30, 0),
            created_at=datetime(2024, 1, 1, 9, 0, 0),
        )

        stuff = StuffFactory.make_stuff(
            concept=ConceptFactory.make(
                concept_code="DateTimeEvent", domain="event", definition="event.DateTimeEvent", structure_class_name="DateTimeEvent"
            ),
            name="project_meeting",
            content=datetime_event,
        )
        return WorkingMemoryFactory.make_from_single_stuff(stuff=stuff)

    @pytest.fixture
    def text_content_memory(self) -> WorkingMemory:
        """Create WorkingMemory with text content."""
        stuff = StuffFactory.make_stuff(
            concept=ConceptFactory.make_native_concept(native_concept_data=NATIVE_CONCEPTS_DATA[NativeConceptEnum.TEXT]),
            name="sample_text",
            content=TextContent(text="Sample text content"),
        )
        return WorkingMemoryFactory.make_from_single_stuff(stuff=stuff)

    @pytest.fixture
    def number_content_memory(self) -> WorkingMemory:
        """Create WorkingMemory with number content."""
        number_content = NumberContent(number=3.14159)
        stuff = StuffFactory.make_stuff(
            concept=ConceptFactory.make_native_concept(native_concept_data=NATIVE_CONCEPTS_DATA[NativeConceptEnum.NUMBER]),
            name="pi_value",
            content=number_content,
        )
        return WorkingMemoryFactory.make_from_single_stuff(stuff=stuff)

    def test_serialize_working_memory_with_datetime(self, datetime_content_memory: WorkingMemory):
        """Test that datetime content is properly serialized to ISO format strings."""
        compact_memory = ApiSerializer.serialize_working_memory_for_api(datetime_content_memory)

        # Should have one entry for the datetime content
        assert len(compact_memory) == 1
        assert "project_meeting" in compact_memory

        # Check the dict structure
        datetime_blueprint = compact_memory["project_meeting"]
        assert isinstance(datetime_blueprint, dict)
        assert datetime_blueprint["concept_code"] == "DateTimeEvent"

        # Check content is properly serialized
        content = datetime_blueprint["content"]
        assert isinstance(content, dict)
        assert "event_name" in content
        assert "start_time" in content
        assert "end_time" in content
        assert "created_at" in content

        # Verify the event name
        assert content["event_name"] == "Project Kickoff Meeting"

        # Verify datetime objects are now formatted as ISO strings
        assert content["start_time"] == "2024-01-15T10:00:00"
        assert content["end_time"] == "2024-01-15T11:30:00"
        assert content["created_at"] == "2024-01-01T09:00:00"

        # Ensure no __module__ or __class__ fields are present
        assert "__module__" not in content
        assert "__class__" not in content

    def test_api_serialized_memory_is_json_serializable(self, datetime_content_memory: WorkingMemory):
        """Test that API serialized memory is JSON serializable."""
        compact_memory = ApiSerializer.serialize_working_memory_for_api(datetime_content_memory)

        # This should NOT raise an exception now
        json_string = json.dumps(compact_memory)
        roundtrip = json.loads(json_string)

        # Verify roundtrip works
        assert roundtrip == compact_memory

        # Verify datetime fields are strings
        content = roundtrip["project_meeting"]["content"]
        assert isinstance(content["start_time"], str)
        assert isinstance(content["end_time"], str)
        assert isinstance(content["created_at"], str)

    def test_serialize_text_content(self, text_content_memory: WorkingMemory):
        """Test that text content is handled specially."""
        compact_memory = ApiSerializer.serialize_working_memory_for_api(text_content_memory)

        assert len(compact_memory) == 1
        assert "sample_text" in compact_memory

        text_blueprint = compact_memory["sample_text"]
        assert text_blueprint["concept_code"] == NativeConceptEnum.TEXT.value
        assert isinstance(text_blueprint["content"], str)
        assert text_blueprint["content"] == "Sample text content"

    def test_serialize_number_content(self, number_content_memory: WorkingMemory):
        """Test that number content is properly serialized."""
        compact_memory = ApiSerializer.serialize_working_memory_for_api(number_content_memory)

        assert len(compact_memory) == 1
        assert "pi_value" in compact_memory

        number_blueprint = compact_memory["pi_value"]
        assert number_blueprint["concept_code"] == NativeConceptEnum.NUMBER.value
        assert isinstance(number_blueprint["content"], dict)
        assert number_blueprint["content"]["number"] == 3.14159
