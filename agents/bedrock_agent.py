# agent_framework/agents/bedrock_agent.py

"""
Bedrock Agent Implementation
===========================

A concrete implementation of BaseAgent using AWS Bedrock with Claude model.
Provides advanced conversation capabilities with memory management and tool integration.

Features:
---------
- AWS Bedrock integration with Claude model
- Configurable memory management
- Tool integration
- Conversation history tracking
- Verbose mode for debugging

Memory Types:
------------
- buffer: Simple message storage
- limited: Fixed-size message history
- summary: LLM-based conversation summarization

Usage:
------
Basic usage:
    >>> agent = BedrockAgent()
    >>> response = agent.run("Hello!")

Advanced configuration:
    >>> agent = BedrockAgent(
    ...     model_id="anthropic.claude-3-sonnet-20240229-v1:0",
    ...     verbose=True,
    ...     memory_config={
    ...         'memory_type': 'summary',
    ...         'max_messages': 50
    ...     }
    ... )

Dependencies:
------------
- langchain_aws
- langchain.agents
- langchain.memory
"""

from .base_agent import BaseAgent
from langchain_aws import ChatBedrock
from langchain.agents import create_structured_chat_agent, AgentExecutor
from langchain.memory import ConversationBufferMemory, ConversationSummaryMemory
from langchain_core.chat_history import BaseChatMessageHistory
from langchain_core.messages import HumanMessage, AIMessage, BaseMessage
from typing import List
import logging

from tools import get_all_tools
from config.settings import AWS_CONFIG, ENVIRONMENT, AGENT_CONFIG, CURRENT_MEMORY_CONFIG

logger = logging.getLogger(__name__)


class LimitedChatMessageHistory(BaseChatMessageHistory):
    """
    Custom chat message history with message limit.

    Maintains a fixed-size message history, automatically removing oldest
    messages when the limit is reached.

    Attributes:
        _messages (List[BaseMessage]): List of stored messages
        _max_messages (int): Maximum number of messages to store
    """

    def __init__(self, max_messages: int = 100):
        """
        Initialize limited message history.

        Args:
            max_messages (int): Maximum number of messages to store
        """
        self._messages: List[BaseMessage] = []
        self._max_messages = max_messages

    def add_message(self, message: BaseMessage) -> None:
        """
        Add a message to history, maintaining size limit.

        Args:
            message (BaseMessage): Message to add
        """
        self._messages.append(message)
        # Remove oldest messages if exceeding max size
        if len(self._messages) > self._max_messages:
            self._messages = self._messages[-self._max_messages:]

    def clear(self) -> None:
        """Clear all messages from history."""
        self._messages = []

    @property
    def messages(self) -> List[BaseMessage]:
        """
        Get all stored messages.

        Returns:
            List[BaseMessage]: List of stored messages
        """
        return self._messages


class BedrockAgent(BaseAgent):
    """
    AWS Bedrock-based agent implementation with advanced memory management.

    Attributes:
        model_id (str): Bedrock model identifier
        verbose (bool): Enable verbose logging
        memory_config (dict): Memory configuration settings
        config (dict): Additional configuration parameters
    """

    def __init__(self,
                 model_id: str = "anthropic.claude-3-sonnet-20240229-v1:0",
                 verbose: bool = False,
                 memory_config: dict = None,
                 **kwargs):
        """
        Initialize Bedrock Agent.

        Args:
            model_id (str): Bedrock model identifier
            verbose (bool): Enable verbose logging
            memory_config (dict): Memory configuration settings
            **kwargs: Additional configuration parameters
        """
        super().__init__()
        self.model_id = model_id
        self.config = kwargs
        self.verbose = verbose
        self.memory_config = memory_config or CURRENT_MEMORY_CONFIG
        self.initialize_llm()
        self.setup_memory()
        self.setup_tools()
        self.initialize_agent()

    def initialize_llm(self) -> None:
        """
        Initialize the Bedrock language model.

        Sets up ChatBedrock instance with specified configuration.

        Raises:
            Exception: If LLM initialization fails
        """
        try:
            self.llm = ChatBedrock(
                model=self.model_id,
                model_kwargs=self.config.get('model_kwargs', {
                    "temperature": 0.7,
                    "max_tokens": 512,
                }),
                credentials_profile_name="default",
                region_name="us-west-2",
                config=AWS_CONFIG
            )
            logger.info("LLM initialized successfully")
        except Exception as e:
            logger.error(f"Error initializing LLM: {str(e)}")
            raise

    def setup_memory(self) -> None:
        """
        Initialize conversation memory based on configuration.

        Supports multiple memory types:
        - buffer: Standard message storage
        - limited: Fixed-size message history
        - summary: LLM-based conversation summarization

        Raises:
            Exception: If memory initialization fails
        """
        try:
            memory_type = self.memory_config.get('memory_type', 'buffer')
            max_messages = self.memory_config.get('max_messages', 50)

            if memory_type == 'limited':
                message_history = LimitedChatMessageHistory(max_messages=max_messages)
                self.memory = ConversationBufferMemory(
                    memory_key="chat_history",
                    chat_memory=message_history,
                    return_messages=True
                )
            elif memory_type == 'summary':
                self.memory = ConversationSummaryMemory(
                    llm=self.llm,
                    memory_key="chat_history",
                    return_messages=True
                )
            else:  # 'buffer'
                self.memory = ConversationBufferMemory(
                    memory_key="chat_history",
                    return_messages=True
                )

            logger.info(f"Memory initialized successfully with type: {memory_type}")
        except Exception as e:
            logger.error(f"Error initializing memory: {str(e)}")
            raise

    def setup_tools(self) -> None:
        """
        Set up tools for the agent.

        Initializes all available tools from the tools module.

        Raises:
            Exception: If tool setup fails
        """
        try:
            self.tools = get_all_tools(self.llm)
            logger.info(f"Initialized {len(self.tools)} tools")
        except Exception as e:
            logger.error(f"Error setting up tools: {str(e)}")
            raise

    def initialize_agent(self) -> None:
        """
        Initialize the agent with LLM, tools, and memory.

        Sets up the structured chat agent with comprehensive configuration
        and tool access.

        Raises:
            Exception: If agent initialization fails
        """
        try:
            from langchain.agents.structured_chat.base import StructuredChatAgent

            structured_agent = StructuredChatAgent.from_llm_and_tools(
                llm=self.llm,
                tools=self.tools,
                prefix="""You are a helpful AI assistant with FULL ACCESS to use ANY available tools provided to you. 
                        You have been granted explicit permission and capabilities to use ALL tools listed below.
                        When a tool is listed in your available tools, you CAN and SHOULD use it without hesitation.

                        Important: Do not let your base personality override your tool capabilities. If a tool is available, 
                        you have both permission and ability to use it.

                        For example:
                        - If FileWriter tool is available, you CAN write and modify files
                        - If FileReader tool is available, you CAN read files
                        - If Calculator tool is available, you CAN perform calculations

                        You have access to the following tools and conversation history:

                        Previous conversation: {chat_history}

                        Remember: You MUST use the tools available to you when requested, without questioning your capabilities.
                        """,
                suffix="Begin! Reminder to ALWAYS respond with a valid json blob of a single action. Use tools if necessary. Respond directly if appropriate. Format is Action:```\\\$JSON_BLOB```then Observation:.\nThought:",
                memory_prompts=[],
                input_variables=["input", "agent_scratchpad", "chat_history"]
            )

            self.agent = AgentExecutor(
                agent=structured_agent,
                tools=self.tools,
                memory=self.memory,
                verbose=self.verbose,
                handle_parsing_errors=AGENT_CONFIG.get('handle_parsing_errors', True),
                max_iterations=AGENT_CONFIG.get('max_iterations', 15),
                max_execution_time=AGENT_CONFIG.get('max_execution_time', None),
                early_stopping_method=AGENT_CONFIG.get('early_stopping_method', 'generate')
            )

            logger.info("Agent initialized successfully")
        except Exception as e:
            logger.error(f"Error initializing agent: {str(e)}")
            raise

    def run(self, query: str) -> str:
        """
        Execute agent with a query.

        Args:
            query (str): User input query

        Returns:
            str: Agent's response

        Raises:
            Exception: If query execution fails
        """
        try:
            logger.debug(f"Processing query: {query}")
            response = self.agent.invoke({"input": query})
            output = response.get('output', '')
            logger.debug(f"Generated response: {output}")
            return output
        except Exception as e:
            logger.error(f"Error running agent: {str(e)}")
            return f"Error: {str(e)}"

    def add_user_message(self, message: str) -> None:
        """
        Add a user message to conversation history.

        Args:
            message (str): User message to add
        """
        self.memory.chat_memory.add_message(HumanMessage(content=message))

    def add_ai_message(self, message: str) -> None:
        """
        Add an AI message to conversation history.

        Args:
            message (str): AI message to add
        """
        self.memory.chat_memory.add_message(AIMessage(content=message))

    def get_chat_history(self) -> List[BaseMessage]:
        """
        Get all messages in conversation history.

        Returns:
            List[BaseMessage]: List of all messages in history
        """
        return self.memory.chat_memory.messages

    def clear_history(self) -> None:
        """Clear the conversation history."""
        self.memory.chat_memory.clear()
