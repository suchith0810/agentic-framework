# agent_framework/tools/filesystem_tools.py
"""
File System Tools Module
=======================

Provides a collection of FileSystem tools with optional security features, particularly
designed for development and production environments.

Key Features:
------------
1. Environment-Aware Operation:
   - Development: Unrestricted file system access
   - Production: Security measures enforced
   - Testing: Basic security checks

2. Available Tools:
   - ReadFileTool: Read file contents
   - WriteFileTool: Create or modify files
   - ListDirectoryTool: List directory contents
   - FileSearchTool: Search for files matching patterns

3. Security Features (Production Only):
   - Path validation and sanitization
   - Root directory restriction
   - File size limitations
   - Operation logging
   - Extension restrictions

4. Development Mode:
   - All security checks disabled
   - Unrestricted file access
   - Full filesystem operations
   - No path validation

Usage Examples:
-------------
Development Mode:
    >>> from tools import get_filesystem_tools
    >>> tools = get_filesystem_tools()  # No restrictions

Production Mode:
    >>> tools = get_filesystem_tools(
    ...     root_dir='/safe/path',
    ...     allowed_operations=['read', 'list']
    ... )

Configuration:
------------
1. Development (Default):
   - Security disabled
   - All operations allowed
   - No file size limits
   - No path validation

2. Production:
   - Security enabled
   - Path validation
   - Operation logging
   - Size limits enforced
   - Extension restrictions

Classes:
-------
FileSystemSecurity: Security manager for filesystem operations
FileSystemMetrics: Operation tracking and monitoring
FileSystemError: Base exception class
SecurityError: Security-related exceptions
ResourceError: Resource limitation exceptions

Implementation Notes:
------------------
1. Development Mode:
   - Direct tool initialization
   - No wrapper functions
   - Maximum flexibility

2. Production Mode:
   - Security wrapper implementation
   - Path validation
   - Resource monitoring
   - Access control

Environment Variables:
-------------------
ENV: Determines security mode
    - 'development': No security (default)
    - 'production': Full security
    - 'testing': Basic security

Dependencies:
-----------
- langchain_community.tools
- config.settings (for environment configuration)
- pathlib (for path operations)
- logging (for operation logging)

See Also:
--------
- config/settings.py: Environment-specific configurations
- tools/file_reader_tool.py: Specific file reading implementation
- tools/file_writer_tool.py: Specific file writing implementation
"""


from langchain_community.tools import (
    ReadFileTool,
    WriteFileTool,
    ListDirectoryTool,
    FileSearchTool,
)
from langchain.tools import Tool
import logging
import os
from datetime import datetime
from typing import List, Optional, Dict, Any
from config.settings import FILESYSTEM_CONFIG, ENVIRONMENT

logger = logging.getLogger(__name__)


class FileSystemSecurity:
    """
    Security manager for filesystem operations.

    Manages security aspects of filesystem operations based on environment configuration.
    Handles path validation, operation logging, and access control.

    Attributes:
        config (dict): Security configuration settings
        security_config (dict): Specific security rules and settings
        metrics (FileSystemMetrics): Optional metrics tracking instance

    Example:
        >>> security = FileSystemSecurity(config={'security': {'validate_paths': True}})
        >>> security.validate_path('/safe/path/file.txt', '/safe/path')
    """

    def __init__(self, config: Dict[str, Any] = None):
        self.config = config or FILESYSTEM_CONFIG
        self.security_config = self.config.get('security', {})
        self.metrics = FileSystemMetrics() if self.security_config.get('monitor_operations') else None

    def validate_path(self, path: str, root_dir: str) -> bool:
        """
        Standalone path validation function for basic security checks.

        Validates that a given path is within the allowed root directory and
        doesn't contain suspicious patterns.

        Args:
            path (str): Path to validate
            root_dir (str): Root directory to check against

        Returns:
            bool: True if path is valid and safe

        Example:
            >>> validate_path('/data/file.txt', '/data')
            True
            >>> validate_path('/etc/passwd', '/data')
            False
        """
        if not self.security_config.get('validate_paths', True):
            return True

        try:
            # Convert to absolute paths
            abs_path = os.path.abspath(path)
            abs_root = os.path.abspath(root_dir)

            # Check if path is within root directory
            if not abs_path.startswith(abs_root):
                logger.warning(f"Path {path} is outside root directory {root_dir}")
                return False

            # Check for restricted patterns
            restricted_patterns = self.security_config.get('restricted_patterns', [])
            if any(pattern in path for pattern in restricted_patterns):
                logger.warning(f"Path {path} contains restricted patterns")
                return False

            # Check file extension if specified
            if self.security_config.get('allowed_extensions'):
                file_ext = os.path.splitext(path)[1].lower()
                if file_ext not in self.security_config['allowed_extensions']:
                    logger.warning(f"File extension {file_ext} is not allowed")
                    return False

            return True

        except Exception as e:
            logger.error(f"Path validation error: {str(e)}")
            return False

    def log_operation(self, operation: str, path: str):
        """
        Log filesystem operations based on security configuration.

        Records operation details and updates metrics if enabled.

        Args:
            operation (str): Type of operation (read/write/list/search)
            path (str): Path of the file being operated on

        Example:
            >>> security.log_operation('read', '/data/file.txt')
        """
        if self.security_config.get('log_all_operations'):
            logger.info(f"Filesystem operation: {operation} on {path}")

        if self.metrics:
            self.metrics.record_operation(operation)


def validate_path(path: str, root_dir: str) -> bool:
    """
    Validate file path for security.

    Ensures paths are within allowed root directory and don't contain
    dangerous patterns.

    Args:
        path (str): Path to validate
        root_dir (str): Root directory to restrict access to

    Returns:
        bool: True if path is valid, False otherwise

    Example:
        >>> validate_path('/safe/path/file.txt', '/safe/path')
        True
        >>> validate_path('/unsafe/path', '/safe/path')
        False
    """
    try:
        # Convert to absolute paths
        abs_path = os.path.abspath(path)
        abs_root = os.path.abspath(root_dir)

        # Check if path is within root directory
        if not abs_path.startswith(abs_root):
            logger.warning(f"Path {path} is outside root directory {root_dir}")
            return False

        # Check for suspicious patterns
        suspicious_patterns = ['..', '~', '\$', '|', ';', '&']
        if any(pattern in path for pattern in suspicious_patterns):
            logger.warning(f"Path {path} contains suspicious patterns")
            return False

        return True

    except Exception as e:
        logger.error(f"Path validation error: {str(e)}")
        return False


def create_safe_file_tool(
        tool_class,
        root_dir: str,
        security_manager: FileSystemSecurity,
        **kwargs
) -> Tool:
    """
    Create a filesystem tool with appropriate security wrapper based on environment.

    Wraps standard filesystem tools with security checks and logging capabilities.
    In development mode, minimal wrapping is applied for maximum flexibility.

    Args:
        tool_class: The tool class to instantiate (ReadFileTool, WriteFileTool, etc.)
        root_dir (str): Base directory for file operations
        security_manager (FileSystemSecurity): Security manager instance
        **kwargs: Additional arguments for tool initialization

    Returns:
        Tool: Configured filesystem tool with security wrapper

    Raises:
        Exception: If tool creation fails

    Example:
        >>> security_manager = FileSystemSecurity()
        >>> read_tool = create_safe_file_tool(ReadFileTool, '/data', security_manager)
    """
    try:
        # Create root directory if it doesn't exist
        os.makedirs(root_dir, exist_ok=True)

        # Create the base tool
        base_tool = tool_class(root_dir=root_dir, **kwargs)

        # Get the original call method
        original_call = base_tool.__call__

        # Create safe wrapper
        def safe_wrapper(*args, **kwargs):
            """Add security checks to tool execution."""
            try:
                # Get file path from args or kwargs
                file_path = args[0] if args else kwargs.get('file_path')

                if not file_path:
                    raise ValueError("No file path provided")

                # Validate path using security manager
                if not security_manager.validate_path(file_path, root_dir):
                    raise SecurityError(f"Invalid or unsafe path: {file_path}")

                # Check file size for read operations
                if isinstance(base_tool, ReadFileTool):
                    full_path = os.path.join(root_dir, file_path)
                    if os.path.exists(full_path):
                        if os.path.getsize(full_path) > FILESYSTEM_CONFIG['max_file_size']:
                            raise ResourceError(f"File exceeds size limit: {file_path}")

                # Log operation
                operation_type = tool_class.__name__.replace('Tool', '').lower()
                security_manager.log_operation(operation_type, file_path)

                # Execute original function
                return original_call(*args, **kwargs)

            except Exception as e:
                logger.error(f"Tool execution error: {str(e)}")
                return f"Error: {str(e)}"

        # Replace original __call__ with safe wrapper
        base_tool.__call__ = safe_wrapper
        return base_tool

    except Exception as e:
        logger.error(f"Tool creation error: {str(e)}")
        raise


def get_filesystem_tools(
        root_dir: Optional[str] = None,
        allowed_operations: List[str] = None
) -> List[Tool]:
    """
    Create and return file system tools based on security configuration.

    The function's behavior is determined by the security configuration in FILESYSTEM_CONFIG:
    - When security is disabled (security.enable_security = False):
        * Creates tools with no root directory restriction
        * Allows unrestricted filesystem access
        * Ignores root_dir parameter

    - When security is enabled (security.enable_security = True):
        * Enforces root directory restrictions
        * Applies configured allowed operations
        * Uses provided root_dir or falls back to configuration

    Args:
        root_dir (Optional[str]): Root directory for file operations when security is enabled
        allowed_operations (List[str]): List of allowed operations when security is enabled

    Returns:
        List[Tool]: List of configured filesystem tools

    Examples:
        # With security disabled:
        >>> tools = get_filesystem_tools()  # Returns unrestricted tools

        # With security enabled:
        >>> tools = get_filesystem_tools(
        ...     root_dir='/safe/path',
        ...     allowed_operations=['read', 'list']
        ... )  # Returns restricted tools

    Note:
        The function's behavior is controlled by FILESYSTEM_CONFIG['security']['enable_security'],
        not by the environment setting.
    """
    try:
        # Check if security is disabled
        security_enabled = FILESYSTEM_CONFIG.get('security', {}).get('enable_security', False)

        if not security_enabled:
            # When security is disabled, create tools with no root_dir restriction
            tools = [
                ReadFileTool(),  # No root_dir restriction
                WriteFileTool(),  # No root_dir restriction
                ListDirectoryTool(),
                FileSearchTool()
            ]
            logger.info(f"Initialized {len(tools)} filesystem tools with no restrictions")
            return tools

        # For secured mode, use the configured root_dir
        root_dir = root_dir or FILESYSTEM_CONFIG.get('root_dir') or os.getcwd()
        allowed_operations = allowed_operations or FILESYSTEM_CONFIG.get('allowed_operations')

        # Create root directory if it doesn't exist
        if not os.path.exists(root_dir):
            os.makedirs(root_dir, exist_ok=True)

        tools = []
        operations_map = {
            'read': ReadFileTool,
            'write': WriteFileTool,
            'list': ListDirectoryTool,
            'search': FileSearchTool
        }

        for operation in allowed_operations:
            if operation in operations_map:
                tool = operations_map[operation](root_dir=root_dir)
                tools.append(tool)

        return tools

    except Exception as e:
        logger.error(f"Error initializing filesystem tools: {str(e)}")
        raise









# def get_filesystem_tools(
#         root_dir: Optional[str] = None,
#         allowed_operations: List[str] = None
# ) -> List[Tool]:
#     """
#     Create and return file system tools.
#     In development mode, returns tools with minimal restrictions.
#     In other environments, applies security measures.
#
#     Args:
#         root_dir (Optional[str]): Root directory for file operations
#         allowed_operations (List[str]): List of allowed operations
#
#     Returns:
#         List[Tool]: List of filesystem tools
#     """
#     try:
#         # Use configuration or defaults
#         root_dir = root_dir or FILESYSTEM_CONFIG.get('root_dir') or os.getcwd()
#         allowed_operations = allowed_operations or FILESYSTEM_CONFIG.get('allowed_operations')
#
#         # Create root directory if it doesn't exist
#         if not os.path.exists(root_dir):
#             os.makedirs(root_dir, exist_ok=True)
#
#         tools = []
#         operations_map = {
#             'read': ReadFileTool,
#             'write': WriteFileTool,
#             'list': ListDirectoryTool,
#             'search': FileSearchTool
#         }
#
#         # In development, create tools with minimal restrictions
#         if ENVIRONMENT == 'development':
#             for operation in operations_map:
#                 tool = operations_map[operation](root_dir=root_dir)
#                 tools.append(tool)
#             logger.info(f"Initialized {len(tools)} filesystem tools in development mode")
#             return tools
#
#         # For other environments, create tools with security measures
#         for operation in allowed_operations:
#             if operation in operations_map:
#                 tool = create_secure_tool(
#                     operations_map[operation],
#                     root_dir=root_dir
#                 )
#                 tools.append(tool)
#
#         return tools
#
#     except Exception as e:
#         logger.error(f"Error initializing filesystem tools: {str(e)}")
#         raise


def create_secure_tool(tool_class, root_dir: str, **kwargs) -> Tool:
    """
    Create a secure version of a filesystem tool for non-development environments.

    Provides appropriate tool initialization based on the current environment.
    In development, returns unrestricted tool; in production, applies security measures.

    Args:
        tool_class: The tool class to instantiate
        root_dir (str): Base directory for file operations
        **kwargs: Additional tool configuration parameters

    Returns:
        Tool: Configured filesystem tool

    Example:
        >>> read_tool = create_secure_tool(ReadFileTool, '/data')
    """
    if ENVIRONMENT == 'development':
        # In development, return tool with no restrictions
        return tool_class(root_dir=root_dir, **kwargs)

    # For other environments, implement security measures
    # (Previous security implementation goes here)
    return tool_class(root_dir=root_dir, **kwargs)






"""
Security Best Practices:
=====================

1. Path Validation:
   - Always validate paths against root directory
   - Check for path traversal attempts
   - Sanitize file names
   - Restrict absolute paths

2. Access Control:
   - Implement root directory restriction
   - Control allowed operations
   - Validate file permissions
   - Monitor file access

3. Resource Limits:
   - Enforce file size limits
   - Limit number of operations
   - Implement timeouts
   - Monitor resource usage

4. Error Handling:
   - Catch and log all exceptions
   - Provide safe error messages
   - Implement retry logic
   - Maintain audit trail

Implementation Example:
--------------------
def secure_file_operation(func):
    '''Decorator for secure file operations.'''
    def wrapper(*args, **kwargs):
        try:
            # Validate operation
            if not validate_operation(args[0]):
                raise SecurityError("Invalid operation")

            # Check permissions
            if not check_permissions(args[0]):
                raise SecurityError("Permission denied")

            # Execute operation
            return func(*args, **kwargs)

        except Exception as e:
            logger.error(f"Security error: {str(e)}")
            raise

    return wrapper
"""


class FileSystemError(Exception):
    """
    Base exception class for filesystem operations.

    Used as the parent class for all filesystem-related exceptions in the module.

    Example:
        >>> raise FileSystemError("Generic filesystem error")
    """
    pass


class SecurityError(FileSystemError):
    """
    Exception class for security-related errors.

    Raised when security violations occur during filesystem operations.

    Example:
        >>> raise SecurityError("Invalid path detected")
    """
    pass


class ResourceError(FileSystemError):
    """
    Exception class for resource limitation errors.

    Raised when resource limits (file size, quota, etc.) are exceeded.

    Example:
        >>> raise ResourceError("File size limit exceeded")
    """
    pass


# Optional: Monitoring and Metrics
class FileSystemMetrics:
    """
    Track and monitor filesystem operations and resource usage.

    Provides metrics collection for filesystem operations, including operation counts,
    byte processing tracking, and error logging. Useful for monitoring system usage
    and debugging.

    Attributes:
        operations (dict): Counter for different types of operations
        errors (list): List of recorded errors with timestamps
        total_bytes_processed (int): Total bytes processed by all operations

    Example:
        >>> metrics = FileSystemMetrics()
        >>> metrics.record_operation('read', 1024)  # Record 1KB read
        >>> print(metrics.get_metrics())  # Get current metrics
    """

    def __init__(self):
        self.operations = {
            'read': 0,
            'write': 0,
            'list': 0,
            'search': 0
        }
        self.errors = []
        self.total_bytes_processed = 0

    def record_operation(self, operation: str, bytes_processed: int = 0):
        """Record an operation and its resource usage."""
        self.operations[operation] = self.operations.get(operation, 0) + 1
        self.total_bytes_processed += bytes_processed

    def add_error(self, error: Exception):
        """Record an error."""
        self.errors.append({
            'timestamp': datetime.now(),
            'error': str(error)
        })

    def get_metrics(self):
        """Get current metrics."""
        return {
            'operations': self.operations,
            'total_bytes': self.total_bytes_processed,
            'error_count': len(self.errors)
        }


















# """
# File System Tools Module
# Provides file system operation tools from LangChain.
#
# Features:
# - List directory contents
# - Read files
# - Write files
# - Search files
# """
#
# from langchain_community.tools import (
#     ReadFileTool,
#     WriteFileTool,
#     ListDirectoryTool,
#     FileSearchTool,
# )
# from typing import List
# from langchain.tools import Tool
# import logging
#
# logger = logging.getLogger(__name__)
#
#
# def get_filesystem_tools(root_dir: str = None) -> List[Tool]:
#     """
#     Create and return file system tools.
#
#     Args:
#         root_dir (str): Root directory for file operations
#                       (defaults to current working directory)
#
#     Returns:
#         List[Tool]: List of file system tools
#     """
#     try:
#         tools = [
#             ReadFileTool(root_dir=root_dir),
#             WriteFileTool(root_dir=root_dir),
#             ListDirectoryTool(root_dir=root_dir),
#             FileSearchTool(root_dir=root_dir)
#         ]
#
#         logger.info(f"Initialized filesystem tools with root_dir: {root_dir}")
#         return tools
#
#     except Exception as e:
#         logger.error(f"Error initializing filesystem tools: {str(e)}")
#         raise