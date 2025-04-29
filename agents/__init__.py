# agent_framework/agents/__init__.py

"""
Agents Package Initialization
============================

Defines and exports available agent implementations in the framework. This module serves
as the central point for agent class registration and access.

Available Agents:
---------------
- BaseAgent: Abstract base class defining the agent interface
- BedrockAgent: AWS Bedrock-based implementation with Claude model

Class Hierarchy:
--------------
BaseAgent
    └── BedrockAgent
    └── (Future implementations)

Usage:
------
Basic import:
    >>> from agent_framework.agents import BedrockAgent
    >>> agent = BedrockAgent()

Custom configuration:
    >>> agent = BedrockAgent(
    ...     model_id='anthropic.claude-3-sonnet-20240229-v1:0',
    ...     verbose=True
    ... )

Adding New Agents:
----------------
1. Create new agent file (e.g., openai_agent.py)
2. Implement agent class inheriting from BaseAgent
3. Import and add to __all__

Example adding new agent:
    # In openai_agent.py:
    class OpenAIAgent(BaseAgent):
        ...

    # In this file:
    from .openai_agent import OpenAIAgent
    __all__ = ['BaseAgent', 'BedrockAgent', 'OpenAIAgent']

Note:
----
- Keep BaseAgent first in __all__ as it's the parent class
- Maintain alphabetical order for other agents
- Ensure all agents implement BaseAgent interface
"""

from .base_agent import BaseAgent
from .bedrock_agent import BedrockAgent

__all__ = [
    'BaseAgent',    # Base class for all agents
    'BedrockAgent'  # AWS Bedrock implementation
]

"""
Future Extensions:
----------------
To add a new agent implementation:

1. Create Agent Class:
   Create a new file in the agents directory:
   agents/
   ├── base_agent.py
   ├── bedrock_agent.py
   └── new_agent.py

2. Import Agent:
   Add import statement:
   from .new_agent import NewAgent

3. Add to Exports:
   Add to __all__ list:
   __all__ = ['BaseAgent', 'BedrockAgent', 'NewAgent']

4. Document Agent:
   Update this docstring with:
   - New agent description
   - Usage examples
   - Configuration options

Example Implementation:
---------------------
# new_agent.py
from .base_agent import BaseAgent

class NewAgent(BaseAgent):
    def __init__(self, **kwargs):
        super().__init__()
        self.configure(**kwargs)

    def initialize_llm(self):
        # Implementation
        pass

    def setup_tools(self):
        # Implementation
        pass

    def run(self, query: str) -> str:
        # Implementation
        pass
"""

# Optional: Package metadata and version tracking
__version__ = '0.1.0'
__author__ = 'Netanel Miller'
__email__ = 'nmiller@ti.com'