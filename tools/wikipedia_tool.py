# # agent_framework/tools/wikipedia_tool.py
# from langchain.tools import Tool
# from langchain_community.utilities import WikipediaAPIWrapper
#
# def get_wikipedia_tool():
#     """Create and return the Wikipedia tool."""
#     wikipedia = WikipediaAPIWrapper()
#
#     return Tool(
#         name="Wikipedia",
#         func=wikipedia.run,
#         description="Useful for searching and retrieving information from Wikipedia"
#     )
#

# agent_framework/tools/wikipedia_tool.py
"""
Wikipedia Tool Module
Provides functionality for searching and retrieving information from Wikipedia.

Features:
- Wikipedia article search
- Content retrieval
- Error handling
- Configurable search parameters

Usage:
    from tools import get_wikipedia_tool
    wiki_tool = get_wikipedia_tool()
    result = wiki_tool.run("Python programming language")
"""

from langchain.tools import Tool
from langchain_community.utilities import WikipediaAPIWrapper
import logging
import requests
from typing import Optional, Dict, Any

# Configure logging
logger = logging.getLogger(__name__)


def get_wikipedia_tool(
        lang: str = "en",
        top_k_results: int = 3,
        max_doc_length: int = 2000,
        proxy: Optional[Dict[str, str]] = None,
        custom_description: Optional[str] = None
) -> Tool:
    """
    Create and return the Wikipedia tool.

    Args:
        lang (str): Wikipedia language (default: "en")
        top_k_results (int): Number of results to fetch (default: 3)
        max_doc_length (int): Maximum length of returned content (default: 2000)
        custom_description (Optional[str]): Custom tool description

    Returns:
        Tool: Configured Wikipedia search tool

    Example:
        >>> wiki_tool = get_wikipedia_tool(lang="en", top_k_results=5)
        >>> result = wiki_tool.run("Albert Einstein")
        >>> print(result)
    """
    try:
        # Configure proxies for requests
        if proxy:
            # Configure requests to use proxy
            requests.Session().proxies.update(proxy)

        # Initialize Wikipedia API wrapper with configuration
        wikipedia = WikipediaAPIWrapper(
            lang=lang,
            top_k_results=top_k_results,
            doc_content_chars_max=max_doc_length
        )

        # Default tool description
        default_description = (
            "Useful for searching and retrieving information from Wikipedia. "
            "Input should be a search query or topic name. "
            f"Returns up to {top_k_results} results in {lang} language."
        )

        # Create and return the tool
        return Tool(
            name="Wikipedia",
            func=wikipedia.run,
            description=custom_description or default_description
        )

    except Exception as e:
        logger.error(f"Error initializing Wikipedia tool: {str(e)}")
        raise


"""
Example Usage:

# Basic usage
wiki_tool = get_wikipedia_tool()
result = wiki_tool.run("Python programming")

# Custom configuration
custom_wiki_tool = get_wikipedia_tool(
    lang="es",                    # Spanish Wikipedia
    top_k_results=5,             # Get 5 results
    max_doc_length=3000,         # Longer content
    custom_description="Search Wikipedia in Spanish"
)

Capabilities:
1. Search Wikipedia articles
2. Retrieve article content
3. Multiple language support
4. Configurable result length
5. Error handling
"""


# Optional: Enhanced version with additional features
# def get_enhanced_wikipedia_tool(
#         config: Optional[Dict[str, Any]] = None
# ) -> Tool:
#     """
#     Enhanced Wikipedia tool with additional features.
#
#     Args:
#         config: Tool configuration parameters
#
#     Returns:
#         Tool: Enhanced Wikipedia tool
#     """
#     # Default configuration
#     default_config = {
#         'lang': 'en',
#         'top_k_results': 3,
#         'max_doc_length': 2000,
#         'load_all_available_meta': True
#     }
#
#     # Update with custom config if provided
#     tool_config = {**default_config, **(config or {})}
#
#     # Initialize Wikipedia wrapper with configuration
#     wikipedia = WikipediaAPIWrapper(**tool_config)
#
#     def enhanced_search(query: str) -> str:
#         """Enhanced search with error handling and formatting."""
#         try:
#             results = wikipedia.run(query)
#             return results
#         except Exception as e:
#             logger.error(f"Wikipedia search error: {str(e)}")
#             return f"Error searching Wikipedia: {str(e)}"
#
#     return Tool(
#         name="EnhancedWikipedia",
#         func=enhanced_search,
#         description=(
#             "Advanced Wikipedia search tool. "
#             f"Searches in {tool_config['lang']} language. "
#             f"Returns up to {tool_config['top_k_results']} results."
#         )
#     )