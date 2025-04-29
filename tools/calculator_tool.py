# agent_framework/tools/calculator_tool.py

from langchain.tools import Tool
from typing import Optional
import logging
import operator

logger = logging.getLogger(__name__)


def get_calculator_tool(
        llm=None,
        custom_description: Optional[str] = None
) -> Tool:
    """Create and return a simple calculator tool."""

    def safe_eval(expression: str) -> float:
        """Safely evaluate mathematical expressions."""
        # Define allowed operators
        operators = {
            '+': operator.add,
            '-': operator.sub,
            '*': operator.mul,
            '/': operator.truediv
        }

        try:
            # Remove all whitespace and get tokens
            expr = ''.join(expression.split())

            # Parse for addition/subtraction first
            terms = []
            current_num = ''
            current_op = '+'

            for char in expr:
                if char.isdigit() or char == '.':
                    current_num += char
                elif char in operators:
                    if current_num:
                        terms.append((float(current_num), current_op))
                        current_num = ''
                    current_op = char

            # Add the last number
            if current_num:
                terms.append((float(current_num), current_op))

            # Calculate result
            result = 0
            for num, op in terms:
                result = operators[op](result, num)

            # Convert to int if it's a whole number
            if result.is_integer():
                return int(result)
            return result

        except Exception as e:
            logger.error(f"Calculation error: {str(e)} for input: {expression}")
            raise ValueError(f"Invalid expression: {expression}")

    def calculator(expression: str) -> str:
        """
        Calculate the result of a mathematical expression.

        Args:
            expression (str): A mathematical expression

        Returns:
            str: The result of the calculation
        """
        try:
            # Extract just the numbers and operators
            cleaned = ''.join(c for c in expression if c.isdigit() or c in '+-*/.() ')
            result = safe_eval(cleaned)
            return str(result)
        except Exception as e:
            return f"Error: {str(e)}"

    return Tool(
        name="Calculator",
        func=calculator,
        description="A calculator for basic math operations (+, -, *, /). Input should be a simple math expression like '2 + 2' or '5 * 3'.",
        return_direct=True
    )