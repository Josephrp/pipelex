from __future__ import annotations

import asyncio
from typing import Annotated, Any, Dict, Optional, cast

import typer
from pydantic import ValidationError

from pipelex import pretty_print
from pipelex.exceptions import PipeDefinitionError, PipelexCLIError
from pipelex.hub import get_library_manager
from pipelex.libraries.library_manager import LibraryManager
from pipelex.libraries.pipeline_blueprint import PipelineLibraryBlueprint
from pipelex.pipe_works.pipe_dry import dry_run_pipe_codes
from pipelex.pipelex import Pipelex
from pipelex.pipeline.execute import execute_pipeline
from pipelex.tools.misc.file_utils import load_text_from_path
from pipelex.tools.typing.pydantic_utils import format_pydantic_validation_error


def _load_requirements_text(requirements: Optional[str], requirements_file: Optional[str]) -> str:
    if requirements_file:
        return load_text_from_path(requirements_file)
    if not requirements:
        raise PipelexCLIError("You must provide requirements text via --requirements or a file via --file")
    return requirements


async def _generate_blueprint_async(requirements_text: str) -> PipelineLibraryBlueprint:
    pipe_output = await execute_pipeline(
        pipe_code="generate_pipeline_blueprint",
        input_memory={
            "requirements": requirements_text,
        },
    )
    return pipe_output.main_stuff_as(content_type=PipelineLibraryBlueprint)


def do_build_blueprint(
    relative_config_folder_path: str,
    requirements: Optional[str],
    requirements_file: Optional[str],
    output_path: Optional[str],
    validate: bool,
) -> None:
    # Initialize Pipelex (loads libraries and pipes)
    Pipelex.make(relative_config_folder_path=relative_config_folder_path, from_file=False)

    # Get requirements text
    try:
        requirements_text = _load_requirements_text(requirements=requirements, requirements_file=requirements_file)
    except Exception as exc:
        raise PipelexCLIError(f"Failed to load requirements: {exc}") from exc

    # Generate blueprint
    blueprint = asyncio.run(_generate_blueprint_async(requirements_text=requirements_text))

    pretty_print(blueprint, title="Pipeline Blueprint")
    pretty_print(blueprint.to_toml_dict(), title="Pipeline Blueprint (TOML)")

    # Save or display result
    output_path = output_path or "pipelex/libraries/pipelines/temp/generated_blueprint.toml"
    blueprint.save_to_file(output_path)
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


# Typer group for build commands
build_app = typer.Typer(help="Build artifacts like pipeline blueprints")


@build_app.command("blueprint")
def build_blueprint_cmd(
    requirements: Annotated[
        Optional[str],
        typer.Option("--requirements", "-r", help="Requirements text to generate the pipeline blueprint from"),
    ] = None,
    requirements_file: Annotated[
        Optional[str],
        typer.Option("--file", "-f", help="Path to a file containing the requirements text"),
    ] = None,
    output_path: Annotated[
        Optional[str],
        typer.Option("--output", "-o", help="Path to save the generated TOML blueprint (optional)"),
    ] = None,
    validate: Annotated[
        bool,
        typer.Option("--validate", help="Dry-run the first generated pipe from the blueprint"),
    ] = False,
    relative_config_folder_path: Annotated[
        str,
        typer.Option(
            "--config-folder-path",
            "-c",
            help="Relative path to the config folder path (libraries)",
        ),
    ] = "./pipelex_libraries",
) -> None:
    # try:
    #     do_build_blueprint(
    #         relative_config_folder_path=relative_config_folder_path,
    #         requirements=requirements,
    #         requirements_file=requirements_file,
    #         output_path=output_path,
    #         validate=validate,
    #     )
    # except Exception as exc:
    #     typer.echo(f"❌ Error: {exc}")
    #     raise typer.Exit(1)

    do_build_blueprint(
        relative_config_folder_path=relative_config_folder_path,
        requirements=requirements,
        requirements_file=requirements_file,
        output_path=output_path,
        validate=validate,
    )
