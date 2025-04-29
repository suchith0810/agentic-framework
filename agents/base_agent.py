# agent_framework/agents/base_agent.py

"""
Base Agent Abstract Class
========================

Defines the core interface and structure for all agent implementations in the framework.
This abstract base class ensures consistent behavior across different agent types by
defining required methods and basic functionality.

Class Structure:
--------------
BaseAgent
    ├── initialize_llm()
    ├── setup_tools()
    ├── initialize_agent()
    └── run()

Required Implementations:
----------------------
All concrete agent classes must implement:
1. initialize_llm(): Set up the language model
2. setup_tools(): Configure available tools
3. initialize_agent(): Set up the agent with LLM and tools
4. run(): Execute queries with the agent

Example Implementation:
--------------------
class CustomAgent(BaseAgent):
    def initialize_llm(self):
        self.llm = SomeLLMImplementation()

    def setup_tools(self):
        self.tools = [Tool1(), Tool2()]

    def initialize_agent(self):
        self.agent = AgentImplementation(self.llm, self.tools)

    def run(self, query: str) -> str:
        return self.agent.execute(query)
"""

from abc import ABC, abstractmethod
from langchain.memory import ConversationBufferMemory
from typing import List, Any, Optional


class BaseAgent(ABC):
    """
    Abstract base class for all agent implementations.

    Attributes:
        llm: Language model instance
        tools (List): Available tools for the agent
        memory: Conversation memory system
        agent: Agent implementation instance

    Note:
        All attributes are initialized as None and must be set by concrete implementations
        in their respective initialization methods.
    """

    def __init__(self):
        """
        Initialize base agent attributes.

        All attributes are set to None initially and should be properly
        initialized by concrete implementations in their respective
        initialization methods.
        """
        self.llm = None       # Language model instance
        self.tools = []       # List of available tools
        self.memory = None    # Conversation memory
        self.agent = None     # Agent implementation

    @abstractmethod
    def initialize_llm(self) -> None:
        """
        Initialize the language model for the agent.

        This method should:
        1. Set up the specific LLM implementation
        2. Configure any LLM-specific parameters
        3. Handle authentication if required
        4. Set self.llm to the initialized LLM instance

        Raises:
            NotImplementedError: Must be implemented by concrete classes
        """
        pass

    @abstractmethod
    def setup_tools(self) -> None:
        """
        Set up tools available to the agent.

        This method should:
        1. Initialize required tools
        2. Configure tool-specific parameters
        3. Add tools to self.tools list
        4. Handle any tool dependencies

        Raises:
            NotImplementedError: Must be implemented by concrete classes
        """
        pass

    @abstractmethod
    def initialize_agent(self) -> None:
        """
        Initialize the agent with LLM and tools.

        This method should:
        1. Create the agent instance
        2. Configure agent parameters
        3. Set up the agent with LLM and tools
        4. Initialize memory if required
        5. Set self.agent to the initialized agent

        Raises:
            NotImplementedError: Must be implemented by concrete classes
        """
        pass

    @abstractmethod
    def run(self, query: str) -> str:
        """
        Execute agent with a query.

        Args:
            query (str): User input query to process

        Returns:
            str: Agent's response to the query

        Raises:
            NotImplementedError: Must be implemented by concrete classes
        """
        pass


"""
Implementation Guidelines:
=======================

1. Memory Management:
   - Initialize appropriate memory system in initialize_agent()
   - Consider memory limitations and cleanup
   - Implement memory persistence if required

2. Error Handling:
   - Implement robust error handling in all methods
   - Provide meaningful error messages
   - Consider retry mechanisms for transient failures

3. Resource Management:
   - Clean up resources in appropriate methods
   - Implement context manager if needed
   - Handle rate limiting and quotas

Example Error Handling:
---------------------
def initialize_llm(self):
    try:
        self.llm = SomeLLM()
    except AuthError:
        raise AgentInitError("Failed to authenticate LLM")
    except ConnectionError:
        raise AgentInitError("Failed to connect to LLM service")

Example Resource Management:
-------------------------
def __enter__(self):
    self.initialize_llm()
    self.setup_tools()
    self.initialize_agent()
    return self

def __exit__(self, exc_type, exc_val, exc_tb):
    self.cleanup_resources()
"""
