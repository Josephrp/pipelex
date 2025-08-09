from pipelex.tools.misc.file_utils import load_text_from_path


def get_pipeline_creation_rules() -> str:
    return load_text_from_path(".pipelex/design_pipelines.md")
