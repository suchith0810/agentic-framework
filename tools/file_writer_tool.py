# agent_framework/tools/file_writer_tool.py

"""
File Writer Tool Module
Provides functionality for writing and modifying files with various operations.
"""

from langchain.tools import BaseTool
from pydantic import BaseModel, Field
from typing import Dict, Any, Union, List, Optional, Literal, Type
import os
import logging
from pathlib import Path
import tempfile
import shutil
import re
import json

# Configure logging
logger = logging.getLogger(__name__)


class FileWriterInput(BaseModel):
    """Schema for FileWriter input"""
    query: str = Field(
        description="""JSON string containing operation details. Example:
        {
            "operation": "insert",
            "target_file": "/path/to/file.txt",
            "insert_position": "end",
            "insert_string": "new content"
        }""")


class FileWriter:
    """File writing operations handler."""

    def __init__(self, base_path: str = None):
        """Initialize FileWriter."""
        self.base_path = base_path or os.getcwd()

    def validate_file(self, filepath: str) -> tuple[bool, str]:
        """Validate file before operations."""
        try:
            path = Path(filepath)

            # Check if directory exists
            if not path.parent.exists():
                return False, f"Directory not found: {path.parent}"

            # Check if file exists
            if not path.exists():
                # For new files, check if directory is writable
                if not os.access(path.parent, os.W_OK):
                    return False, f"Directory not writable: {path.parent}"
            else:
                # For existing files, check if file is writable
                if not os.access(path, os.W_OK):
                    return False, f"File not writable: {filepath}"

            return True, ""
        except Exception as e:
            return False, f"Validation error: {str(e)}"

    def modify_block(self, filepath: str, start_line: int, end_line: int, content: str) -> Dict[str, Any]:
        """Modify a block of lines in the file."""
        try:
            is_valid, error = self.validate_file(filepath)
            if not is_valid:
                raise ValueError(error)

            # Create file if it doesn't exist
            if not os.path.exists(filepath):
                with open(filepath, 'w') as f:
                    f.write('\n' * (start_line - 1))
                lines = [''] * (start_line - 1)
            else:
                # Read existing content
                with open(filepath, 'r') as f:
                    lines = f.readlines()

            # Validate line numbers
            if start_line < 1:
                raise ValueError(f"Invalid start line: {start_line}")

            # Extend file if end_line is beyond current length
            while len(lines) < end_line:
                lines.append('\n')

            # Prepare new content
            new_content = content.split('\n')
            if not new_content[-1].endswith('\n'):
                new_content[-1] += '\n'

            # Replace block
            lines[start_line - 1:end_line] = new_content

            # Write back to file
            with open(filepath, 'w') as f:
                f.writelines(lines)

            return {
                'success': True,
                'message': f"Modified lines {start_line}-{end_line}"
            }

        except Exception as e:
            logger.error(f"Error modifying block: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }

    def insert_text(self, filepath: str, position: str, content: str) -> Dict[str, Any]:
        """Insert text at specified position."""
        try:
            is_valid, error = self.validate_file(filepath)
            if not is_valid:
                raise ValueError(error)

            # Create file if it doesn't exist
            if not os.path.exists(filepath):
                existing_content = ""
            else:
                with open(filepath, 'r') as f:
                    existing_content = f.read()

            if position == 'begin':
                new_content = content + existing_content
            elif position == 'end':
                new_content = existing_content + content
            elif position == 'middle':
                mid_point = len(existing_content) // 2
                new_content = existing_content[:mid_point] + content + existing_content[mid_point:]
            else:
                raise ValueError(f"Invalid position: {position}")

            with open(filepath, 'w') as f:
                f.write(new_content)

            return {
                'success': True,
                'message': f"Inserted text at {position}"
            }

        except Exception as e:
            logger.error(f"Error inserting text: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }

    def replace_content(self, filepath: str, pattern: str, replacement: str,
                        use_regex: bool = False) -> Dict[str, Any]:
        """Replace content using sed-like operations."""
        try:
            is_valid, error = self.validate_file(filepath)
            if not is_valid:
                raise ValueError(error)

            if not os.path.exists(filepath):
                return {
                    'success': False,
                    'error': "File does not exist and cannot be created for replacement operation"
                }

            # Create temporary file
            temp_file = tempfile.NamedTemporaryFile(delete=False, mode='w')
            replacements = 0

            with open(filepath, 'r') as f:
                for line in f:
                    if use_regex:
                        new_line, count = re.subn(pattern, replacement, line)
                    else:
                        new_line = line.replace(pattern, replacement)
                        count = (len(line) - len(new_line)) // (len(pattern) - len(replacement)) \
                            if len(pattern) != len(replacement) else 0

                    replacements += count
                    temp_file.write(new_line)

            temp_file.close()

            # Replace original file
            shutil.move(temp_file.name, filepath)

            return {
                'success': True,
                'message': f"Made {replacements} replacements"
            }

        except Exception as e:
            logger.error(f"Error replacing content: {str(e)}")
            if 'temp_file' in locals():
                os.unlink(temp_file.name)
            return {
                'success': False,
                'error': str(e)
            }


class FileWriterTool(BaseTool):
    """Tool for writing and modifying files."""
    name: str = "FileWriter"
    description: str = """Write or modify files with various operations (input should be a JSON string):
    1. modify_block: Replace content between specific lines
    2. insert: Add text at beginning, middle, or end
    3. replace: Replace content using plain text or regex patterns

    Examples:
    For insertion: {"operation": "insert", "target_file": "file.txt", "insert_position": "end", "insert_string": "new text"}
    For block modification: {"operation": "modify_block", "target_file": "file.txt", "start_line": 1, "end_line": 5, "insert_string": "new content"}
    For replacement: {"operation": "replace", "target_file": "file.txt", "pattern": "old", "replacement": "new", "use_regex": false}"""

    return_direct: bool = False
    base_path: Optional[str] = Field(default=None, description="Base path for file operations")
    file_writer: Optional[FileWriter] = Field(default=None, exclude=True)

    class Config:
        """Pydantic config"""
        arbitrary_types_allowed = True
        exclude = ["file_writer"]

    def __init__(self, **data):
        """Initialize the tool with base path."""
        super().__init__(**data)
        self.file_writer = FileWriter(self.base_path or os.getcwd())

    def _run(self, input_str: str) -> str:
        """Execute the file writing operation."""
        try:
            # Parse the input JSON string
            try:
                kwargs = json.loads(input_str)
            except json.JSONDecodeError:
                return "Error: Input must be a valid JSON string"

            operation = kwargs.get('operation', '')
            target_file = kwargs.get('target_file', '')

            if not operation or not target_file:
                return "Error: Missing operation or target_file"

            if operation == 'insert':
                result = self.file_writer.insert_text(
                    target_file,
                    kwargs.get('insert_position', 'end'),
                    kwargs.get('insert_string', '')
                )
            elif operation == 'modify_block':
                if not all([kwargs.get('start_line'), kwargs.get('end_line'), kwargs.get('insert_string')]):
                    return "Error: modify_block requires start_line, end_line, and insert_string"
                result = self.file_writer.modify_block(
                    target_file,
                    kwargs.get('start_line'),
                    kwargs.get('end_line'),
                    kwargs.get('insert_string')
                )
            elif operation == 'replace':
                if not all([kwargs.get('pattern'), kwargs.get('replacement')]):
                    return "Error: replace requires pattern and replacement"
                result = self.file_writer.replace_content(
                    target_file,
                    kwargs.get('pattern'),
                    kwargs.get('replacement'),
                    kwargs.get('use_regex', False)
                )
            else:
                return f"Error: Unknown operation '{operation}'"

            return result['message'] if result['success'] else f"Error: {result['error']}"

        except Exception as e:
            logger.error(f"Error in file writer tool: {str(e)}")
            return f"Error: {str(e)}"

    async def _arun(self, input_str: str) -> str:
        """Async implementation - Not implemented yet."""
        raise NotImplementedError("Async version not implemented")





def get_file_writer_tool(base_path: str = None) -> BaseTool:
    """Create and return the file writer tool."""
    return FileWriterTool(base_path=base_path)