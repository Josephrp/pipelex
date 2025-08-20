from typing import ClassVar, List, Tuple

import pytest

from pipelex.core.concepts.concept_native import NativeConcept
from pipelex.core.memory.working_memory import WorkingMemory
from pipelex.core.memory.working_memory_factory import WorkingMemoryFactory
from pipelex.core.stuffs.stuff_content import HtmlContent, ImageContent, ListContent, NumberContent, TextAndImagesContent, TextContent
from pipelex.core.stuffs.stuff_factory import StuffFactory


class TestWorkingMemoryData:
    """Test data for WorkingMemory tests."""

    # Sample text content
    SAMPLE_TEXT = """
    The Dawn of Ultra-Rapid Transit: NextGen High-Speed Trains Redefine Travel
    By Eliza Montgomery, Transportation Technology Reporter

    In an era where time is increasingly precious, a revolution in rail transportation is quietly 
    transforming how we connect cities and regions. The emergence of ultra-high-speed train 
    networks, capable of speeds exceeding 350 mph, promises to render certain short-haul 
    flights obsolete while dramatically reducing carbon emissions.
    """

    # Sample PDF and image URLs
    SAMPLE_PDF_URL = "assets/extract_dpe/dpe_single_page.pdf"
    SAMPLE_IMAGE_URL = "assets/gantt_charts/sample_gantt.png"

    # Test cases for different content types
    SINGLE_TEXT_CASE = "single_text"
    SINGLE_IMAGE_CASE = "single_image"
    SINGLE_PDF_CASE = "single_pdf"
    MULTIPLE_STUFF_CASE = "multiple_stuff"
    WITH_ALIASES_CASE = "with_aliases"
    COMPLEX_LIST_CASE = "complex_list"
    TEXT_AND_IMAGES_CASE = "text_and_images"
    HTML_CONTENT_CASE = "html_content"
    NUMBER_CONTENT_CASE = "number_content"

    TEST_CASES: ClassVar[List[Tuple[str, str]]] = [
        ("Single text content", SINGLE_TEXT_CASE),
        ("Single image content", SINGLE_IMAGE_CASE),
        ("Single PDF content", SINGLE_PDF_CASE),
        ("Multiple stuff items", MULTIPLE_STUFF_CASE),
        ("WorkingMemory with aliases", WITH_ALIASES_CASE),
        ("Complex list content", COMPLEX_LIST_CASE),
        ("Text and images content", TEXT_AND_IMAGES_CASE),
        ("HTML content", HTML_CONTENT_CASE),
        ("Number content", NUMBER_CONTENT_CASE),
    ]


class TestWorkingMemory:
    """Unit tests for WorkingMemory class - focus on core functionality."""

    @pytest.fixture
    def single_text_memory(self) -> WorkingMemory:
        """Create WorkingMemory with single text content."""
        return WorkingMemoryFactory.make_from_text(text=TestWorkingMemoryData.SAMPLE_TEXT, concept_str=NativeConcept.TEXT.code, name="sample_text")

    @pytest.fixture
    def single_image_memory(self) -> WorkingMemory:
        """Create WorkingMemory with single image content."""
        return WorkingMemoryFactory.make_from_image(
            image_url=TestWorkingMemoryData.SAMPLE_IMAGE_URL, concept_str="gantt.GanttImage", name="gantt_chart_image"
        )

    @pytest.fixture
    def single_pdf_memory(self) -> WorkingMemory:
        """Create WorkingMemory with single PDF content."""
        return WorkingMemoryFactory.make_from_pdf(pdf_url=TestWorkingMemoryData.SAMPLE_PDF_URL, concept_str="PDF", name="pdf_document")

    @pytest.fixture
    def multiple_stuff_memory(self) -> WorkingMemory:
        """Create WorkingMemory with multiple stuff items."""
        text_stuff = StuffFactory.make_stuff(
            concept_str="native.Text", name="question", content=TextContent(text="What are the aerodynamic features?")
        )

        document_stuff = StuffFactory.make_stuff(
            concept_str="native.Text", name="document", content=TextContent(text=TestWorkingMemoryData.SAMPLE_TEXT)
        )

        image_stuff = StuffFactory.make_stuff(
            concept_str="native.Image", name="diagram", content=ImageContent(url=TestWorkingMemoryData.SAMPLE_IMAGE_URL)
        )

        return WorkingMemoryFactory.make_from_multiple_stuffs(stuff_list=[text_stuff, document_stuff, image_stuff], main_name="document")

    @pytest.fixture
    def memory_with_aliases(self) -> WorkingMemory:
        """Create WorkingMemory with aliases."""
        text_stuff = StuffFactory.make_stuff(concept_str="native.Text", name="primary_text", content=TextContent(text="Primary content"))

        secondary_stuff = StuffFactory.make_stuff(concept_str="native.Text", name="secondary_text", content=TextContent(text="Secondary content"))

        memory = WorkingMemory()
        memory.add_new_stuff(name="primary_text", stuff=text_stuff)
        memory.add_new_stuff(name="secondary_text", stuff=secondary_stuff)
        memory.set_alias(alias="main_text", target="primary_text")
        memory.set_alias(alias="backup_text", target="secondary_text")

        return memory

    @pytest.fixture
    def complex_list_memory(self) -> WorkingMemory:
        """Create WorkingMemory with complex list content containing mixed types."""
        complex_content: ListContent[TextContent | ImageContent | NumberContent] = ListContent(
            items=[
                TextContent(text="The quick brown fox jumps over the lazy dog"),
                ImageContent(url=TestWorkingMemoryData.SAMPLE_IMAGE_URL),
                NumberContent(number=42.5),
            ]
        )

        complex_stuff = StuffFactory.make_stuff(concept_str="native.List", name="mixed_list", content=complex_content)

        return WorkingMemoryFactory.make_from_single_stuff(stuff=complex_stuff)

    @pytest.fixture
    def text_and_images_memory(self) -> WorkingMemory:
        """Create WorkingMemory with text and images content."""
        text_and_images_content = TextAndImagesContent(
            text=TextContent(text="Project overview with diagrams"),
            images=[ImageContent(url=TestWorkingMemoryData.SAMPLE_IMAGE_URL), ImageContent(url="assets/diagrams/architecture.png")],
        )

        stuff = StuffFactory.make_stuff(concept_str="native.TextAndImages", name="project_overview", content=text_and_images_content)

        return WorkingMemoryFactory.make_from_single_stuff(stuff=stuff)

    @pytest.fixture
    def html_content_memory(self) -> WorkingMemory:
        """Create WorkingMemory with HTML content."""
        html_content = HtmlContent(
            inner_html="<h1>Test Report</h1><p>This is a <strong>test</strong> report.</p><ul><li>Item 1</li><li>Item 2</li></ul>",
            css_class="report-content",
        )

        stuff = StuffFactory.make_stuff(concept_str="native.Html", name="test_report", content=html_content)

        return WorkingMemoryFactory.make_from_single_stuff(stuff=stuff)

    @pytest.fixture
    def number_content_memory(self) -> WorkingMemory:
        """Create WorkingMemory with number content."""
        number_content = NumberContent(number=3.14159)

        stuff = StuffFactory.make_stuff(concept_str="native.Number", name="pi_value", content=number_content)

        return WorkingMemoryFactory.make_from_single_stuff(stuff=stuff)

    def test_working_memory_basic_functionality(self, single_text_memory: WorkingMemory):
        """Test basic WorkingMemory functionality."""
        # Should have one entry for the text content
        assert len(single_text_memory.root) == 1
        assert "sample_text" in single_text_memory.root

        # Check stuff retrieval
        stuff = single_text_memory.get_stuff("sample_text")
        assert stuff.concept_code == NativeConcept.TEXT.code
        assert isinstance(stuff.content, TextContent)
        assert stuff.content.text == TestWorkingMemoryData.SAMPLE_TEXT

    def test_working_memory_aliases(self, memory_with_aliases: WorkingMemory):
        """Test WorkingMemory alias functionality."""
        # Should have two root items and two aliases
        assert len(memory_with_aliases.root) == 2
        assert len(memory_with_aliases.aliases) == 2

        # Check aliases work
        primary_stuff = memory_with_aliases.get_stuff("primary_text")
        alias_stuff = memory_with_aliases.get_stuff("main_text")
        assert primary_stuff == alias_stuff

    def test_working_memory_empty(self):
        """Test empty WorkingMemory."""
        empty_memory = WorkingMemoryFactory.make_empty()
        assert len(empty_memory.root) == 0
        assert len(empty_memory.aliases) == 0
