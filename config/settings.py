# config/settings.py

"""
Configuration Settings Module
===========================

Central configuration management for the agent framework. Contains all global settings,
environment-specific configurations, and customizable parameters.

Configuration Categories:
----------------------
1. Proxy Settings
2. AWS Configuration
3. Model Parameters
4. Tool Settings
5. Environment-specific Configurations
6. Memory Management
7. Agent Behavior Settings

Usage:
------
Basic import:
    >>> from config.settings import AWS_CONFIG, DEFAULT_MODEL_KWARGS
    >>> agent_config = AWS_CONFIG

Environment-specific settings:
    >>> from config.settings import AGENT_CONFIG
    >>> max_iterations = AGENT_CONFIG['max_iterations']

Memory configuration:
    >>> from config.settings import CURRENT_MEMORY_CONFIG
    >>> memory_type = CURRENT_MEMORY_CONFIG['memory_type']
"""

from botocore.config import Config
from typing import Dict, Any
import os

# Proxy Configuration
# ------------------
PROXY_CONFIG = {
    'http': "http://webproxy.ext.ti.com:80",
    'https': "http://webproxy.ext.ti.com:80"
}

# AWS Configuration
# ---------------
AWS_CONFIG = Config(
    connect_timeout=30,  # Connection timeout in seconds
    read_timeout=30,  # Read timeout in seconds
    retries={'max_attempts': 2},  # Retry configuration
    proxies={
        'http': "http://webproxy.ext.ti.com:80",
        'https': "http://webproxy.ext.ti.com:80"
    }
)

# Default Model Parameters
# ----------------------
DEFAULT_MODEL_KWARGS = {
    "temperature": 0.7,  # Controls response randomness (0.0-1.0)
    "max_tokens": 512,  # Maximum tokens in response
}

# Tool Configuration
# ----------------
ENABLED_TOOLS = {
    'calculator': False,  # Basic calculation capabilities
    'file_reader': False,  # File reading operations
    'wikipedia': False,  # Wikipedia search and retrieval
    'llm_math': False,  # Advanced mathematical operations
    'file_writer': False,  # File writing operations
    'filesystem': True  # Filesystem operations (enabled by default)
}

# Filesystem Configuration
# ----------------------
"""
Filesystem Security and Configuration Settings
===========================================

Controls filesystem access, security, and operational parameters across different
environments. Configuration adapts based on the ENVIRONMENT setting.

Structure:
---------
1. Basic Settings:
   - root_dir: Base directory for all operations
   - allowed_operations: Permitted filesystem actions
   - max_file_size: File size limitations

2. Security Settings:
   - enable_security: Master switch for security features
   - validate_paths: Path validation enforcement
   - restricted_patterns: Blocked path patterns
   - allowed_extensions: Permitted file types
   - monitor_operations: Operation tracking
   - log_all_operations: Detailed logging

Environment Behaviors:
-------------------
Development:
    - Security disabled
    - No path validation
    - All operations allowed
    - No file size limits
    - Minimal logging

Production:
    - Full security enabled
    - Strict path validation
    - Limited file extensions
    - Size limits enforced
    - Complete operation logging

Testing:
    - Basic security enabled
    - Path validation active
    - Minimal logging
    - Reduced size limits

Usage:
-----
    from config.settings import FILESYSTEM_CONFIG

    # Check if operation is allowed
    if 'write' in FILESYSTEM_CONFIG['allowed_operations']:
        # Perform write operation

    # Verify security status
    if FILESYSTEM_CONFIG['security']['enable_security']:
        # Perform security checks
"""

FILESYSTEM_CONFIG = {
    'root_dir': None,        # None means current working directory
    'allowed_operations': [   # Allow all operations by default
        'read',              # Permission to read files
        'write',             # Permission to create/modify files
        'list',             # Permission to list directory contents
        'search'            # Permission to search for files
    ],
    'max_file_size': None,   # No file size limit in development
    'security': {
        'enable_security': False,    # Master switch for security features
        'validate_paths': False,     # Path validation enforcement
        'restricted_patterns': [],   # Patterns to block (e.g., '..' for parent dir)
        'allowed_extensions': None,  # None means all extensions allowed
        'monitor_operations': False, # Track operation metrics
        'log_all_operations': False  # Record all filesystem activities
    }
}


# Environment-specific configurations
FILESYSTEM_ENV_CONFIGS = {
    'development': {
        'security': {
            'enable_security': False,     # Disable all security in development
            'validate_paths': False,
            'log_all_operations': False
        }
    },
    'production': {
        'max_file_size': 5 * 1024 * 1024,   # 5MB in production
        'security': {
            'enable_security': True,      # Enable security in production
            'validate_paths': True,
            'log_all_operations': True,
            'restricted_patterns': ['..', '~', '\$', '|', ';', '&'],
            'allowed_extensions': ['.txt', '.log', '.md', '.json', '.yaml', '.yml', '.csv', '.dat']
        }
    },
    'testing': {
        'security': {
            'enable_security': True,      # Enable basic security in testing
            'validate_paths': True,
            'log_all_operations': False
        }
    }
}

# Environment Configuration
# -----------------------
ENVIRONMENT = os.getenv('ENV', 'development')  # Default to development

# # Update filesystem config based on environment
FILESYSTEM_CONFIG.update(FILESYSTEM_ENV_CONFIGS.get(ENVIRONMENT, {}))

# Agent Configuration by Environment
# -------------------------------
AGENT_ENV_CONFIGS = {
    'development': {
        'max_iterations': 15,  # Maximum number of thought iterations
        'max_execution_time': None,  # No time limit
        'early_stopping_method': 'generate',
        'handle_parsing_errors': True
    },
    'production': {
        'max_iterations': 10,  # Limited iterations for production
        'max_execution_time': 30.0,  # 30 seconds timeout
        'early_stopping_method': 'force',
        'handle_parsing_errors': True
    },
    'testing': {
        'max_iterations': 5,  # Minimal iterations for testing
        'max_execution_time': 10.0,  # Quick timeout for tests
        'early_stopping_method': 'force',
        'handle_parsing_errors': True
    }
}

# Get environment-specific agent configuration
AGENT_CONFIG = AGENT_ENV_CONFIGS.get(ENVIRONMENT, AGENT_ENV_CONFIGS['development'])

# Memory Configuration
# ------------------
MEMORY_CONFIG = {
    'development': {
        'max_messages': 100,
        'memory_type': 'summary'  # Uses LLM for conversation summarization
    },
    'production': {
        'max_messages': 50,
        'memory_type': 'limited'  # Limited message history
    },
    'testing': {
        'max_messages': 10,
        'memory_type': 'summary'  # Summarized history for testing
    }
}

"""
Memory Types Description:
----------------------
buffer:  Simple storage of all messages
         - Good for short conversations
         - Useful for debugging
         - No processing overhead

limited: Fixed-size message history
         - Keeps only last N messages
         - Memory efficient
         - Good for long-running agents

summary: LLM-based conversation summarization
         - Maintains context while reducing storage
         - Uses LLM for summarization
         - Best for long, context-dependent conversations
"""

# Get environment-specific memory configuration
CURRENT_MEMORY_CONFIG = MEMORY_CONFIG.get(ENVIRONMENT, MEMORY_CONFIG['development'])

"""
Configuration Best Practices:
--------------------------
1. Environment Variables:
   - Use environment variables for sensitive settings
   - Provide defaults for development
   - Document required variables

2. Security:
   - Never commit sensitive credentials
   - Use secure parameter storage in production
   - Implement access controls

3. Validation:
   - Validate configurations at startup
   - Provide clear error messages
   - Implement fallback values

4. Documentation:
   - Document all configuration options
   - Provide usage examples
   - Explain impact of settings

Example Validation Implementation:
-------------------------------
def validate_config():
    '''Validate critical configuration settings.'''
    if ENVIRONMENT not in AGENT_ENV_CONFIGS:
        raise ValueError(f"Invalid environment: {ENVIRONMENT}")

    if CURRENT_MEMORY_CONFIG['max_messages'] < 1:
        raise ValueError("max_messages must be positive")

Example Security Implementation:
-----------------------------
def get_secure_config():
    '''Get secure configuration from parameter store.'''
    if ENVIRONMENT == 'production':
        # Get from secure parameter store
        pass
    return DEFAULT_CONFIG
"""

# Future Extensions (Commented Out)
"""
# Environment-specific configurations
ENV_CONFIGS = {
    'development': {
        'debug': True,
        'log_level': 'DEBUG',
        'retry_attempts': 2
    },
    'production': {
        'debug': False,
        'log_level': 'INFO',
        'retry_attempts': 3
    }
}

# Model-specific configurations
MODEL_CONFIGS = {
    'claude-3-sonnet': {
        'temperature': 0.7,
        'max_tokens': 512,
        'top_p': 1
    },
    'claude-3-opus': {
        'temperature': 0.5,
        'max_tokens': 1024,
        'top_p': 0.9
    }
}

# Function to get environment configuration
def get_environment_config() -> Dict[str, Any]:
    '''Get configuration for current environment.'''
    return ENV_CONFIGS.get(ENVIRONMENT, ENV_CONFIGS['development'])

# Function to get model configuration
def get_model_config(model_name: str) -> Dict[str, Any]:
    '''Get configuration for specific model.'''
    return MODEL_CONFIGS.get(model_name, DEFAULT_MODEL_KWARGS)
"""
