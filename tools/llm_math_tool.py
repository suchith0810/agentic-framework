# agent_framework/tools/llm_math_tool.py
"""
LLM Math Tool Module
Provides a language model-powered mathematical computation tool.

This tool uses LangChain's llm-math tool for performing mathematical calculations
using the language model. It can handle complex mathematical expressions and
provide step-by-step solutions.

Usage:
    from tools import get_llm_math_tool
    math_tool = get_llm_math_tool(llm)
    result = math_tool.run("2 + 2 * 3")
"""

from langchain_community.agent_toolkits.load_tools import load_tools
import logging

# Configure logging
logger = logging.getLogger(__name__)


def get_llm_math_tool(llm):
    """
    Create and return the LLM Math tool.

    Args:
        llm: Language model instance required for mathematical computations

    Returns:
        Tool: Configured LLM Math tool

    Example:
        >>> math_tool = get_llm_math_tool(llm)
        >>> result = math_tool.run("sqrt(16) + 2")
        >>> print(result)  # "6"

    Note:
        - This tool requires an LLM instance to work
        - Can handle complex mathematical expressions
        - Returns the first tool from load_tools as it only loads one math tool
    """
    try:
        # Load the LLM Math tool from LangChain
        math_tools = load_tools(["llm-math"], llm=llm)
        if not math_tools:
            raise ValueError("No math tools loaded")
        else:
            logger.info("Successfully loaded LLM Math tool")
        return math_tools[0]  # Return the first (and only) math tool

    except Exception as e:
        logger.error(f"Error loading LLM Math tool: {str(e)}")
        raise


"""
Example Usage:

from langchain_community.llms import OpenAI

# Initialize LLM
llm = OpenAI()

# Get math tool
math_tool = get_llm_math_tool(llm)

# Use the tool
result = math_tool.run("2 * (3 + 4)")
print(result)  # "14"

Capabilities:
1. Basic arithmetic: +, -, *, /
2. Functions: sqrt(), pow(), abs(), etc.
3. Complex expressions with parentheses
4. Step-by-step problem solving
"""