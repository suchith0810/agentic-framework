#!/apps/free/python/3.9.2/bin/python3
"""
Agent Framework - Main Entry Point
================================

Interactive chat interface for the agent framework featuring configurable verbosity
levels, command handling, and chat history tracking.

Features:
---------
- Interactive chat interface with AI agent
- Multiple verbosity levels with dynamic adjustment
- Persistent chat history tracking
- Controlled logging for different components
- Special command handling

Commands:
---------
- 'exit': Quit the chat session
- 'history': Display chat conversation history
- 'verbose': Cycle through verbose levels (quiet → info → warning → error)
- 'verbose [level]': Set specific verbose level:
    * quiet: Show only Q&A
    * info: Show detailed processing information
    * warning: Show warnings and above
    * error: Show only errors

Usage:
------
    \$ ./main.py

Example Session:
    You: hello
    Agent: Hello! How can I help you?

    You: verbose info
    Verbose level: INFO
    [Shows detailed processing information]

    You: verbose quiet
    Verbose level: QUIET
    [Shows only Q&A]
"""

import sys
import os
import logging

# Add the parent directory to Python path for module imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from agents.bedrock_agent import BedrockAgent
from langchain_core.messages import HumanMessage
from enum import Enum

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class VerboseLevel(Enum):
    """
    Enumeration for controlling output detail levels.

    Attributes:
        QUIET (0): Show only essential Q&A interaction
        INFO (1): Show detailed processing steps and information
        WARNING (2): Show warnings and more critical messages
        ERROR (3): Show only error messages
    """
    QUIET = 0
    INFO = 1
    WARNING = 2
    ERROR = 3

    @classmethod
    def from_string(cls, level_str: str) -> 'VerboseLevel':
        """
        Convert string input to VerboseLevel enum.

        Args:
            level_str (str): String representation of verbose level

        Returns:
            VerboseLevel: Corresponding enum value or QUIET if invalid

        Example:
            >>> VerboseLevel.from_string('info')
            VerboseLevel.INFO
        """
        try:
            return cls[level_str.upper()]
        except KeyError:
            return cls.QUIET


class ChatConfig:
    """
    Configuration handler for chat settings and logging.

    Manages verbose levels and logging configuration for different
    components of the system.

    Attributes:
        verbose_level (VerboseLevel): Current verbosity level
        verbose (bool): Verbose mode state
        debug (bool): Debug mode state
    """

    def __init__(self):
        """Initialize chat configuration with default settings."""
        self.verbose_level = VerboseLevel.QUIET
        self._setup_logging()

    def set_verbose_level(self, level: str) -> str:
        """
        Set verbose level and adjust logging.

        Args:
            level (str): Desired verbose level name

        Returns:
            str: Confirmation message
        """
        self.verbose_level = VerboseLevel.from_string(level)
        self._setup_logging()
        return f"Verbose level set to: {self.verbose_level.name}"

    def _get_logging_level(self, base_level: VerboseLevel = None) -> int:
        """
        Convert VerboseLevel to corresponding logging level.

        Args:
            base_level (VerboseLevel, optional): Override current verbose level

        Returns:
            int: Corresponding logging level
        """
        level = base_level or self.verbose_level
        return {
            VerboseLevel.QUIET: logging.ERROR,
            VerboseLevel.INFO: logging.INFO,
            VerboseLevel.WARNING: logging.WARNING,
            VerboseLevel.ERROR: logging.ERROR
        }[level]

    def toggle_verbose(self) -> str:
        """
        Toggle verbose mode and adjust logging level.

        Returns:
            str: Status message indicating new verbose state
        """
        self.verbose = not self.verbose
        self.debug = self.verbose
        self._setup_logging(self.debug)
        return f"Verbose mode {'enabled' if self.verbose else 'disabled'}"

    def _setup_logging(self):
        """
        Configure logging levels for different components.

        Sets up logging levels for specific loggers while maintaining
        stricter control over other system loggers.
        """
        # Loggers to control
        loggers_to_adjust = [
            'langchain',
            'boto3',
            'botocore',
            'langchain_aws',
            'langchain_core',
            'langchain_community'
        ]

        # Set base logging configuration
        logging.basicConfig(
            level=logging.ERROR,
            format='%(asctime)s - %(levelname)s - %(message)s'
        )

        logging_level = self._get_logging_level()

        # Set specific level for controlled loggers
        for logger_name in loggers_to_adjust:
            logging.getLogger(logger_name).setLevel(logging_level)

        # Set all other loggers to ERROR to minimize noise
        for name in logging.root.manager.loggerDict:
            if name not in loggers_to_adjust:
                logging.getLogger(name).setLevel(logging.ERROR)

        loggers_list = ', '.join(loggers_to_adjust)
        print(f"\nVerbose level: {self.verbose_level.name}")
        print(f"Affected loggers: {loggers_list}")


def setup_agent(config: ChatConfig) -> BedrockAgent:
    """
    Initialize and configure the Bedrock Agent.

    Args:
        config (ChatConfig): Current configuration settings

    Returns:
        BedrockAgent: Configured agent instance or None if initialization fails

    Raises:
        Exception: If agent initialization fails
    """
    try:
        logger.debug("Initializing Bedrock Agent...")
        agent = BedrockAgent(verbose=(config.verbose_level == VerboseLevel.INFO))
        logger.debug("Agent initialized successfully")
        return agent
    except Exception as e:
        logger.error(f"Failed to initialize agent: {str(e)}")
        return None


def process_commands(command: str, agent: BedrockAgent, config: ChatConfig) -> bool:
    """
    Process special commands in the chat interface.

    Args:
        command (str): User input command
        agent (BedrockAgent): Current agent instance
        config (ChatConfig): Current configuration

    Returns:
        bool: True if should exit, False to continue

    Commands:
        exit: Quit the chat session
        history: Display chat conversation history
        verbose: Toggle or set verbose level
    """
    command = command.lower()

    if command == 'exit':
        return True
    elif command == 'history':
        print("\nChat History:")
        for msg in agent.memory.chat_memory.messages:
            role = "User" if isinstance(msg, HumanMessage) else "Agent"
            print(f"{role}: {msg.content}")
        return False
    elif command.startswith('verbose'):
        parts = command.split()
        if len(parts) > 1:
            message = config.set_verbose_level(parts[1])
        else:
            current_idx = list(VerboseLevel).index(config.verbose_level)
            next_idx = (current_idx + 1) % len(VerboseLevel)
            next_level = list(VerboseLevel)[next_idx]
            message = config.set_verbose_level(next_level.name)

        agent.agent.verbose = config.verbose_level == VerboseLevel.INFO
        print(message)
        return False
    return False


def main():
    """
    Main function implementing the chat loop.

    Handles:
    - Configuration initialization
    - Agent setup
    - Command processing
    - Chat interaction
    - Error handling
    """
    try:
        # Initialize configuration
        config = ChatConfig()

        # Initialize agent with config
        agent = setup_agent(config)
        if not agent:
            logger.error("Failed to initialize agent. Exiting.")
            return

        print("\nChat with the agent")
        print("Commands:")
        print("  'exit': Quit the chat")
        print("  'history': View chat history")
        print("  'verbose': Cycle through verbose levels")
        print("  'verbose [level]': Set specific verbose level (quiet/info/warning/error)")

        # Main chat loop
        while True:
            user_input = input("\nYou: ").strip()

            if process_commands(user_input, agent, config):
                break

            if user_input and not user_input.lower().startswith(('history', 'verbose')):
                response = agent.run(user_input)
                print(f"\nAgent: {response}")

    except Exception as e:
        logger.error(f"Error in main: {str(e)}")
        print(f"An error occurred: {str(e)}")


if __name__ == "__main__":
    main()
