"""
Bridge Layer for WordPress AI Content Portero Agent.

This package provides the bridge interfaces that connect humans and LLMs 
to the Portero agent through CLI and programmatic APIs.

Modules:
    - cli: Interactive command-line interface
    - api: Programmatic API for programmatic access

Example usage:
    from bridge import ask_portero
    response = ask_portero("Create a blog post about AI in marketing")
    print(response['output'])
"""

from bridge.api import (
    ask_portero,
    ask_portero_batch,
    ask_portero_with_context,
    get_tools_info,
    clear_agent_memory,
    get_agent_status,
    reset_agent
)

__all__ = [
    'ask_portero',
    'ask_portero_batch',
    'ask_portero_with_context',
    'get_tools_info',
    'clear_agent_memory',
    'get_agent_status',
    'reset_agent'
]

__version__ = '0.1.0'
__author__ = 'WordPress AI Content Team'
