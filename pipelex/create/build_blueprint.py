from __future__ import annotations

from typing import Optional

from pipelex import log, pretty_print
from pipelex.create.helpers import get_support_file
from pipelex.create.pipeline_toml import save_pipeline_blueprint_toml_to_path
from pipelex.create.validate_blueprint import load_pipes_from_generated_blueprint, validate_blueprint
from pipelex.libraries.pipeline_blueprint import PipelineBlueprint
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
    output_path_base = output_path or "pipelex/libraries/pipelines/temp/gen_blueprint"
    draft_path = f"{output_path_base}_draft.md"
    save_text_to_path(text=pipeline_draft, path=draft_path)
    rough_toml_path = f"{output_path_base}_rough.toml"
    save_pipeline_blueprint_toml_to_path(blueprint=blueprint, path=rough_toml_path)
    rough_json_path = f"{output_path_base}_rough.json"
    save_as_json_to_path(object_to_save=blueprint, path=rough_json_path)
    log.info(f"✅ Rough blueprint saved to '{output_path_base}'")

    load_pipes_from_generated_blueprint(blueprint=blueprint)
    log.info("✅ Pipes loaded from blueprint")

    if validate:
        await validate_blueprint(blueprint=blueprint, is_error_fixing_enabled=True)
        fixed_toml_path = f"{output_path_base}_fixed.toml"
        save_pipeline_blueprint_toml_to_path(blueprint=blueprint, path=fixed_toml_path)
        fixed_json_path = f"{output_path_base}_fixed.json"
        save_as_json_to_path(object_to_save=blueprint, path=fixed_json_path)
        log.info(f"✅ Fixed blueprint saved to '{output_path_base}'")
