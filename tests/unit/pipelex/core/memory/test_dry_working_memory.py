"""Test dry working memory functionality."""

from typing import List

import pytest
from pytest import FixtureRequest

from pipelex import log
from pipelex.core.concepts.concept_native import NativeConcept
from pipelex.core.memory.working_memory_factory import WorkingMemoryFactory
from pipelex.core.pipes.pipe_input_spec import TypedNamedInputRequirement
from pipelex.core.stuffs.stuff_content import PageContent, TextContent
from tests.test_pipelines.tricky_questions import ThoughtfulAnswer


@pytest.mark.dry_runnable
@pytest.mark.asyncio(loop_scope="class")
class TestDryWorkingMemory:
    """Test WorkingMemory dry run functionality."""

    async def test_make_for_dry_run_with_page_content(
        self,
        request: FixtureRequest,
    ):
        """Test that make_for_dry_run creates appropriate mocks for PageContent."""
        log.info("Testing dry run with PageContent")

        # Test the specific inputs requested by the user
        needed_inputs = [
            TypedNamedInputRequirement(
                variable_name="page",
                concept_code=NativeConcept.PAGE.code,
                structure_class=PageContent,
            ),
        ]

        dry_memory = WorkingMemoryFactory.make_for_dry_run(needed_inputs=needed_inputs)
        # Verify working memory contains exactly this
        assert len(dry_memory.root) == 1
        assert dry_memory.get_optional_stuff("page") is not None

        # Verify concept code is correct
        page_stuff = dry_memory.get_stuff("page")
        assert page_stuff.concept_code == NativeConcept.PAGE.code
        assert page_stuff.stuff_name == "page"

        # Verify structured content was created properly
        page_content = page_stuff.content
        assert isinstance(page_content, PageContent)

        # Verify PageContent has the expected structure
        assert hasattr(page_content, "text_and_images")
        assert hasattr(page_content, "page_view")

        # Verify text_and_images field exists and has mock data
        assert page_content.text_and_images is not None

        # Verify page_view field exists (it's Optional so could be None)
        assert hasattr(page_content, "page_view")

    async def test_make_for_dry_run_with_structured_content(
        self,
        request: FixtureRequest,
    ):
        """Test that make_for_dry_run creates appropriate mocks for structured content."""
        log.info("Testing dry run with structured content (ThoughtfulAnswer)")

        # Use ThoughtfulAnswer from tricky questions domain
        needed_inputs = [
            TypedNamedInputRequirement(
                variable_name="thoughtful_answer",
                concept_code="test_tricky_questions.ThoughtfulAnswer",
                structure_class=ThoughtfulAnswer,
            ),
            TypedNamedInputRequirement(
                variable_name="question",
                concept_code="answer.Question",
                structure_class=TextContent,
            ),
        ]

        dry_memory = WorkingMemoryFactory.make_for_dry_run(needed_inputs=needed_inputs)

        # Verify mocks were created
        assert len(dry_memory.root) == 2
        assert dry_memory.get_optional_stuff("thoughtful_answer") is not None
        assert dry_memory.get_optional_stuff("question") is not None

        # Verify concept codes are preserved
        thoughtful_answer_stuff = dry_memory.get_stuff("thoughtful_answer")
        assert thoughtful_answer_stuff.concept_code == "test_tricky_questions.ThoughtfulAnswer"

        question_stuff = dry_memory.get_stuff("question")
        assert question_stuff.concept_code == "answer.Question"

        # Verify structured content was created properly
        thoughtful_answer_content = thoughtful_answer_stuff.content
        assert isinstance(thoughtful_answer_content, ThoughtfulAnswer)
        assert hasattr(thoughtful_answer_content, "the_trap")
        assert hasattr(thoughtful_answer_content, "the_counter")
        assert hasattr(thoughtful_answer_content, "the_lesson")
        assert hasattr(thoughtful_answer_content, "the_answer")

        # Verify all fields have mock values
        assert thoughtful_answer_content.the_trap is not None
        assert thoughtful_answer_content.the_counter is not None
        assert thoughtful_answer_content.the_lesson is not None
        assert thoughtful_answer_content.the_answer is not None

        log.info("Created mock working memory with structured content:")
        dry_memory.pretty_print_summary()

    async def test_make_for_dry_run_with_text_content_fallback(
        self,
        request: FixtureRequest,
    ):
        """Test that make_for_dry_run falls back to TextContent when needed."""
        log.info("Testing dry run with TextContent fallback")

        needed_inputs = [
            TypedNamedInputRequirement(
                variable_name="question_analysis",
                concept_code="QuestionAnalysis",
                structure_class=TextContent,
            ),
            TypedNamedInputRequirement(
                variable_name="conclusion",
                concept_code="test_tricky_questions.ThoughtfulAnswerConclusion",
                structure_class=TextContent,
            ),
        ]

        dry_memory = WorkingMemoryFactory.make_for_dry_run(needed_inputs=needed_inputs)

        # Verify mocks were created
        assert len(dry_memory.root) == 2
        assert dry_memory.get_optional_stuff("question_analysis") is not None
        assert dry_memory.get_optional_stuff("conclusion") is not None

        # Verify both use TextContent
        question_analysis_stuff = dry_memory.get_stuff("question_analysis")
        assert isinstance(question_analysis_stuff.content, TextContent)
        assert question_analysis_stuff.concept_code == "QuestionAnalysis"

        conclusion_stuff = dry_memory.get_stuff("conclusion")
        assert isinstance(conclusion_stuff.content, TextContent)
        assert conclusion_stuff.concept_code == "test_tricky_questions.ThoughtfulAnswerConclusion"

        log.info("Created mock working memory with TextContent fallback:")
        dry_memory.pretty_print_summary()

    async def test_make_for_dry_run_mixed_content_types(
        self,
        request: FixtureRequest,
    ):
        """Test that make_for_dry_run handles mixed content types correctly."""
        log.info("Testing dry run with mixed content types")

        needed_inputs = [
            TypedNamedInputRequirement(
                variable_name="thoughtful_answer",
                concept_code="test_tricky_questions.ThoughtfulAnswer",
                structure_class=ThoughtfulAnswer,
            ),
            TypedNamedInputRequirement(
                variable_name="raw_question",
                concept_code="answer.Question",
                structure_class=TextContent,
            ),
            TypedNamedInputRequirement(
                variable_name="analysis_result",
                concept_code="QuestionAnalysis",
                structure_class=TextContent,
            ),
        ]

        dry_memory = WorkingMemoryFactory.make_for_dry_run(needed_inputs=needed_inputs)

        # Verify all mocks were created
        assert len(dry_memory.root) == 3

        # Verify structured content
        thoughtful_answer_stuff = dry_memory.get_stuff("thoughtful_answer")
        assert isinstance(thoughtful_answer_stuff.content, ThoughtfulAnswer)
        assert thoughtful_answer_stuff.concept_code == "test_tricky_questions.ThoughtfulAnswer"

        # Verify text content
        raw_question_stuff = dry_memory.get_stuff("raw_question")
        assert isinstance(raw_question_stuff.content, TextContent)
        assert raw_question_stuff.concept_code == "answer.Question"

        analysis_result_stuff = dry_memory.get_stuff("analysis_result")
        assert isinstance(analysis_result_stuff.content, TextContent)
        assert analysis_result_stuff.concept_code == "QuestionAnalysis"

        log.info("Created mock working memory with mixed content types:")
        dry_memory.pretty_print_summary()

    async def test_make_for_dry_run_empty_inputs(
        self,
        request: FixtureRequest,
    ):
        """Test that make_for_dry_run handles empty inputs gracefully."""
        log.info("Testing dry run with empty inputs")

        needed_inputs: List[TypedNamedInputRequirement] = []

        dry_memory = WorkingMemoryFactory.make_for_dry_run(needed_inputs=needed_inputs)

        # Verify empty memory was created
        assert len(dry_memory.root) == 0
        assert dry_memory.root == {}

        log.info("Created empty mock working memory")

    async def test_make_for_dry_run_realistic_pipeline_scenario(
        self,
        request: FixtureRequest,
    ):
        """Test make_for_dry_run with a realistic pipeline scenario from tricky questions."""
        log.info("Testing dry run with realistic tricky questions pipeline scenario")

        # Simulate the conclude_tricky_question_by_steps pipeline needs
        needed_inputs = [
            TypedNamedInputRequirement(
                variable_name="question",
                concept_code="answer.Question",
                structure_class=TextContent,
            ),
            TypedNamedInputRequirement(
                variable_name="question_analysis",
                concept_code="QuestionAnalysis",
                structure_class=TextContent,
            ),
            TypedNamedInputRequirement(
                variable_name="thoughtful_answer",
                concept_code="test_tricky_questions.ThoughtfulAnswer",
                structure_class=ThoughtfulAnswer,
            ),
        ]

        dry_memory = WorkingMemoryFactory.make_for_dry_run(needed_inputs=needed_inputs)

        # Verify the complete pipeline inputs are mocked
        assert len(dry_memory.root) == 3

        # Test question input
        question_stuff = dry_memory.get_stuff("question")
        assert isinstance(question_stuff.content, TextContent)
        assert len(question_stuff.content.text) > 0  # Should have mock text

        # Test question analysis input
        question_analysis_stuff = dry_memory.get_stuff("question_analysis")
        assert isinstance(question_analysis_stuff.content, TextContent)
        assert len(question_analysis_stuff.content.text) > 0  # Should have mock text

        # Test thoughtful answer input (structured)
        thoughtful_answer_stuff = dry_memory.get_stuff("thoughtful_answer")
        assert isinstance(thoughtful_answer_stuff.content, ThoughtfulAnswer)

        # Verify the ThoughtfulAnswer has all required fields with mock data
        ta_content = thoughtful_answer_stuff.content
        assert isinstance(ta_content.the_trap, str) and len(ta_content.the_trap) > 0
        assert isinstance(ta_content.the_counter, str) and len(ta_content.the_counter) > 0
        assert isinstance(ta_content.the_lesson, str) and len(ta_content.the_lesson) > 0
        assert isinstance(ta_content.the_answer, str) and len(ta_content.the_answer) > 0

        log.info("Created realistic pipeline mock memory:")
        dry_memory.pretty_print_summary()

        # Log the detailed thoughtful answer content for verification
        log.info("Mock ThoughtfulAnswer details:")
        log.info(f"  - the_trap: {ta_content.the_trap}")
        log.info(f"  - the_counter: {ta_content.the_counter}")
        log.info(f"  - the_lesson: {ta_content.the_lesson}")
        log.info(f"  - the_answer: {ta_content.the_answer}")
