from __future__ import annotations

from pathlib import Path
from typing import Optional

import typer

from pipelex import log, pretty_print
from pipelex.create.helpers import get_support_file
from pipelex.create.pipeline_toml import save_pipeline_blueprint_toml_to_path
from pipelex.create.validate_blueprint import load_pipes_from_generated_blueprint, validate_blueprint
from pipelex.exceptions import PipelexCLIError, StaticValidationError, StaticValidationErrorType
from pipelex.hub import get_library_manager, get_required_pipe
from pipelex.libraries.pipeline_blueprint import PipelineBlueprint
from pipelex.pipe_controllers.pipe_controller import PipeController
from pipelex.pipeline.execute import execute_pipeline
from pipelex.tools.misc.file_utils import save_text_to_path
from pipelex.tools.misc.json_utils import save_as_json_to_path


async def do_build_blueprint(
    domain: str,
    pipeline_name: str,
    requirements: str,
    output_path: Optional[str],
    validate: bool,
) -> None:
    pipe_output = await execute_pipeline(
        pipe_code="build_blueprint",
        input_memory={
            "domain": domain,
            "pipeline_name": pipeline_name,
            "requirements": requirements,
            "draft_pipeline_rules": get_support_file(subpath="create/draft_pipelines.md"),
            "build_pipeline_rules": get_support_file(subpath="create/build_pipelines.md"),
        },
    )
    blueprint = pipe_output.main_stuff_as(content_type=PipelineBlueprint)
    pretty_print(blueprint, title="Pipeline Blueprint")
    pipeline_draft = pipe_output.working_memory.get_stuff_as_str(name="pipeline_draft")
    pretty_print(pipeline_draft, title="Pipeline Draft")

    # Save or display result
    output_path = output_path or "pipelex/libraries/pipelines/temp/generated_blueprint.toml"
    # blueprint_dict = blueprint.smart_dump()
    # save_toml_to_path(data=blueprint_dict, path=output_path)
    save_pipeline_blueprint_toml_to_path(blueprint=blueprint, path=output_path)
    json_path = output_path.replace(Path(output_path).suffix, ".json")
    save_as_json_to_path(object_to_save=blueprint, path=json_path)
    draft_path = output_path.replace(Path(output_path).suffix, "_draft.md")
    save_text_to_path(text=pipeline_draft, path=draft_path)
    log.info(f"✅ Blueprint saved to '{output_path}'")

    load_pipes_from_generated_blueprint(blueprint=blueprint)
    log.info("✅ Pipes loaded from blueprint")

    if validate:
        await validate_blueprint(blueprint=blueprint, is_error_fixing_enabled=True)
