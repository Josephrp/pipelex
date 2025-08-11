from __future__ import annotations

from typing import Any, Dict, cast

from pipelex import log
from pipelex.exceptions import PipeDefinitionError, PipelexCLIError, StaticValidationError, StaticValidationErrorType
from pipelex.hub import get_library_manager, get_required_pipe
from pipelex.libraries.library_manager import LibraryManager
from pipelex.libraries.pipeline_blueprint import PipelineBlueprint
from pipelex.pipe_controllers.pipe_controller import PipeController
from pipelex.pipe_works.pipe_dry import dry_run_pipe_codes


async def validate_blueprint(blueprint: PipelineBlueprint, is_error_fixing_enabled: bool) -> None:
    # Load pipes from the blueprint
    log.dev("Loading pipes from blueprint")
    try:
        load_pipes_from_generated_blueprint(blueprint=blueprint, updates_allowed=True)
    except PipeDefinitionError as exc:
        raise PipelexCLIError(f"Failed to load pipes from blueprint for domain '{blueprint.desc}': {exc}") from exc

    try:
        await validate_loaded_blueprint(blueprint=blueprint)
    except StaticValidationError as static_validation_error:
        match static_validation_error.error_type:
            case StaticValidationErrorType.MISSING_INPUT_VARIABLE:
                if is_error_fixing_enabled:
                    pipe_code = static_validation_error.pipe_code
                    if not pipe_code:
                        raise PipelexCLIError(f"No pipe code found for static validation error: {static_validation_error}")
                    pipe = get_required_pipe(pipe_code=pipe_code)
                    if isinstance(pipe, PipeController):
                        variable_names = static_validation_error.variable_names
                        required_concept_codes = static_validation_error.required_concept_codes
                        if not variable_names:
                            raise PipelexCLIError(f"No variable names found for static validation error: {static_validation_error}")
                        if not required_concept_codes:
                            raise PipelexCLIError(f"No required concept codes found for static validation error: {static_validation_error}")
                        log.error(f"❌ Missing: {variable_names} / concepts: {required_concept_codes}")
                        for variable_name, concept_code in zip(variable_names, required_concept_codes):
                            if "inputs" not in blueprint.pipe[pipe_code]:
                                blueprint.pipe[pipe_code]["inputs"] = {}
                            blueprint.pipe[pipe_code]["inputs"][variable_name] = concept_code
                            log.info(f"✅ Added: {variable_name} / {concept_code}")
                        await validate_blueprint(blueprint=blueprint, is_error_fixing_enabled=True)
                    else:
                        raise PipelexCLIError(f"Unexpected validation error:\n{static_validation_error}") from static_validation_error
                else:
                    raise static_validation_error
            case (
                StaticValidationErrorType.EXTRANEOUS_INPUT_VARIABLE
                | StaticValidationErrorType.INADEQUATE_INPUT_CONCEPT
                | StaticValidationErrorType.TOO_MANY_CANDIDATE_INPUTS
            ):
                raise static_validation_error
    log.info("✅ Validation passed")


async def validate_loaded_blueprint(blueprint: PipelineBlueprint) -> None:
    # Run validation
    log.dev("Validating blueprint")
    get_library_manager().validate_libraries()
    generated_pipe_codes = list(blueprint.pipe.keys())
    if not generated_pipe_codes:
        raise PipelexCLIError("No pipe found in blueprint to validate")
    await dry_run_pipe_codes(pipe_codes=generated_pipe_codes)
    log.info(f"✅ All pipes validated successfully: {generated_pipe_codes}")


def load_pipes_from_generated_blueprint(blueprint: PipelineBlueprint, updates_allowed: bool = False) -> None:
    """Instantiate and register all pipes from a generated PipelineBlueprint.

    This constructs the appropriate typed PipeBlueprint for each pipe entry and
    uses LibraryManager.load_pipe_from_blueprint to create the Pipe, then adds it
    to the in-memory PipeLibrary so that validation can run against them.
    """
    library_manager = cast(LibraryManager, get_library_manager())
    domain_code = blueprint.domain

    for pipe_code, details in blueprint.pipe.items():
        details_dict: Dict[str, Any] = details.copy()

        pipe_blueprint = LibraryManager.make_pipe_blueprint_from_details(
            domain_code=domain_code,
            details_dict=details_dict,
        )
        # Create pipe and register in library
        pipe = LibraryManager.load_pipe_from_blueprint(
            pipe_code=pipe_code,
            pipe_blueprint=pipe_blueprint,
        )
        if updates_allowed:
            library_manager.pipe_library.add_or_update_pipe(pipe=pipe)
        else:
            library_manager.pipe_library.add_new_pipe(pipe=pipe)
