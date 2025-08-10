from __future__ import annotations

from typing import Any, Dict, List, Mapping, Optional, cast

import tomlkit
from tomlkit import array, document, inline_table, table
from tomlkit import string as tk_string

from pipelex.libraries.pipeline_blueprint import PipelineLibraryBlueprint
from pipelex.tools.misc.file_utils import save_text_to_path
from pipelex.tools.misc.json_utils import remove_none_values_from_dict
from pipelex.tools.misc.toml_utils import clean_trailing_whitespace


def make_toml_string(text: str, prefer_literal: bool = False, force_multiline: bool = False):
    """Return a tomlkit String configured for triple quotes when appropriate."""
    needs_multiline = force_multiline or ("\n" in text)
    # Prefer literal '''...''' when you do not want escapes, as long as it
    # does not contain a triple single-quote sequence (which would be invalid).
    use_literal = prefer_literal and ("'''" not in text)
    return tk_string(text, multiline=needs_multiline, literal=use_literal)


def _convert_to_inline(value: Any):
    """Recursively convert Python values; dicts -> inline tables; lists kept as arrays."""
    if isinstance(value, Mapping):
        value = cast(Mapping[str, Any], value)
        inline_table_obj = inline_table()
        for key, value_item in value.items():
            inline_table_obj[key] = _convert_to_inline(value_item)
        return inline_table_obj

    if isinstance(value, list):
        value = cast(List[Any], value)
        array_obj = array()
        array_obj.multiline(True)  # set to False for single-line arrays
        for element in value:
            if isinstance(element, Mapping):
                element = cast(Mapping[str, Any], element)
                inline_element = inline_table()
                for inner_key, inner_value in element.items():
                    inline_element[inner_key] = _convert_to_inline(inner_value)
                array_obj.append(inline_element)  # pyright: ignore[reportUnknownMemberType]
            else:
                array_obj.append(_convert_to_inline(element))  # pyright: ignore[reportUnknownMemberType]
        return array_obj

    if isinstance(value, str):
        # Emit """...""" when there are newlines; flip prefer_literal=True to get '''...'''.
        return make_toml_string(value, prefer_literal=False)

    return value


def dict_to_toml(data: Mapping[str, Any]) -> str:
    """Top-level keys become tables; nested dicts become inline tables."""
    data = remove_none_values_from_dict(data=data)
    document_root = document()
    for section_key, section_value in data.items():
        if isinstance(section_value, Mapping):
            section_value = cast(Mapping[str, Any], section_value)
            table_obj = table()
            for field_key, field_value in section_value.items():
                table_obj.add(field_key, _convert_to_inline(field_value))
            document_root.add(section_key, table_obj)  # `[section_key]` section
        else:
            document_root.add(section_key, _convert_to_inline(section_value))
    dumped_content = tomlkit.dumps(document_root)  # pyright: ignore[reportUnknownMemberType]
    return dumped_content


def pipeline_blueprint_to_toml(blueprint: PipelineLibraryBlueprint) -> str:
    blueprint_dict = blueprint.smart_dump()
    return dict_to_toml(data=blueprint_dict)


def save_toml_to_path(data: Dict[str, Any], path: str) -> None:
    """Save dictionary as TOML to file path.

    Args:
        data: Dictionary to save as TOML
        path: Path where to save the TOML file
    """
    # data_cleaned = remove_none_values_from_dict(data=data)
    data_cleaned = data
    with open(path, "w", encoding="utf-8") as file:
        toml_content: str = dict_to_toml(data=data_cleaned)
        cleaned_content = clean_trailing_whitespace(toml_content)
        file.write(cleaned_content)


def save_pipeline_blueprint_toml_to_path(blueprint: PipelineLibraryBlueprint, path: str) -> None:
    pipeline_blueprint_toml = pipeline_blueprint_to_toml(blueprint=blueprint)
    save_text_to_path(text=pipeline_blueprint_toml, path=path)
