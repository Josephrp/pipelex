from __future__ import annotations

import asyncio
from pathlib import Path
from typing import Annotated, Any, Dict, Optional, cast

import typer
from pydantic import ValidationError

from pipelex import pretty_print
from pipelex.create.helpers import get_pipeline_creation_rules
from pipelex.exceptions import PipeDefinitionError, PipelexCLIError
from pipelex.hub import get_library_manager
from pipelex.libraries.library_manager import LibraryManager
from pipelex.libraries.pipeline_blueprint import PipelineLibraryBlueprint
from pipelex.libraries.pipelines.meta.pipeline_draft import PipelineDraft
from pipelex.pipe_works.pipe_dry import dry_run_pipe_codes
from pipelex.pipelex import Pipelex
from pipelex.pipeline.execute import execute_pipeline
from pipelex.tools.misc.file_utils import load_text_from_path
from pipelex.tools.misc.json_utils import save_as_json_to_path
from pipelex.tools.misc.toml_utils import dict_to_toml_string, save_toml_to_path
from pipelex.tools.typing.pydantic_utils import format_pydantic_validation_error


async def do_build_blueprint(
    pipeline_name: str,
    requirements: str,
    output_path: Optional[str],
    validate: bool,
) -> None:
    pipe_output = await execute_pipeline(
        pipe_code="build_blueprint",
        input_memory={
            "pipeline_name": pipeline_name,
            "requirements": requirements,
            "rules": get_pipeline_creation_rules(),
        },
    )
    blueprint = pipe_output.main_stuff_as(content_type=PipelineLibraryBlueprint)
    pretty_print(blueprint, title="Pipeline Blueprint")

    # Save or display result
    output_path = output_path or "pipelex/libraries/pipelines/temp/generated_blueprint.toml"
    save_toml_to_path(blueprint.smart_dump(), output_path)
    json_path = output_path.replace(Path(output_path).suffix, ".json")
    save_as_json_to_path(blueprint.smart_dump(), json_path)
    typer.echo(f"✅ Blueprint saved to '{output_path}'")

    if validate:
        try:
            _load_pipes_from_generated_blueprint(blueprint=blueprint)
        except PipeDefinitionError as exc:
            raise PipelexCLIError(f"Failed to load pipes from generated blueprint at '{output_path}': {exc}") from exc

        generated_pipe_codes = list(blueprint.pipe.keys())
        if not generated_pipe_codes:
            raise PipelexCLIError("No pipe found in generated blueprint to validate")
        asyncio.run(dry_run_pipe_codes(pipe_codes=generated_pipe_codes))


def _load_pipes_from_generated_blueprint(blueprint: PipelineLibraryBlueprint) -> None:
    """Instantiate and register all pipes from a generated PipelineLibraryBlueprint.

    This constructs the appropriate typed PipeBlueprint for each pipe entry and
    uses LibraryManager.load_pipe_from_blueprint to create the Pipe, then adds it
    to the in-memory PipeLibrary so that validation can run against them.
    """
    library_manager = cast(LibraryManager, get_library_manager())
    domain_code = blueprint.domain

    for pipe_code, details in blueprint.pipe.items():
        details_dict: Dict[str, Any] = details.copy()

        # Build the concrete PipeBlueprint via LibraryManager helper
        try:
            pipe_blueprint = LibraryManager.make_pipe_blueprint_from_details(
                domain_code=domain_code,
                details_dict=details_dict,
            )
        except ValidationError as exc:
            error_msg = format_pydantic_validation_error(exc=exc)
            raise PipeDefinitionError(f"Failed to build pipe blueprint for pipe '{pipe_code}': {error_msg}") from exc

        # Create pipe and register in library
        pipe = LibraryManager.load_pipe_from_blueprint(
            pipe_code=pipe_code,
            pipe_blueprint=pipe_blueprint,
        )
        library_manager.pipe_library.add_new_pipe(pipe=pipe)
