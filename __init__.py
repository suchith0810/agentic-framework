# agent_framework/__init__.py
"""
Agent Framework Package
======================

A comprehensive framework for building and managing AI agents with different LLM backends.
This is the main package initialization file that exposes key components of the framework
to users.

Key Components:
--------------
- BedrockAgent: AWS Bedrock-based conversational agent with memory management
- Additional components can be added through the modular architecture

Features:
---------
- Modular agent architecture
- Configurable memory systems
- Extensible tool integration
- Environment-specific configurations

Usage:
------
Basic usage with Bedrock Agent:
    >>> from agent_framework import BedrockAgent
    >>> agent = BedrockAgent()
    >>> response = agent.run("Hello, how can you help me?")

Advanced usage with custom configuration:
    >>> agent = BedrockAgent(
    ...     model_id="anthropic.claude-3-sonnet-20240229-v1:0",
    ...     verbose=True,
    ...     memory_config={'memory_type': 'summary', 'max_messages': 50}
    ... )

Dependencies:
------------
- langchain
- boto3 (for AWS Bedrock integration)
- Additional dependencies based on enabled tools
"""

from .agents.bedrock_agent import BedrockAgent

# Version of the framework
__version__ = '0.1.0'

# List of public components
__all__ = ['BedrockAgent']

"""
Framework Extension Guide:
========================

1. Adding a New Agent:
---------------------
To add a new agent implementation:
    from .agents.new_agent import NewAgent
    __all__.append('NewAgent')

Example:
    # Adding OpenAI agent
    from .agents.openai_agent import OpenAIAgent
    __all__ = ['BedrockAgent', 'OpenAIAgent']

2. Adding Utility Functions:
--------------------------
To add utility functions:
    from .utils.helpers import utility_function
    __all__.append('utility_function')

3. Adding Configuration:
----------------------
To add global configuration:
    from .config.settings import CONFIG
    __all__.append('CONFIG')
"""

# Package metadata
__author__ = 'Netanel Miller'
__email__ = 'nmiller@ti.com'
__description__ = 'A framework for building AI agents with different LLM backends'

# Framework default configuration
DEFAULT_CONFIG = {
    'logging_level': 'INFO',    # Default logging level
    'default_agent': 'BedrockAgent'  # Default agent implementation
}

# Note: Additional configuration can be added in config/settings.pyl
