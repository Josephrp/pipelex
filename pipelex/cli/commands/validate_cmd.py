from __future__ import annotations

import asyncio
from typing import Annotated

import typer

from pipelex import log
from pipelex.create.build_blueprint import validate_blueprint as do_validate_blueprint
from pipelex.hub import get_pipeline_tracker
from pipelex.pipe_works.pipe_dry import dry_run_all_pipes, dry_run_single_pipe
from pipelex.pipelex import Pipelex

from .common import is_pipelex_libraries_folder


def do_validate(relative_config_folder_path: str = "./pipelex_libraries") -> None:
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


# Typer group for validation commands
validate_app = typer.Typer(help="Validation and dry-run commands")


@validate_app.command("all")
def validate_all_cmd(
    relative_config_folder_path: Annotated[
        str, typer.Option("--config-folder-path", "-c", help="Relative path to the config folder path")
    ] = "./pipelex_libraries",
) -> None:
    do_validate(relative_config_folder_path=relative_config_folder_path)


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
    asyncio.run(do_validate_blueprint(blueprint_path=blueprint_path))
    log.info("Blueprint validation completed successfully.")
