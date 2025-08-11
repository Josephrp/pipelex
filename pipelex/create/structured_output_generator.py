"""Generate Pydantic BaseModel classes from TOML definitions for structured outputs."""

from __future__ import annotations

import textwrap
from typing import Any, ClassVar, Dict, List, Optional, Union

import tomlkit

from pipelex.core.stuff_content import StructuredContent
from pipelex.types import StrEnum


class FieldType(StrEnum):
    """Supported field types for structured outputs."""
    TEXT = "text"
    NUMBER = "number"
    INTEGER = "integer"
    BOOLEAN = "boolean"
    LIST = "list"
    DICT = "dict"


class StructuredOutputGenerator:
    """Generate Pydantic BaseModel classes from TOML structured output definitions."""
    
    # Map high-level type names to Python types
    TYPE_MAPPING: ClassVar[Dict[FieldType, str]] = {
        FieldType.TEXT: "str",
        FieldType.NUMBER: "float",
        FieldType.INTEGER: "int",
        FieldType.BOOLEAN: "bool",
        FieldType.LIST: "List",
        FieldType.DICT: "Dict",
    }

    def __init__(self):
        self.imports = {
            "from typing import Optional, List, Dict, Any",
            "from pipelex.core.stuff_content import StructuredContent",
            "from pydantic import Field",
        }

    def generate_from_toml(self, toml_content: str) -> str:
        """Generate Python module content from TOML structured output definitions.
        
        Args:
            toml_content: TOML content containing schema definitions
            
        Returns:
            Generated Python module content
        """
        data = tomlkit.parse(toml_content)
        
        if "schema" not in data:
            raise ValueError("TOML must contain a 'schema' section")
        
        schemas = data["schema"]
        classes: List[str] = []
        
        for class_name, schema_def in schemas.items():  # type: ignore[attr-defined,union-attr]
            class_code = self._generate_class(str(class_name), dict(schema_def))  # type: ignore[arg-type]
            classes.append(class_code)
        
        # Generate the complete module
        imports_section = "\n".join(sorted(self.imports))
        classes_section = "\n\n\n".join(classes)
        
        return f"{imports_section}\n\n\n{classes_section}\n"

    def _generate_class(self, class_name: str, schema_def: Dict[str, Any]) -> str:
        """Generate a single class definition.
        
        Args:
            class_name: Name of the class
            schema_def: Schema definition from TOML
            
        Returns:
            Generated class code
        """
        definition = schema_def.get("definition", f"Generated {class_name} class")
        fields = schema_def.get("fields", {})
        
        # Generate class header
        class_header = f'class {class_name}(StructuredContent):\n    """{definition}"""\n'
        
        # Generate fields
        field_definitions: List[str] = []
        for field_name, field_def in fields.items():
            field_code = self._generate_field(str(field_name), field_def)  # type: ignore[arg-type]
            field_definitions.append(field_code)
        
        if not field_definitions:
            # Empty class with just pass
            return class_header + "\n    pass"
        
        fields_code = "\n".join(field_definitions)
        return class_header + "\n" + fields_code

    def _generate_field(self, field_name: str, field_def: Union[Dict[str, Any], str]) -> str:
        """Generate a single field definition.
        
        Args:
            field_name: Name of the field
            field_def: Field definition (dict or string for simple types)
            
        Returns:
            Generated field code
        """
        # Handle simple string definitions (just the definition text)
        if isinstance(field_def, str):
            field_def = {"type": FieldType.TEXT, "definition": field_def}
        
        field_type = field_def.get("type", FieldType.TEXT)
        definition = field_def.get("definition", f"{field_name} field")
        required = field_def.get("required", False)
        default_value = field_def.get("default")
        
        # Handle complex types
        python_type = self._get_python_type(field_type, field_def)
        
        # Make optional if not required
        if not required:
            python_type = f"Optional[{python_type}]"
        
        # Generate Field parameters
        field_params = [f'description="{definition}"']
        
        if required:
            if default_value is not None:
                field_params.insert(0, f'default={repr(default_value)}')
            else:
                field_params.insert(0, "...")
        else:
            if default_value is not None:
                field_params.insert(0, f'default={repr(default_value)}')
            else:
                field_params.insert(0, "default=None")
        
        field_call = f"Field({', '.join(field_params)})"
        
        return f"    {field_name}: {python_type} = {field_call}"

    def _get_python_type(self, field_type: Any, field_def: Dict[str, Any]) -> str:
        """Convert high-level type to Python type annotation.
        
        Args:
            field_type: High-level type name or FieldType enum
            field_def: Complete field definition
            
        Returns:
            Python type annotation string
        """
        # Convert string to FieldType if needed
        if isinstance(field_type, str):
            try:
                field_type_enum = FieldType(field_type)
            except ValueError:
                # Unknown type, assume it's a custom type or class reference
                return field_type
            field_type = field_type_enum
        
        # Use match/case for type handling
        match field_type:
            case FieldType.TEXT:
                return "str"
            case FieldType.NUMBER:
                return "float"
            case FieldType.INTEGER:
                return "int"
            case FieldType.BOOLEAN:
                return "bool"
            case FieldType.LIST:
                item_type = field_def.get("item_type", "Any")
                # Recursively handle item types
                if isinstance(item_type, str):
                    try:
                        item_type_enum = FieldType(item_type)
                        item_type = self._get_python_type(item_type_enum, {})
                    except ValueError:
                        # Keep as string if not a known FieldType
                        pass
                return f"List[{item_type}]"
            case FieldType.DICT:
                key_type = field_def.get("key_type", "str")
                value_type = field_def.get("value_type", "Any")
                # Recursively handle key and value types
                if isinstance(key_type, str):
                    try:
                        key_type_enum = FieldType(key_type)
                        key_type = self._get_python_type(key_type_enum, {})
                    except ValueError:
                        pass
                if isinstance(value_type, str):
                    try:
                        value_type_enum = FieldType(value_type)
                        value_type = self._get_python_type(value_type_enum, {})
                    except ValueError:
                        pass
                return f"Dict[{key_type}, {value_type}]"
            case _:
                # Unknown FieldType, assume it's a custom type
                return str(field_type)


def generate_structured_outputs_from_toml_file(toml_file_path: str, output_file_path: str) -> None:
    """Generate structured output Python module from TOML file.
    
    Args:
        toml_file_path: Path to input TOML file
        output_file_path: Path to output Python file
    """
    with open(toml_file_path, "r", encoding="utf-8") as f:
        toml_content = f.read()
    
    generator = StructuredOutputGenerator()
    python_code = generator.generate_from_toml(toml_content)
    
    with open(output_file_path, "w", encoding="utf-8") as f:
        f.write(python_code)


def generate_structured_outputs_from_toml_string(toml_content: str) -> str:
    """Generate structured output Python code from TOML string.
    
    Args:
        toml_content: TOML content as string
        
    Returns:
        Generated Python module content
    """
    generator = StructuredOutputGenerator()
    return generator.generate_from_toml(toml_content)