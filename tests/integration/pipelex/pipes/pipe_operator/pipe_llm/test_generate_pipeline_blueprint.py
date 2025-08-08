import pytest

from pipelex import pretty_print
from pipelex.core.pipe_run_params import PipeRunMode
from pipelex.libraries.pipeline_blueprint import PipelineLibraryBlueprint
from pipelex.pipeline.execute import execute_pipeline


@pytest.mark.asyncio(loop_scope="class")
@pytest.mark.dry_runnable
@pytest.mark.llm
@pytest.mark.inference
@pytest.mark.parametrize(
    "requirements",
    [
        (
            "Create a domain 'sample' to describe simple demo pipelines. "
            "Define concept ThingDescription = 'A short natural language description of a thing'. "
            "Add a pipe write_thing that takes input { text = Text } and outputs ThingDescription using PipeLLM."
        ),
        (
            "Domain: gadgets. Concept: GadgetSpec = 'Technical description of a gadget'. "
            "Add pipe summarize_gadget: inputs { text = Text } -> output GadgetSpec via PipeLLM."
        ),
    ],
)
async def test_generate_pipeline_blueprint_dry_run(pipe_run_mode: PipeRunMode, requirements: str):
    pipe_output = await execute_pipeline(
        pipe_code="generate_pipeline_blueprint",
        input_memory={
            "requirements": requirements,
        },
        pipe_run_mode=pipe_run_mode,
    )

    blueprint = pipe_output.main_stuff_as(content_type=PipelineLibraryBlueprint)
    assert isinstance(blueprint, PipelineLibraryBlueprint)
    # Basic sanity checks
    assert isinstance(blueprint.domain, str) and blueprint.domain != ""

    pretty_print(blueprint, title="PipelineBlueprint")
    pretty_print(blueprint.to_toml_dict(), title="PipelineBlueprint TOML")
