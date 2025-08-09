from pathlib import Path
from typing import Any, Dict, Union

from pydantic import Field

from pipelex.core.stuff_content import StructuredContent
from pipelex.tools.misc.toml_utils import dict_to_toml_string, save_toml_to_path


class PipeDraft(StructuredContent):
    code: str
    type: str
    definition: str
    inputs: Dict[str, str]
    output: str


class PipelineDraft(StructuredContent):
    """Complete blueprint of a pipeline library TOML file."""

    # Domain information (required)
    domain: str
    definition: str

    # Concepts section - concept_name -> definition (string) or blueprint (dict)
    concept: Dict[str, str] = Field(default_factory=dict)

    # Pipes section - pipe_name -> blueprint dict
    pipe: Dict[str, PipeDraft] = Field(default_factory=dict)

    def to_toml_dict(self) -> Dict[str, Any]:
        """Convert blueprint back to TOML-compatible dictionary structure."""
        result: Dict[str, Any] = {"domain": self.domain}

        # Add optional domain-level fields
        if self.definition:
            result["definition"] = self.definition

        # Add concepts section if not empty
        if self.concept:
            result["concept"] = self.concept

        # Add pipes section if not empty
        if self.pipe:
            result["pipe"] = self.pipe

        return result

    def to_toml_string(self) -> str:
        """Convert blueprint to TOML string format."""
        return dict_to_toml_string(self.to_toml_dict())

    def save_to_file(self, file_path: Union[str, Path]) -> None:
        """Save blueprint to a TOML file."""
        path = Path(file_path)
        path.parent.mkdir(parents=True, exist_ok=True)
        save_toml_to_path(data=self.to_toml_dict(), path=str(path))
