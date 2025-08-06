from pathlib import Path
from typing import Any, Dict, List, Optional, Union

from pydantic import BaseModel, Field

from pipelex.core.concept_factory import ConceptBlueprint
from pipelex.exceptions import LibraryError
from pipelex.tools.misc.toml_utils import dict_to_toml_string, save_toml_to_path


class PipelineBlueprintValidationError(LibraryError):
    """Error raised when a pipeline blueprint fails validation."""

    def __init__(self, file_path: str, validation_error_msg: str):
        self.file_path = file_path
        self.validation_error_msg = validation_error_msg
        super().__init__(f"Pipeline blueprint validation failed for '{file_path}': {validation_error_msg}")


class ConceptBlueprintError(LibraryError):
    """Error raised when loading concept blueprints."""

    def __init__(self, file_path: str, concept_name: str, error_msg: str):
        self.file_path = file_path
        self.concept_name = concept_name
        super().__init__(f"Error loading concept '{concept_name}' from '{file_path}': {error_msg}")


class PipeBlueprintError(LibraryError):
    """Error raised when loading pipe blueprints."""

    def __init__(self, file_path: str, pipe_name: str, error_msg: str):
        self.file_path = file_path
        self.pipe_name = pipe_name
        super().__init__(f"Error loading pipe '{pipe_name}' from '{file_path}': {error_msg}")


class PipeStepBlueprint(BaseModel):
    """Blueprint of a step in a pipe sequence."""

    pipe: str
    result: str


class PipelineLibraryBlueprint(BaseModel):
    """Complete blueprint of a pipeline library TOML file."""

    # Domain information (required)
    domain: str
    definition: Optional[str] = None
    system_prompt: Optional[str] = None
    system_prompt_to_structure: Optional[str] = None
    prompt_template_to_structure: Optional[str] = None

    # Concepts section - concept_name -> definition (string) or blueprint (dict)
    concept: Dict[str, Union[str, ConceptBlueprint]] = Field(default_factory=dict)

    # Pipes section - pipe_name -> blueprint dict
    pipe: Dict[str, Dict[str, Any]] = Field(default_factory=dict)

    def to_toml_dict(self) -> Dict[str, Any]:
        """Convert blueprint back to TOML-compatible dictionary structure."""
        result: Dict[str, Any] = {"domain": self.domain}

        # Add optional domain-level fields
        if self.definition:
            result["definition"] = self.definition
        if self.system_prompt:
            result["system_prompt"] = self.system_prompt
        if self.system_prompt_to_structure:
            result["system_prompt_to_structure"] = self.system_prompt_to_structure
        if self.prompt_template_to_structure:
            result["prompt_template_to_structure"] = self.prompt_template_to_structure

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
