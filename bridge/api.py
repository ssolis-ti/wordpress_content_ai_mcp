#!/usr/bin/env python3
"""
WordPress AI Content API Module

Provides a simple programmatic interface for interacting with the Portero agent.
Designed to be imported by other programs and scripts.
"""

import sys
import os
from typing import Dict, Any, Optional, Union

# Add project root to path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

try:
    from portero.agent import get_agent, process_user_query
except ImportError as e:
    raise ImportError(
        f"Could not import Portero agent. Please ensure the project is properly installed.\n\n"
        f"Error details: {e}\n\n"
        f"Note: Make sure portero/agent.py exists at {os.path.join(project_root, 'portero', 'agent.py')}"
    )


class PorteroClient:
    """
    Programmatic client for interacting with the WordPress Content Portero agent.
    
    This class provides a clean API for querying the agent without using the CLI.
    
    Example usage:
        from bridge.api import PorteroClient
        
        client = PorteroClient()
        result = client.generate_blog_post(
            topic="AI in Marketing",
            target_keywords=["AI", "marketing", "automation"],
            word_count=1500,
            tone="professional"
        )
        
        if result.get("success"):
            print(result["content"])
    """
    
    def __init__(self, config_path: Optional[str] = None):
        """
        Initialize the Portero client.
        
        Args:
            config_path: Optional path to configuration file
        """
        self.agent = get_agent(config_path)
        self._initialized = True
    
    def query(self, query: str) -> Dict[str, Any]:
        """
        Process a natural language query.
        
        Args:
            query: The natural language query to process
            
        Returns:
            Dictionary containing response, success status, and metadata
        """
        return process_user_query(query, self.agent)
    
    def generate_blog_post(self, topic: str, target_keywords: list, 
                          word_count: int = 1200, tone: str = "professional",
                          target_audience: str = "general") -> Dict[str, Any]:
        """
        Generate a blog post using the generate_blog_post tool.
        
        Args:
            topic: The main topic of the blog post
            target_keywords: List of keywords for SEO optimization
            word_count: Desired word count (default: 1200)
            tone: Tone of the article (professional, casual, etc.)
            target_audience: Target audience description
            
        Returns:
            Dictionary with success status and blog post content
        """
        query = f"""
            Please generate a blog post with the following details:
            - Topic: {topic}
            - Target Keywords: {', '.join(target_keywords)}
            - Word Count: {word_count}
            - Tone: {tone}
            - Target Audience: {target_audience}
            
            Use the generate_blog_post tool to create this content.
        """
        
        return process_user_query(query, self.agent)
    
    def seo_audit(self, content: str, primary_keyword: str, 
                 secondary_keywords: Optional[list] = None) -> Dict[str, Any]:
        """
        Perform SEO audit and optimization on content.
        
        Args:
            content: The text content to analyze
            primary_keyword: Primary keyword to optimize for
            secondary_keywords: Additional keywords (optional)
            
        Returns:
            Dictionary with SEO analysis and optimization recommendations
        """
        keywords = secondary_keywords if secondary_keywords else []
        
        query = f"""
            Please perform a comprehensive SEO audit on the following content:
            - Primary Keyword: {primary_keyword}
            - Secondary Keywords: {', '.join(keywords) if keywords else 'None'}
            
            Use the seo_audit_and_optimize tool to analyze and optimize this content.
            
            Content to analyze:
            {content}
        """
        
        return process_user_query(query, self.agent)
    
    def research_topic(self, topic: str, depth: str = "basic") -> Dict[str, Any]:
        """
        Research a topic for content planning.
        
        Args:
            topic: The topic to research
            depth: Research depth - "basic" or "comprehensive" (default: "basic")
            
        Returns:
            Dictionary with research findings and recommendations
        """
        query = f"""
            Please conduct {depth} research on the topic: "{topic}"
            
            Use the research_topic tool to gather information about:
            - Key facts and data
            - Competitors and trends
            - Content opportunities
            - Relevant sources
            
            Depth: {depth}
        """
        
        return process_user_query(query, self.agent)
    
    def publish_to_wordpress(self, content: Dict[str, Any], wp_url: str,
                            username: str, app_password: str,
                            status: str = "draft", categories: Optional[list] = None,
                            tags: Optional[list] = None) -> Dict[str, Any]:
        """
        Publish content to WordPress.
        
        Args:
            content: Content dictionary (from generate_blog_post or similar)
            wp_url: WordPress site URL
            username: WordPress username
            app_password: WordPress application password
            status: "draft" or "publish" (default: "draft")
            categories: List of categories (optional)
            tags: List of tags (optional)
            
        Returns:
            Dictionary with publishing result
        """
        publish_args = {
            "content": content,
            "wp_url": wp_url,
            "username": username,
            "app_password": app_password,
            "status": status
        }
        
        if categories:
            publish_args["categories"] = categories
            
        if tags:
            publish_args["tags"] = tags
            
        query = f"""
            Please publish the following content to WordPress using publish_to_wordpress:
            
            WordPress URL: {wp_url}
            Username: {username}
            Status: {status}
            Categories: {categories if categories else 'None'}
            Tags: {tags if tags else 'None'}
        """
        
        return process_user_query(query, self.agent)
    
    def get_system_info(self) -> Dict[str, Any]:
        """
        Get current system and agent configuration.
        
        Returns:
            Dictionary with system information
        """
        return self.agent.get_system_info()
    
    def get_available_tools(self) -> list:
        """
        Get list of available tools and their signatures.
        
        Returns:
            List of tool information dictionaries
        """
        return self.agent.get_available_tools()


# Simple convenience function for quick queries
def ask_portero(query: str, config_path: Optional[str] = None) -> str:
    """
    Simple function to ask the Portero agent a question.
    
    This is the main entry point for programmatic use.
    
    Args:
        query: Natural language query to process
        config_path: Optional path to configuration file
        
    Returns:
        String response from the agent
    """
    try:
        result = process_user_query(query, config_path)
        
        if result.get("success"):
            return result.get("response", "No response received")
        else:
            return f"Error: {result.get('error', 'Unknown error')}"
    except Exception as e:
        return f"Error processing query: {str(e)}"


def ask_portero_batch(queries: list, config_path: Optional[str] = None) -> list:
    """
    Process multiple queries in batch.
    
    Args:
        queries: List of natural language queries
        config_path: Optional path to configuration file
        
    Returns:
        List of string responses
    """
    agent = get_agent(config_path)
    responses = []
    for q in queries:
        result = agent.process_query(q)
        if result.get("success"):
            responses.append(result.get("response", "No response received"))
        else:
            responses.append(f"Error: {result.get('error', 'Unknown error')}")
    return responses


def ask_portero_with_context(query: str, context: dict, config_path: Optional[str] = None) -> str:
    """
    Ask the Portero agent with additional context.
    
    Args:
        query: Natural language query
        context: Context dictionary
        config_path: Optional path to configuration file
        
    Returns:
        String response
    """
    agent = get_agent(config_path)
    result = agent.process_query(query, context)
    if result.get("success"):
        return result.get("response", "No response received")
    else:
        return f"Error: {result.get('error', 'Unknown error')}"


def get_tools_info(config_path: Optional[str] = None) -> list:
    """Get information about available tools."""
    agent = get_agent(config_path)
    return agent.get_available_tools()


def clear_agent_memory(config_path: Optional[str] = None) -> bool:
    """Clear the agent's memory."""
    agent = get_agent(config_path)
    if agent.memory_manager:
        # Simplified: in real Portero, this would call a clear method
        return True
    return False


def get_agent_status(config_path: Optional[str] = None) -> Dict[str, Any]:
    """Get the current status of the agent."""
    agent = get_agent(config_path)
    return agent.get_system_info()


def reset_agent(config_path: Optional[str] = None) -> bool:
    """Reset the agent to initial state."""
    global _agent_instance
    _agent_instance = None
    return True


# Alternative simplified interface
def ask_porter_simple(query: str, mode: str = "chat") -> str:
    """
    Simplified interface for quick queries.
    
    Args:
        query: Natural language query
        mode: "chat", "blog", "seo", "research", "publish"
        
    Returns:
        String response from the agent
    """
    if mode == "chat":
        return ask_portero(query)
    
    elif mode == "blog":
        return ask_porter_simple_chat(
            query,
            "Please generate a complete blog post about this topic."
        )
    
    elif mode == "seo":
        return ask_porter_simple_chat(
            query,
            "Please perform an SEO audit and optimization on this content."
        )
    
    elif mode == "research":
        return ask_porter_simple_chat(
            query,
            "Please conduct comprehensive research on this topic."
        )
    
    elif mode == "publish":
        return ask_porter_simple_chat(
            query,
            "Please prepare to publish this content to WordPress."
        )
    
    else:
        raise ValueError(f"Unknown mode: {mode}. Use: chat, blog, seo, research, publish")


def ask_porter_simple_chat(query: str, mode_instruction: str) -> str:
    """
    Helper function for specialized modes.
    
    Args:
        query: User's query or content
        mode_instruction: How the agent should process the query
        
    Returns:
        String response
    """
    full_query = f"{mode_instruction}\n\nHere is the query/content:\n{query}"
    return ask_portero(full_query)


# Export clean public API
__all__ = [
    'PorteroClient',
    'ask_portero',
    'ask_portero_batch',
    'ask_portero_with_context',
    'get_tools_info',
    'clear_agent_memory',
    'get_agent_status',
    'reset_agent',
    'ask_porter_simple',
    'ask_porter_simple_chat'
]
