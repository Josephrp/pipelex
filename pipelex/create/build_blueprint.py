from __future__ import annotations

import asyncio
from pathlib import Path
from typing import Any, Dict, Optional, cast

import typer
from pydantic import ValidationError

from pipelex import log, pretty_print
from pipelex.create.helpers import get_support_file
from pipelex.create.pipeline_toml import save_pipeline_blueprint_toml_to_path
from pipelex.exceptions import PipeDefinitionError, PipelexCLIError
from pipelex.hub import get_library_manager
from pipelex.libraries.library_manager import LibraryManager
from pipelex.libraries.pipeline_blueprint import PipelineBlueprint
from pipelex.pipe_works.pipe_dry import dry_run_pipe_codes
from pipelex.pipeline.execute import execute_pipeline
from pipelex.tools.misc.file_utils import save_text_to_path
from pipelex.tools.misc.json_utils import save_as_json_to_path
from pipelex.tools.typing.pydantic_utils import format_pydantic_validation_error


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
    typer.echo(f"✅ Blueprint saved to '{output_path}'")

    if validate:
        try:
            _load_pipes_from_generated_blueprint(blueprint=blueprint)
        except PipeDefinitionError as exc:
            raise PipelexCLIError(f"Failed to load pipes from generated blueprint at '{output_path}': {exc}") from exc

        generated_pipe_codes = list(blueprint.pipe.keys())
        if not generated_pipe_codes:
            raise PipelexCLIError("No pipe found in generated blueprint to validate")
        log.info(f"Loaded pipes: {generated_pipe_codes}")

        log.info("Validating pipes...")
        asyncio.run(dry_run_pipe_codes(pipe_codes=generated_pipe_codes))
        log.info(f"Pipes validated: {generated_pipe_codes}")


def _load_pipes_from_generated_blueprint(blueprint: PipelineBlueprint) -> None:
    """Instantiate and register all pipes from a generated PipelineBlueprint.

    This constructs the appropriate typed PipeBlueprint for each pipe entry and
    uses LibraryManager.load_pipe_from_blueprint to create the Pipe, then adds it
    to the in-memory PipeLibrary so that validation can run against them.
    """
    library_manager = cast(LibraryManager, get_library_manager())
    domain_code = blueprint.domain

    for pipe_code, details in blueprint.pipe.items():
        details_dict: Dict[str, Any] = details.copy()

        # Build the concrete PipeBlueprint via LibraryManager helper
        # try:
        #     pipe_blueprint = LibraryManager.make_pipe_blueprint_from_details(
        #         domain_code=domain_code,
        #         details_dict=details_dict,
        #     )
        # except ValidationError as exc:
        #     error_msg = format_pydantic_validation_error(exc=exc)
        #     raise PipeDefinitionError(f"Failed to build pipe blueprint for pipe '{pipe_code}': {error_msg}\n{exc}") from exc

        pipe_blueprint = LibraryManager.make_pipe_blueprint_from_details(
            domain_code=domain_code,
            details_dict=details_dict,
        )
        # Create pipe and register in library
        pipe = LibraryManager.load_pipe_from_blueprint(
            pipe_code=pipe_code,
            pipe_blueprint=pipe_blueprint,
        )
        library_manager.pipe_library.add_new_pipe(pipe=pipe)
