from __future__ import annotations

from typing import Any, Dict, cast

from pipelex import log
from pipelex.exceptions import PipeDefinitionError, PipelexCLIError
from pipelex.hub import get_library_manager
from pipelex.libraries.library_manager import LibraryManager
from pipelex.libraries.pipeline_blueprint import PipelineBlueprint
from pipelex.pipe_works.pipe_dry import dry_run_pipe_codes


async def validate_blueprint(blueprint: PipelineBlueprint) -> None:
    # Load pipes from the blueprint
    try:
        _load_pipes_from_generated_blueprint(blueprint=blueprint)
    except PipeDefinitionError as exc:
        raise PipelexCLIError(f"Failed to load pipes from blueprint for domain '{blueprint.desc}': {exc}") from exc

    # Run validation
    log.info("Validating pipes ----------------------")
    log.info("Validating libraries ----------------------")
    get_library_manager().validate_libraries()
    generated_pipe_codes = list(blueprint.pipe.keys())
    if not generated_pipe_codes:
        raise PipelexCLIError("No pipe found in blueprint to validate")
    log.info(f"Dry running pipes: {generated_pipe_codes}")
    await dry_run_pipe_codes(pipe_codes=generated_pipe_codes)
    log.info(f"✅ All pipes validated successfully: {generated_pipe_codes}")


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
