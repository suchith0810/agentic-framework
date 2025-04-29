# # agent_framework/tools/file_reader_tool.py
# from langchain.tools import Tool
#
# def get_file_reader_tool():
#     """Create and return the file reader tool."""
#     def file_reader(filepath: str) -> str:
#         try:
#             with open(filepath, 'r') as f:
#                 return f.read()
#         except Exception as e:
#             return f"Error reading file: {str(e)}"
#
#     return Tool(
#         name="FileReader",
#         func=file_reader,
#         description="Reads content from a specified file"
#     )


# agent_framework/tools/file_reader_tool.py
"""
File Reader Tool Module
Provides functionality for reading and processing files of various formats.

Features:
- File content reading
- Multiple file format support
- Error handling
- File validation
- Optional content processing

Usage:
    from agent_framework.tools import get_file_reader_tool
    reader = get_file_reader_tool()
    content = reader.run("path/to/file.txt")
"""

from langchain.tools import Tool
from typing import Optional, Dict, List, Any
import os
import logging
from pathlib import Path
import json
import yaml
import csv

# Configure logging
logger = logging.getLogger(__name__)

# Supported file formats and their handlers
SUPPORTED_FORMATS = {
    '.txt': 'text',
    '.json': 'json',
    '.yaml': 'yaml',
    '.yml': 'yaml',
    '.csv': 'csv',
    '.md': 'text',
    '.log': 'text'
}


class FileReader:
    def __init__(self,
                 base_path: Optional[str] = None,
                 max_size: int = 10 * 1024 * 1024):  # 10MB default
        """
        Initialize FileReader.

        Args:
            base_path (Optional[str]): Base directory for file operations
            max_size (int): Maximum file size in bytes (default: 10MB)
        """
        self.base_path = base_path or os.getcwd()
        self.max_size = max_size
        logger.info(f"FileReader initialized with base_path: {self.base_path}, max_size: {self.max_size}")

    def validate_file(self, filepath: str) -> tuple[bool, str]:
        """
        Validate file before reading.

        Args:
            filepath (str): Path to file

        Returns:
            tuple[bool, str]: (is_valid, error_message)
        """
        try:
            path = Path(filepath)

            # Check if file exists
            if not path.exists():
                return False, f"File not found: {filepath}"

            # Check file size
            if path.stat().st_size > self.max_size:
                return False, f"File too large: {path.stat().st_size} bytes"

            return True, ""

        except Exception as e:
            return False, f"Validation error: {str(e)}"

    def read_file(self, filepath: str) -> Dict[str, Any]:
        """
        Read and process file content.

        Args:
            filepath (str): Path to file

        Returns:
            Dict[str, Any]: Dictionary containing file content and metadata
        """
        try:
            # Validate file
            is_valid, error = self.validate_file(filepath)
            if not is_valid:
                raise ValueError(error)

            path = Path(filepath)
            file_format = SUPPORTED_FORMATS.get(path.suffix, 'text')  # Default to 'text' for unsupported formats

            # Read file based on format
            try:
                if file_format == 'json':
                    with open(filepath, 'r') as f:
                        content = json.load(f)
                elif file_format == 'yaml':
                    with open(filepath, 'r') as f:
                        content = yaml.safe_load(f)
                elif file_format == 'csv':
                    with open(filepath, 'r') as f:
                        reader = csv.DictReader(f)
                        content = list(reader)
                else:  # Default text reading for unsupported formats
                    with open(filepath, 'r') as f:
                        content = f.read()
            except (json.JSONDecodeError, yaml.YAMLError, csv.Error) as e:
                # If parsing fails, fall back to text reading
                logger.warning(f"Failed to parse {file_format} file, falling back to text reading: {str(e)}")
                with open(filepath, 'r') as f:
                    content = f.read()
                file_format = 'text'

            # Return content with metadata
            return {
                'content': content,
                'format': file_format,
                'size': path.stat().st_size,
                'modified': path.stat().st_mtime,
                'success': True
            }

        except Exception as e:
            logger.error(f"Error reading file {filepath}: {str(e)}")
            return {
                'content': None,
                'error': str(e),
                'success': False
            }

def get_file_reader_tool(
        base_path: Optional[str] = None,
        max_size: Optional[int] = None,
        custom_description: Optional[str] = None
) -> Tool:
    """
    Create and return the file reader tool.

    Args:
        base_path (Optional[str]): Base directory for file operations
        max_size (Optional[int]): Maximum file size in bytes
        custom_description (Optional[str]): Custom tool description

    Returns:
        Tool: Configured file reader tool
    """
    # Initialize file reader
    reader = FileReader(
        base_path=base_path,
        max_size=max_size if max_size is not None else 10 * 1024 * 1024  # Default 10MB
    )

    def file_reader(filepath: str) -> str:
        """
        Read file content with error handling.

        Args:
            filepath (str): Path to file

        Returns:
            str: File content or error message
        """
        try:
            result = reader.read_file(filepath)

            if not result['success']:
                return f"Error reading file: {result['error']}"

            # Format content based on file type
            content = result['content']
            if isinstance(content, (dict, list)):
                return json.dumps(content, indent=2)
            return str(content)

        except Exception as e:
            logger.error(f"Error in file reader tool: {str(e)}")
            return f"Error reading file: {str(e)}"

    # Default tool description
    default_description = (
        "Reads content from specified files. "
        f"Supports special handling for: {', '.join(SUPPORTED_FORMATS.keys())}. "
        "Other file types will be read as text. "
        f"Maximum file size: {max_size or '10MB'}"
    )

    return Tool(
        name="FileReader",
        func=file_reader,
        description=custom_description or default_description
    )




# Optional Extensions:

# def get_advanced_file_reader_tool(
#         base_path: Optional[str] = None,
#         **kwargs
# ) -> Tool:
#     """
#     Create advanced file reader with additional features.
#
#     Features:
#     - Content summarization
#     - Format conversion
#     - Content filtering
#     """
#     reader = FileReader(base_path=base_path)
#
#     def advanced_reader(filepath: str, **options) -> Dict[str, Any]:
#         """Advanced file reading with options."""
#         result = reader.read_file(filepath)
#
#         if options.get('summarize'):
#             # Add summarization logic
#             pass
#
#         if options.get('format'):
#             # Add format conversion logic
#             pass
#
#         return result
#
#     return Tool(
#         name="AdvancedFileReader",
#         func=advanced_reader,
#         description="Advanced file reader with summarization and conversion options"
#     )
#
#
# # Utility Functions
#
# def is_binary_file(filepath: str) -> bool:
#     """Check if file is binary."""
#     pass
#
#
# def get_file_metadata(filepath: str) -> Dict[str, Any]:
#     """Get detailed file metadata."""
#     pass
#
#
# def sanitize_filepath(filepath: str) -> str:
#     """Sanitize file path for security."""
#     pass