from __future__ import annotations

from pathlib import Path
from typing import Annotated

import typer

from pipelex.tools.migrate.migrate_v0_1_0_to_v0_2_0 import TomlMigrator, migrate_concept_syntax

from .common import is_pipelex_libraries_folder


def do_migrate(
    relative_config_folder_path: str = "./pipelex_libraries",
    dry_run: bool = False,
    backups: bool = True,
) -> None:
    """Migrate TOML files to new syntax (Concept = -> definition = and PipeClassName = -> type/definition)."""
    config_path = Path(relative_config_folder_path)

    if is_pipelex_libraries_folder(relative_config_folder_path):
        pipelines_dir = config_path / "pipelines"
    else:
        pipelines_dir = config_path

    if not pipelines_dir.exists():
        typer.echo(f"❌ Directory not found at '{pipelines_dir}'")
        raise typer.Exit(1)

    try:
        result = migrate_concept_syntax(
            directory=pipelines_dir,
            create_backups=backups and not dry_run,
            dry_run=dry_run,
        )

        for error in result.errors:
            typer.echo(f"❌ {error}")

        if result.errors and not result.files_modified:
            typer.echo("❌ Migration failed due to errors")
            raise typer.Exit(1)

        typer.echo(f"Found {result.files_processed} TOML file(s) to check")

        if result.files_modified == 0:
            typer.echo("✅ All TOML files are already using the new syntax")
            return

        if dry_run:
            migrator = TomlMigrator()
            for file_path in result.modified_files:
                try:
                    with open(file_path, "r", encoding="utf-8") as f:
                        content = f.read()

                    changes = migrator.get_migration_preview(content)
                    typer.echo(f"\n📄 {file_path.relative_to(pipelines_dir)}:")
                    for change in changes:
                        typer.echo(f"  Line {change['line_number']}: {change['old_line']} → {change['new_line']}")
                except Exception as exc:
                    typer.echo(f"❌ Error reading {file_path}: {exc}")

            typer.echo(f"\n📋 Summary: Found {result.total_changes} change(s) in {result.files_modified} file(s)")
            typer.echo("   Run without --dry-run to apply these changes")
        else:
            create_backups = backups and not dry_run
            for file_path in result.modified_files:
                typer.echo(f"✅ Migrated {file_path.relative_to(pipelines_dir)}")
                if create_backups:
                    backup_path = file_path.with_suffix(".toml.backup")
                    typer.echo(f"   Backup saved to {backup_path.name}")

            typer.echo(f"\n✅ Migration completed: {result.total_changes} change(s) applied to {result.files_modified} file(s)")
            if create_backups:
                typer.echo("   Backup files created with .backup extension")
            typer.echo("   Run 'pipelex validate all' to verify the migration")
    except FileNotFoundError as exc:
        typer.echo(f"❌ {exc}")
        raise typer.Exit(1)
    except Exception as exc:
        typer.echo(f"❌ Migration failed: {exc}")
        raise typer.Exit(1)


# Typer group for migration commands
migrate_app = typer.Typer(help="Migration commands")


@migrate_app.command("run")
def migrate_cmd(
    relative_config_folder_path: Annotated[
        str, typer.Option("--config-folder-path", "-c", help="Relative path to the config folder path")
    ] = "./pipelex_libraries",
    dry_run: Annotated[bool, typer.Option("--dry-run", help="Preview changes without applying them")] = False,
    backups: Annotated[bool, typer.Option("--backups/--no-backups", help="Create backup files before migration")] = True,
) -> None:
    do_migrate(relative_config_folder_path=relative_config_folder_path, dry_run=dry_run, backups=backups)
