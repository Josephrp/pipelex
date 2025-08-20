from pathlib import Path
from typing import Any, Optional, Tuple, Type

import pytest
from pytest import FixtureRequest

from pipelex import log, pretty_print
from pipelex.config import get_config
from pipelex.core.memory.working_memory import WorkingMemory
from pipelex.core.memory.working_memory_factory import WorkingMemoryFactory
from pipelex.core.pipes.pipe_output import PipeOutput
from pipelex.core.pipes.pipe_run_params import PipeOutputMultiplicity, PipeRunMode
from pipelex.core.pipes.pipe_run_params_factory import PipeRunParamsFactory
from pipelex.core.stuffs.stuff import Stuff
from pipelex.core.stuffs.stuff_factory import StuffBlueprint
from pipelex.hub import get_library_manager, get_pipe_router, get_report_delegate
from pipelex.pipeline.activity.activity_handler import ActivityHandlerForResultFiles
from pipelex.pipeline.job_metadata import JobMetadata
from tests.integration.pipelex.test_data import PipeTestCases


@pytest.mark.dry_runnable
@pytest.mark.llm
@pytest.mark.ocr
@pytest.mark.inference
@pytest.mark.asyncio(loop_scope="class")
class TestPipeRunningVariants:
    @pytest.mark.parametrize("topic, blueprint, pipe_code", PipeTestCases.BLUEPRINT_AND_PIPE)
    async def test_pipe_from_blueprint(
        self,
        pipe_run_mode: PipeRunMode,
        request: FixtureRequest,
        pipe_result_handler: Tuple[str, ActivityHandlerForResultFiles],
        save_working_memory: Any,
        topic: str,
        blueprint: StuffBlueprint,
        pipe_code: str,
    ):
        log.verbose(blueprint, title=f"{topic}: start from '{blueprint.stuff_name}', run pipe '{pipe_code}'")
        working_memory = WorkingMemoryFactory.make_from_single_blueprint(blueprint=blueprint)
        pipe_output: PipeOutput = await get_pipe_router().run_pipe_code(
            pipe_code=pipe_code,
            pipe_run_params=PipeRunParamsFactory.make_run_params(pipe_run_mode=pipe_run_mode),
            working_memory=working_memory,
            job_metadata=JobMetadata(job_name=request.node.originalname),  # type: ignore
        )
        log.verbose(pipe_output, title="pipe_output")
        pretty_print(pipe_output, title="pipe_output")

        # Save stuff context
        result_dir_path, _ = pipe_result_handler
        await save_working_memory(pipe_output, result_dir_path)

        get_report_delegate().generate_report()

    @pytest.mark.parametrize("topic, stuff, pipe_code", PipeTestCases.STUFF_AND_PIPE)
    async def test_pipe_from_stuff(
        self,
        pipe_run_mode: PipeRunMode,
        request: FixtureRequest,
        pipe_result_handler: Tuple[str, ActivityHandlerForResultFiles],
        save_working_memory: Any,
        topic: str,
        stuff: Stuff,
        pipe_code: str,
    ):
        log.verbose(stuff, title=f"{topic}: start from '{stuff.stuff_name}', run pipe '{pipe_code}'")
        working_memory = WorkingMemoryFactory.make_from_single_stuff(stuff=stuff)
        pipe_output: PipeOutput = await get_pipe_router().run_pipe_code(
            pipe_code=pipe_code,
            pipe_run_params=PipeRunParamsFactory.make_run_params(pipe_run_mode=pipe_run_mode),
            working_memory=working_memory,
            job_metadata=JobMetadata(job_name=request.node.originalname),  # type: ignore
        )
        get_report_delegate().generate_report()

        # Save stuff context
        result_dir_path, _ = pipe_result_handler
        await save_working_memory(pipe_output, result_dir_path)

    @pytest.mark.parametrize("topic, pipe_code", PipeTestCases.NO_INPUT)
    async def test_pipe_no_input(
        self,
        pipe_run_mode: PipeRunMode,
        request: FixtureRequest,
        pipe_result_handler: Tuple[str, ActivityHandlerForResultFiles],
        save_working_memory: Any,
        topic: str,
        pipe_code: str,
    ):
        log.verbose(f"{topic}: just run pipe '{pipe_code}'")
        pipe_output: PipeOutput = await get_pipe_router().run_pipe_code(
            pipe_code=pipe_code,
            pipe_run_params=PipeRunParamsFactory.make_run_params(pipe_run_mode=pipe_run_mode),
            working_memory=WorkingMemory(),
            job_metadata=JobMetadata(job_name=request.node.originalname),  # type: ignore
        )
        get_report_delegate().generate_report()

        # Save stuff context
        result_dir_path, _ = pipe_result_handler
        await save_working_memory(pipe_output, result_dir_path)

        stuff = pipe_output.main_stuff
        pretty_print(stuff, title=f"{topic}: run pipe '{pipe_code}'")
        pretty_print(stuff.content.rendered_html(), title=f"{topic}: run pipe '{pipe_code}' in html")
        pretty_print(stuff.content.rendered_markdown(), title=f"{topic}: run pipe '{pipe_code}' in markdown")

    @pytest.mark.parametrize("topic, pipe_code, output_multiplicity", PipeTestCases.NO_INPUT_PARALLEL1)
    async def test_pipe_batch_no_input(
        self,
        pipe_run_mode: PipeRunMode,
        request: FixtureRequest,
        pipe_result_handler: Tuple[str, ActivityHandlerForResultFiles],
        save_working_memory: Any,
        topic: str,
        pipe_code: str,
        output_multiplicity: Optional[PipeOutputMultiplicity],
    ):
        log.verbose(f"{topic}: just run pipe '{pipe_code}'")
        pipe_output: PipeOutput = await get_pipe_router().run_pipe_code(
            pipe_code=pipe_code,
            pipe_run_params=PipeRunParamsFactory.make_run_params(
                pipe_run_mode=pipe_run_mode,
                output_multiplicity=output_multiplicity,
            ),
            working_memory=WorkingMemory(),
            job_metadata=JobMetadata(job_name=request.node.originalname),  # type: ignore
        )
        get_report_delegate().generate_report()

        # Save stuff context
        result_dir_path, _ = pipe_result_handler
        await save_working_memory(pipe_output, result_dir_path)

        stuff = pipe_output.main_stuff
        pretty_print(stuff, title=f"{topic}: run pipe '{pipe_code}'")
        pretty_print(stuff.content.rendered_html(), title=f"{topic}: run pipe '{pipe_code}' in html")
        pretty_print(stuff.content.rendered_markdown(), title=f"{topic}: run pipe '{pipe_code}' in markdown")

    @pytest.mark.parametrize("pipe_code, exception, expected_error_message", PipeTestCases.FAILURE_PIPES)
    async def test_pipe_infinite_loop(
        self,
        pipe_run_mode: PipeRunMode,
        request: FixtureRequest,
        pipe_code: str,
        exception: Type[Exception],
        expected_error_message: str,
    ):
        failing_pipelines_file_paths = get_config().pipelex.library_config.failing_pipelines_file_paths
        library_manager = get_library_manager()
        library_manager.load_libraries(
            library_file_paths=[Path(failing_pipeline_file_path) for failing_pipeline_file_path in failing_pipelines_file_paths]
        )

        log.verbose(f"This pipe '{pipe_code}' is supposed to cause an error of type: {exception.__name__}")
        with pytest.raises(exception) as exc:
            await get_pipe_router().run_pipe_code(
                pipe_code=pipe_code,
                pipe_run_params=PipeRunParamsFactory.make_run_params(
                    pipe_stack_limit=6,
                    pipe_run_mode=pipe_run_mode,
                ),
                job_metadata=JobMetadata(job_name=request.node.originalname),  # type: ignore
            )
        pretty_print(exc.value, title="exception")
        assert expected_error_message in str(exc.value)
        get_report_delegate().generate_report()
