"""Test pipe sequence functionality with output multiplicity and advanced features."""

import pytest
from pytest import FixtureRequest

from pipelex.core.memory.working_memory_factory import WorkingMemoryFactory
from pipelex.core.pipes.pipe_run_params import PipeRunMode
from pipelex.core.stuffs.stuff_content import TextContent
from pipelex.core.stuffs.stuff_factory import StuffFactory
from pipelex.pipeline.execute import execute_pipeline


@pytest.mark.dry_runnable
@pytest.mark.inference
@pytest.mark.asyncio
class TestPipeSequenceMultiplicity:
    async def test_creative_ideation_sequence_with_multiplicity(self, request: FixtureRequest, pipe_run_mode: PipeRunMode):
        """Test creative ideation sequence with nb_output and batching."""
        # Create test input
        topic_stuff = StuffFactory.make_stuff(
            name="topic",
            concept_str="creative_ideation.CreativeTopic",
            content=TextContent(text="Sustainable transportation solutions for urban areas"),
        )

        working_memory = WorkingMemoryFactory.make_from_multiple_stuffs([topic_stuff])

        # Execute the pipeline
        pipe_output = await execute_pipeline(
            pipe_code="creative_ideation_sequence",
            working_memory=working_memory,
            pipe_run_mode=pipe_run_mode,
        )

        # Basic assertions
        assert pipe_output is not None
        assert pipe_output.working_memory is not None
        assert pipe_output.main_stuff is not None
        assert pipe_output.main_stuff.concept_code == "creative_ideation.BestIdea"
