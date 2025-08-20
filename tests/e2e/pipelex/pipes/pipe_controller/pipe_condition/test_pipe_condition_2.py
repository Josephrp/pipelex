import pytest
from pytest import FixtureRequest

from pipelex import pretty_print
from pipelex.core.memory.working_memory_factory import WorkingMemoryFactory
from pipelex.core.pipes.pipe_output import PipeOutput
from pipelex.core.pipes.pipe_run_params import PipeRunMode
from pipelex.core.pipes.pipe_run_params_factory import PipeRunParamsFactory
from pipelex.core.stuffs.stuff_factory import StuffFactory
from pipelex.hub import get_pipe_router, get_report_delegate
from pipelex.pipeline.job_metadata import JobMetadata
from tests.test_pipelines.pipe_controllers.pipe_condition.pipe_condition import CategoryInput


@pytest.mark.llm
@pytest.mark.inference
@pytest.mark.dry_runnable
@pytest.mark.asyncio(loop_scope="class")
class TestPipeConditionExpression:
    @pytest.mark.parametrize(
        "category",
        ["small", "medium", "large"],
    )
    async def test_pipe_condition_routing_expression(
        self,
        request: FixtureRequest,
        pipe_run_mode: PipeRunMode,
        category: str,
    ):
        """Test that PipeCondition routes to the correct pipe based on expression."""
        # Create input data
        category_input = CategoryInput(category=category)
        stuff = StuffFactory.make_stuff(
            concept_str="test_pipe_condition.CategoryInput",
            content=category_input,
            name="input_data",
        )

        # Create Working Memory
        working_memory = WorkingMemoryFactory.make_from_single_stuff(stuff)

        # Run the pipe
        pipe_output: PipeOutput = await get_pipe_router().run_pipe_code(
            pipe_code="basic_condition_by_category",
            pipe_run_params=PipeRunParamsFactory.make_run_params(pipe_run_mode=pipe_run_mode),
            working_memory=working_memory,
            job_metadata=JobMetadata(job_name=request.node.originalname),  # type: ignore
        )

        # Log output and generate report
        pretty_print(pipe_output, title=f"PipeCondition routing test - {category}")
        get_report_delegate().generate_report()

        # Basic assertions
        assert pipe_output is not None
        assert pipe_output.working_memory is not None
        if pipe_run_mode != PipeRunMode.DRY:
            assert category in pipe_output.main_stuff_as_text.text
