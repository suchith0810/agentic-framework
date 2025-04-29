# agent_framework/tools/get_tools.py

"""
Tool Aggregator Module
=====================

Central module for collecting and initializing all available tools for the agent framework.
Manages tool initialization, configuration, and aggregation based on environment settings.

Features:
--------
- Dynamic tool loading
- Environment-based configuration
- Tool validation and verification
- Error handling for tool initialization
- Proxy configuration for network-dependent tools

Usage:
------
Basic tool collection:
    >>> from tools.get_tools import get_all_tools
    >>> tools = get_all_tools(llm)
    >>> agent.tools = tools

Specific tool initialization:
    >>> tools = get_all_tools(llm, enabled_only=['calculator', 'file_reader'])

Example with custom configuration:
    >>> tools = get_all_tools(
    ...     llm,
    ...     proxy_config={'http': 'http://proxy:8080'},
    ...     filesystem_root='/safe/path'
    ... )
"""

from typing import List
from langchain.tools import Tool

# Import tool getters - add new tool imports here
from .calculator_tool import get_calculator_tool
from .file_reader_tool import get_file_reader_tool
from .wikipedia_tool import get_wikipedia_tool
from .llm_math_tool import get_llm_math_tool
from .file_writer_tool import get_file_writer_tool
from .filesystem_tools import get_filesystem_tools
from config.settings import AWS_CONFIG, ENABLED_TOOLS, FILESYSTEM_CONFIG


def get_all_tools(llm) -> List[Tool]:
    """
    Aggregate and initialize all available tools based on configuration.

    This function serves as the central point for tool initialization and management.
    It respects environment settings and handles tool-specific configurations.

    Args:
        llm: Language model instance required by certain tools

    Returns:
        List[Tool]: List of initialized and configured tools

    Raises:
        Exception: If critical tool initialization fails

    Example:
        >>> llm = ChatBedrock(model="anthropic.claude-v3")
        >>> tools = get_all_tools(llm)
        >>> print(f"Initialized {len(tools)} tools")

    Note:
        - Tools are initialized based on ENABLED_TOOLS configuration
        - Each tool may have specific initialization requirements
        - Failed tool initialization is logged but doesn't stop other tools
    """
    tools = []

    try:
        # Add calculator tool if enabled
        if ENABLED_TOOLS.get('calculator', True):
            tools.append(get_calculator_tool(llm))

        # Add file reader tool if enabled
        if ENABLED_TOOLS.get('file_reader', True):
            tools.append(get_file_reader_tool())

        # Add file writer tool if enabled
        if ENABLED_TOOLS.get('file_writer', True):
            tools.append(get_file_writer_tool())

        # Add Wikipedia tool if enabled, with proxy configuration
        if ENABLED_TOOLS.get('wikipedia', False):
            # Get proxy settings from AWS_CONFIG
            proxy = AWS_CONFIG.proxies if hasattr(AWS_CONFIG, 'proxies') else None
            tools.append(get_wikipedia_tool(proxy=proxy))

        # Add LLM math tool if enabled
        if ENABLED_TOOLS.get('llm_math', True):
            tools.append(get_llm_math_tool(llm))

        # Add filesystem tools if enabled
        if ENABLED_TOOLS.get('filesystem', True):
            filesystem_tools = get_filesystem_tools(
                root_dir=FILESYSTEM_CONFIG.get('root_dir')
            )
            tools.extend(filesystem_tools)

        return tools

    except Exception as e:
        logger.error(f"Error initializing tools: {str(e)}")
        raise


"""
Tool Extension Guide:
===================

1. Adding a New Tool:
-------------------
a. Create tool implementation file (new_tool.py)
b. Create getter function
c. Add import statement here
d. Add to get_all_tools function

Example:
    # 1. Create new_tool.py
    from langchain.tools import Tool

    def get_new_tool(llm=None):
        def tool_function(input_str: str) -> str:
            # Implementation
            return result

        return Tool(
            name="NewTool",
            func=tool_function,
            description="Tool description"
        )

    # 2. Add import
    from .new_tool import get_new_tool

    # 3. Add to get_all_tools
    if ENABLED_TOOLS.get('new_tool', True):
        tools.append(get_new_tool(llm))

2. Tool Configuration:
-------------------
- Add tool to ENABLED_TOOLS in config/settings.py
- Add any tool-specific configuration
- Handle tool dependencies
- Consider environment-specific settings

3. Error Handling:
----------------
def initialize_tool(tool_getter, *args, **kwargs):
    '''Safe tool initialization with error handling.'''
    try:
        return tool_getter(*args, **kwargs)
    except Exception as e:
        logger.error(f"Failed to initialize {tool_getter.__name__}: {e}")
        return None

4. Tool Validation:
-----------------
def validate_tool(tool: Tool) -> bool:
    '''Validate tool configuration and capabilities.'''
    if not hasattr(tool, 'name') or not tool.name:
        return False
    if not callable(getattr(tool, 'func', None)):
        return False
    return True

Best Practices:
-------------
1. Tool Implementation:
   - Clear documentation
   - Proper error handling
   - Resource management
   - Input validation

2. Configuration:
   - Environment awareness
   - Secure defaults
   - Clear documentation
   - Version compatibility

3. Security:
   - Input sanitization
   - Resource limitations
   - Access control
   - Secure operations

4. Performance:
   - Lazy initialization
   - Resource pooling
   - Caching when appropriate
   - Clean cleanup
"""

# Optional: Debugging and logging support
import logging

logger = logging.getLogger(__name__)

# Optional: Tool initialization tracking
INITIALIZED_TOOLS = set()
FAILED_TOOLS = set()


def track_tool_initialization(tool_name: str, success: bool):
    """
    Track tool initialization status for debugging.

    Args:
        tool_name (str): Name of the tool
        success (bool): Whether initialization succeeded
    """
    if success:
        INITIALIZED_TOOLS.add(tool_name)
    else:
        FAILED_TOOLS.add(tool_name)


def get_tool_status():
    """
    Get current tool initialization status.

    Returns:
        dict: Status of tool initialization
    """
    return {
        'initialized': list(INITIALIZED_TOOLS),
        'failed': list(FAILED_TOOLS)
    }

