# agent_framework/tools/__init__.py

"""
Tools Package Initialization
==========================

Central module for managing and exposing all available tools in the agent framework.
Provides standardized access to various tool implementations and their configuration.

Available Tools:
--------------
1. Calculator: Basic and advanced mathematical operations
2. File Reader: File content reading and processing
3. Wikipedia: Online information retrieval
4. LLM Math: Language model-based mathematics
5. File Writer: File creation and modification
6. Filesystem Tools: Directory and file operations

Tool Categories:
--------------
- Mathematical: calculator_tool, llm_math_tool
- File Operations: file_reader_tool, file_writer_tool, filesystem_tools
- Information Retrieval: wikipedia_tool

Usage:
------
Basic tool access:
    >>> from agent_framework.tools import get_all_tools
    >>> tools = get_all_tools(llm)

Specific tool access:
    >>> from agent_framework.tools import get_calculator_tool
    >>> calc_tool = get_calculator_tool(llm)

Example with multiple tools:
    >>> from agent_framework.tools import (
    ...     get_calculator_tool,
    ...     get_file_reader_tool,
    ...     get_wikipedia_tool
    ... )
"""

from .get_tools import get_all_tools
from .calculator_tool import get_calculator_tool
from .file_reader_tool import get_file_reader_tool
from .wikipedia_tool import get_wikipedia_tool
from .llm_math_tool import get_llm_math_tool
from .file_writer_tool import get_file_writer_tool

# Export all tool getter functions
__all__ = [
    'get_all_tools',  # Get all available tools
    'get_calculator_tool',  # Basic calculations
    'get_file_reader_tool',  # File reading operations
    'get_wikipedia_tool',  # Wikipedia searches
    'get_llm_math_tool',  # Advanced math operations
    'get_file_writer_tool',  # File writing operations
    'get_filesystem_tools'  # Filesystem operations
]

"""
Tool Extension Guide:
===================

1. Creating a New Tool:
---------------------
a. Create new tool file (e.g., new_tool.py)
b. Implement tool functionality
c. Create getter function
d. Add imports and exports here

Example:
    # new_tool.py
    from langchain.tools import Tool

    def get_new_tool(llm=None):
        def tool_func(input_str: str) -> str:
            # Tool implementation
            return result

        return Tool(
            name="NewTool",
            func=tool_func,
            description="Tool description"
        )

2. Tool Categories:
-----------------
TOOL_CATEGORIES = {
    'math': [
        'calculator_tool',
        'llm_math_tool'
    ],
    'information': [
        'wikipedia_tool'
    ],
    'file_operations': [
        'file_reader_tool',
        'file_writer_tool',
        'filesystem_tools'
    ]
}

3. Tool Dependencies:
------------------
TOOL_DEPENDENCIES = {
    'calculator_tool': [],
    'llm_math_tool': ['llm'],
    'wikipedia_tool': ['requests'],
    'file_reader_tool': [],
    'file_writer_tool': [],
    'filesystem_tools': []
}

4. Tool Configuration:
-------------------
TOOL_CONFIG = {
    'calculator_tool': {
        'enabled': True,
        'requires_llm': False
    },
    'llm_math_tool': {
        'enabled': True,
        'requires_llm': True
    },
    'wikipedia_tool': {
        'enabled': True,
        'requires_llm': False
    }
}

Utility Functions:
----------------
def get_tools_by_category(category: str) -> List[Tool]:
    '''
    Get all tools in a specific category.

    Args:
        category (str): Category name

    Returns:
        List[Tool]: List of tools in the category
    '''
    tool_names = TOOL_CATEGORIES.get(category, [])
    return [globals()[f"get_{name}"] for name in tool_names]

def check_tool_dependencies():
    '''
    Check if all required dependencies for tools are installed.

    Returns:
        dict: Missing dependencies by tool
    '''
    # Implementation
    pass

def get_enabled_tools():
    '''
    Get list of currently enabled tools.

    Returns:
        list: Names of enabled tools
    '''
    return [tool for tool, config in TOOL_CONFIG.items()
            if config['enabled']]

Best Practices:
-------------
1. Tool Implementation:
   - Clear documentation
   - Error handling
   - Input validation
   - Resource cleanup

2. Tool Integration:
   - Consistent interface
   - Proper error reporting
   - Resource management
   - Performance consideration

3. Security:
   - Input sanitization
   - Permission checks
   - Resource limitations
   - Secure operations
"""

# Optional: Package metadata and versioning
__version__ = '0.1.0'
__author__ = 'Netanel Miller'
__description__ = 'Tool collection for AI agent framework'

# Note: Additional utility functions and configurations can be added as neede
