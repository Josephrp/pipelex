from __future__ import annotations

import asyncio
from pathlib import Path
from typing import Annotated, Any, Dict, Optional, cast

import typer
from pydantic import ValidationError

from pipelex import log, pretty_print
from pipelex.cli.commands.common import is_pipelex_libraries_folder
from pipelex.create.helpers import get_support_file
from pipelex.create.pipeline_toml import save_pipeline_blueprint_toml_to_path
from pipelex.create.validate_blueprint import validate_blueprint
from pipelex.exceptions import PipeDefinitionError, PipelexCLIError
from pipelex.hub import get_library_manager, get_pipeline_tracker
from pipelex.libraries.library_manager import LibraryManager
from pipelex.libraries.pipeline_blueprint import PipelineBlueprint
from pipelex.pipe_works.pipe_dry import dry_run_all_pipes, dry_run_pipe_codes, dry_run_single_pipe
from pipelex.pipelex import Pipelex
from pipelex.pipeline.execute import execute_pipeline
from pipelex.tools.misc.file_utils import save_text_to_path
from pipelex.tools.misc.json_utils import save_as_json_to_path
from pipelex.tools.misc.toml_utils import load_toml_from_path
from pipelex.tools.typing.pydantic_utils import format_pydantic_validation_error


def do_validate_all_libraries_and_dry_run(relative_config_folder_path: str = "./pipelex_libraries") -> None:
    """Validate libraries and dry-run all pipes."""
    if not is_pipelex_libraries_folder(relative_config_folder_path):
        typer.echo(f"❌ No pipelex libraries folder found at '{relative_config_folder_path}'")
        typer.echo("To create a pipelex libraries folder, run: pipelex init-libraries")
        raise typer.Exit(1)

    pipelex_instance = Pipelex.make(relative_config_folder_path=relative_config_folder_path, from_file=False)
    pipelex_instance.validate_libraries()
    asyncio.run(dry_run_all_pipes())
    log.info("Setup sequence passed OK, config and pipelines are validated.")


def do_dry_run_pipe(pipe_code: str, relative_config_folder_path: str = "./pipelex_libraries") -> None:
    """Dry run a single pipe."""
    if not is_pipelex_libraries_folder(relative_config_folder_path):
        typer.echo(f"❌ No pipelex libraries folder found at '{relative_config_folder_path}'")
        typer.echo("To create a pipelex libraries folder, run: pipelex init-libraries")
        raise typer.Exit(1)

    try:
        pipelex_instance = Pipelex.make(relative_config_folder_path=relative_config_folder_path, from_file=False)
        pipelex_instance.validate_libraries()
        asyncio.run(dry_run_single_pipe(pipe_code))
        get_pipeline_tracker().output_flowchart()
    except Exception as exc:
        typer.echo(f"❌ Error running dry run for pipe '{pipe_code}': {exc}")
        raise typer.Exit(1)


async def do_validate_blueprint_toml_file(blueprint_path: str) -> None:
    """Validate an already generated pipeline blueprint from a TOML file.

    Args:
        blueprint_path: Path to the blueprint TOML file to validate

    Raises:
        PipelexCLIError: If validation fails
        ValidationError: If the TOML structure doesn't match PipelineBlueprint
    """
    # Load the TOML file
    log.info(f"Loading blueprint from '{blueprint_path}'...")
    blueprint_dict = load_toml_from_path(path=blueprint_path)

    # Validate and create PipelineBlueprint model
    try:
        blueprint = PipelineBlueprint.model_validate(blueprint_dict)
    except ValidationError as exc:
        error_msg = format_pydantic_validation_error(exc=exc)
        raise PipelexCLIError(f"Invalid blueprint structure in '{blueprint_path}': {error_msg}") from exc

    log.info(f"Blueprint loaded successfully: domain='{blueprint.domain}'")

    await validate_blueprint(blueprint=blueprint)


# Typer group for validation commands
validate_app = typer.Typer(help="Validation and dry-run commands")


@validate_app.command("all")
def validate_all_cmd(
    relative_config_folder_path: Annotated[
        str, typer.Option("--config-folder-path", "-c", help="Relative path to the config folder path")
    ] = "./pipelex_libraries",
) -> None:
    do_validate_all_libraries_and_dry_run(relative_config_folder_path=relative_config_folder_path)


@validate_app.command("pipe")
def dry_run_pipe_cmd(
    pipe_code: Annotated[str, typer.Argument(help="The pipe code to dry run")],
    relative_config_folder_path: Annotated[
        str, typer.Option("--config-folder-path", "-c", help="Relative path to the config folder path")
    ] = "./pipelex_libraries",
) -> None:
    do_dry_run_pipe(pipe_code=pipe_code, relative_config_folder_path=relative_config_folder_path)


@validate_app.command("blueprint")
def validate_blueprint_cmd(
    blueprint_path: Annotated[str, typer.Argument(help="Path to the blueprint TOML file to validate")],
    relative_config_folder_path: Annotated[
        str, typer.Option("--config-folder-path", "-c", help="Relative path to the config folder path")
    ] = "./pipelex_libraries",
) -> None:
    """Validate an already generated pipeline blueprint TOML file.

    This command loads the TOML file, validates it against the `PipelineBlueprint` model,
    loads the defined pipes into memory, and performs a dry-run validation of those pipes.
    """
    if not is_pipelex_libraries_folder(relative_config_folder_path):
        typer.echo(f"❌ No pipelex libraries folder found at '{relative_config_folder_path}'")
        typer.echo("To create a pipelex libraries folder, run: pipelex init-libraries")
        raise typer.Exit(1)

    # Initialize Pipelex (loads libraries and pipes)
    Pipelex.make(relative_config_folder_path=relative_config_folder_path, from_file=False)

    # Run validation
    asyncio.run(do_validate_blueprint_toml_file(blueprint_path=blueprint_path))
    log.info("Blueprint validation completed successfully.")
