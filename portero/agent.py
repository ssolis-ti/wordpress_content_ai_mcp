"""Portero agent configuration for WordPress AI Content system.

This module configures the LLM agent with all available tools and system prompt.
The agent uses LiteLLM proxy at the configured endpoint.
"""

import os
import logging
from typing import List, Dict, Any, Optional
from pathlib import Path

# Import Portero components
try:
    from portero.agent import Agent
    from portero.memory import MemoryManager
    from portero.llm_proxy import LiteLLMProxy
except ImportError:
    # Define minimal classes for compatibility
    class Agent:
        """Minimal Agent class for compatibility."""
        def __init__(self, **kwargs):
            self.config = kwargs
    
    class MemoryManager:
        """Minimal MemoryManager class for compatibility."""
        def __init__(self, **kwargs):
            self.config = kwargs
    
    class LiteLLMProxy:
        """Minimal LiteLLMProxy class for compatibility."""
        def __init__(self, **kwargs):
            self.config = kwargs

# Import our tools
from portero.tools import (
    generate_blog_post,
    seo_audit_and_optimize,
    research_topic,
    publish_to_wordpress
)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# System prompt based on manifest.yaml
SYSTEM_PROMPT = """You are an expert WordPress Content Strategist, SEO Specialist, and professional ghostwriter. 
Your goal is to create engaging, SEO-optimized, factually accurate content that ranks well and drives traffic. 
Always consider target audience, brand voice, and conversion elements.

CAPABILITIES:
1. GENERATE BLOG POSTS: Create complete, SEO-optimized blog posts from topics and keywords
   - Input: Topic, target keywords, word count, tone, target audience
   - Output: Full markdown content with frontmatter, headings, meta description, image suggestions
   - Use: generate_blog_post(topic, target_keywords, word_count=1200, tone="professional", target_audience="general")

2. SEO AUDIT AND OPTIMIZATION: Analyze and improve existing content for SEO
   - Input: Content text, primary keyword, secondary keywords
   - Output: SEO score, recommendations, optimized version
   - Use: seo_audit_and_optimize(content, primary_keyword, secondary_keywords)

3. TOPIC RESEARCH: Conduct comprehensive research on any topic
   - Input: Topic, research depth (basic/comprehensive)
   - Output: Key findings, competitor analysis, trends, sources, recommendations
   - Use: research_topic(topic, depth="basic")

4. WORDPRESS PUBLISHING: Publish content directly to WordPress
   - Input: Content (from generate_blog_post), WordPress credentials, status, categories, tags
   - Output: Publishing result with post ID and URL
   - Use: publish_to_wordpress(content, wp_url, username, app_password, status="draft", categories=None, tags=None)

5. IMAGE GENERATION: Create high-quality visual assets using fal.ai
   - Input: Image prompt, size (optional)
   - Output: Image URL and metadata
   - Use: generate_image_asset(prompt, image_size="landscape_4_3")

GUIDELINES:
- Always start by understanding the user's content goals and target audience
- For blog posts, suggest optimal word counts based on topic complexity (800-3000 words)
- Ensure all content follows SEO best practices (headings, keyword density, meta descriptions)
- When researching, provide actionable insights and content recommendations
- Before publishing, verify WordPress credentials and test with draft status first
- Provide clear explanations of SEO scores and optimization recommendations
- Consider the brand voice specified by the user (professional, casual, authoritative, etc.)
- Always include calls-to-action and conversion elements where appropriate
- Suggest relevant images and multimedia to enhance content
- Provide content structure recommendations (H1, H2, bullet points, etc.)

WORKFLOW EXAMPLES:
1. Complete content creation: research_topic → generate_blog_post → seo_audit_and_optimize → publish_to_wordpress
2. Content optimization: seo_audit_and_optimize on existing content
3. Quick publishing: generate_blog_post → publish_to_wordpress
4. Research only: research_topic for content planning

REMEMBER:
- You are an expert in WordPress content strategy and SEO
- Always aim for high-quality, engaging, and valuable content
- Consider the user's specific needs and constraints
- Provide step-by-step guidance when needed
- Be proactive in suggesting improvements and optimizations
- Maintain brand consistency across all content
- Prioritize user experience and readability
"""


class WpContentAgent:
    """Main agent for WordPress AI Content system."""
    
    def __init__(self, config_path: Optional[str] = None):
        """
        Initialize the WordPress content agent.
        
        Args:
            config_path: Optional path to configuration file
        """
        self.config = self._load_config(config_path)
        self.tools = self._initialize_tools()
        self.llm_proxy = self._initialize_llm()
        self.memory_manager = self._initialize_memory()
        self.agent = self._initialize_agent()
        
    def _load_config(self, config_path: Optional[str] = None) -> Dict[str, Any]:
        """Load configuration from file or use defaults."""
        default_config = {
            "llm_provider": "google",
            "model": "gemini/gemini-1.5-flash",
            "temperature": 0.7,
            "max_tokens": 4000,
            "liteLLM_endpoint": "http://localhost:4000",
            "memory_type": "contextual",
            "memory_file": "portero/memory/app_context.md",
            "memory_persistence": True,
            "default_word_count": 1500,
            "enable_web_search": True,
            "storage_backend": "json",
            "data_path": "data/"
        }
        
        # TODO: Load from config file if provided
        return default_config
    
    def _initialize_tools(self) -> List:
        """Initialize all available tools."""
        tools = [
            generate_blog_post,
            seo_audit_and_optimize,
            research_topic,
            publish_to_wordpress
        ]
        
        logger.info(f"Initialized {len(tools)} tools")
        return tools
    
    def _initialize_llm(self):
        """Initialize LiteLLM proxy."""
        try:
            llm_proxy = LiteLLMProxy(
                endpoint=self.config["liteLLM_endpoint"],
                provider=self.config["llm_provider"],
                model=self.config["model"],
                temperature=self.config["temperature"],
                max_tokens=self.config["max_tokens"]
            )
            logger.info(f"Initialized LLM proxy: {self.config['model']} via {self.config['liteLLM_endpoint']}")
            return llm_proxy
        except Exception as e:
            logger.error(f"Failed to initialize LLM proxy: {e}")
            # Fallback to direct OpenAI if LiteLLM not available
            logger.info("Using direct OpenAI configuration")
            return None
    
    def _initialize_memory(self):
        """Initialize memory manager."""
        try:
            memory_manager = MemoryManager(
                memory_type=self.config["memory_type"],
                memory_file=self.config["memory_file"],
                persistence=self.config["memory_persistence"]
            )
            logger.info(f"Initialized memory manager: {self.config['memory_type']}")
            return memory_manager
        except Exception as e:
            logger.error(f"Failed to initialize memory manager: {e}")
            return None
    
    def _initialize_agent(self):
        """Initialize the main agent."""
        try:
            agent = Agent(
                name="WordPress Content Strategist",
                role="Expert WordPress content creator and SEO specialist",
                system_prompt=SYSTEM_PROMPT,
                tools=self.tools,
                llm_proxy=self.llm_proxy,
                memory_manager=self.memory_manager,
                config={
                    "enable_web_search": self.config["enable_web_search"],
                    "default_word_count": self.config["default_word_count"],
                    "verbose": True
                }
            )
            logger.info("Initialized WordPress Content Agent")
            return agent
        except Exception as e:
            logger.error(f"Failed to initialize agent: {e}")
            # Create minimal agent for compatibility
            return Agent(
                name="WordPress Content Strategist",
                role="Expert WordPress content creator and SEO specialist",
                system_prompt=SYSTEM_PROMPT,
                tools=self.tools,
                config={"verbose": True}
            )
    
    def process_query(self, query: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Process a user query using the agent.
        
        Args:
            query: User query in natural language
            context: Optional context dictionary
            
        Returns:
            Agent response with tool calls and results
        """
        try:
            logger.info(f"Processing query: {query[:100]}...")
            
            # Prepare context
            agent_context = {
                "query": query,
                "timestamp": self._get_timestamp(),
                "config": {
                    "default_word_count": self.config["default_word_count"],
                    "enable_web_search": self.config["enable_web_search"]
                }
            }
            
            if context:
                agent_context.update(context)
            
            # Process with agent
            # Note: Actual implementation depends on Portero framework
            # This is a simplified version
            response = self._simulate_agent_response(query, agent_context)
            
            logger.info(f"Query processed successfully")
            return response
            
        except Exception as e:
            logger.error(f"Error processing query: {e}")
            return {
                "success": False,
                "error": str(e),
                "response": "I encountered an error processing your request. Please try again."
            }
    
    def _simulate_agent_response(self, query: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Simulate agent response for demonstration.
        In production, this would use the actual Portero agent framework.
        """
        query_lower = query.lower()
        
        # Pattern matching for tool selection
        if any(word in query_lower for word in ["generate", "create", "write", "blog", "post", "article"]):
            return self._handle_content_generation(query, context)
        elif any(word in query_lower for word in ["seo", "optimize", "audit", "analyze", "improve"]):
            return self._handle_seo_audit(query, context)
        elif any(word in query_lower for word in ["research", "study", "analyze topic", "investigate"]):
            return self._handle_research(query, context)
        elif any(word in query_lower for word in ["publish", "wordpress", "post to", "upload"]):
            return self._handle_publishing(query, context)
        else:
            return {
                "success": True,
                "response": "I can help you with WordPress content creation and management. I can:\n"
                           "1. Generate SEO-optimized blog posts\n"
                           "2. Audit and optimize existing content for SEO\n"
                           "3. Research topics for content planning\n"
                           "4. Publish content directly to WordPress\n\n"
                           f"For your query: '{query}'\n\n"
                           "Which of these capabilities would you like to use? "
                           "Please provide more details about your content needs.",
                "suggested_tools": ["generate_blog_post", "seo_audit_and_optimize", "research_topic", "publish_to_wordpress"]
            }
    
    def _handle_content_generation(self, query: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Handle content generation queries."""
        return {
            "success": True,
            "response": "I can generate SEO-optimized blog posts for you. "
                       "I'll need:\n"
                       "1. The main topic\n"
                       "2. Target keywords (for SEO)\n"
                       "3. Desired word count (default: 1200)\n"
                       "4. Tone (professional, casual, authoritative, etc.)\n"
                       "5. Target audience\n\n"
                       "Example usage: generate_blog_post('Artificial Intelligence in Marketing', "
                       "['AI', 'marketing automation', 'personalization'], word_count=1500, "
                       "tone='professional', target_audience='Marketing professionals')",
            "tool": "generate_blog_post",
            "required_params": ["topic", "target_keywords"],
            "optional_params": ["word_count", "tone", "target_audience"]
        }
    
    def _handle_seo_audit(self, query: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Handle SEO audit queries."""
        return {
            "success": True,
            "response": "I can perform comprehensive SEO analysis and optimization. "
                       "I'll need:\n"
                       "1. The content text to analyze\n"
                       "2. Primary keyword\n"
                       "3. Secondary keywords (optional)\n\n"
                       "Example usage: seo_audit_and_optimize('# Your Content Here...', "
                       "'digital marketing', ['SEO', 'social media', 'content marketing'])",
            "tool": "seo_audit_and_optimize",
            "required_params": ["content", "primary_keyword"],
            "optional_params": ["secondary_keywords"]
        }
    
    def _handle_research(self, query: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Handle research queries."""
        return {
            "success": True,
            "response": "I can conduct in-depth research on any topic. "
                       "I'll need:\n"
                       "1. The topic to research\n"
                       "2. Research depth (basic or comprehensive, default: basic)\n\n"
                       "Example usage: research_topic('Content Marketing', depth='comprehensive')",
            "tool": "research_topic",
            "required_params": ["topic"],
            "optional_params": ["depth"]
        }
    
    def _handle_publishing(self, query: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Handle WordPress publishing queries."""
        return {
            "success": True,
            "response": "I can publish content directly to WordPress. "
                       "I'll need:\n"
                       "1. Content (from generate_blog_post)\n"
                       "2. WordPress URL\n"
                       "3. WordPress username\n"
                       "4. WordPress application password\n"
                       "5. Status (draft or publish, default: draft)\n"
                       "6. Categories (optional)\n"
                       "7. Tags (optional)\n\n"
                       "Example usage: publish_to_wordpress(content_dict, "
                       "'https://example.com', 'admin', 'xxxx xxxx xxxx xxxx', "
                       "status='publish', categories=['Marketing'], tags=['AI'])",
            "tool": "publish_to_wordpress",
            "required_params": ["content", "wp_url", "username", "app_password"],
            "optional_params": ["status", "categories", "tags"]
        }
    
    def _get_timestamp(self) -> str:
        """Get current timestamp."""
        from datetime import datetime
        return datetime.now().isoformat()
    
    def get_available_tools(self) -> List[Dict[str, Any]]:
        """Get list of available tools with descriptions."""
        tools_info = []
        
        for tool_func in self.tools:
            tool_info = {
                "name": getattr(tool_func, "__tool_name__", tool_func.__name__),
                "description": getattr(tool_func, "__tool_description__", tool_func.__doc__ or ""),
                "signature": self._get_tool_signature(tool_func)
            }
            tools_info.append(tool_info)
        
        return tools_info
    
    def _get_tool_signature(self, tool_func) -> str:
        """Get tool signature for documentation."""
        import inspect
        
        try:
            sig = inspect.signature(tool_func)
            params = []
            
            for param_name, param in sig.parameters.items():
                if param_name == 'self':
                    continue
                    
                if param.default == inspect.Parameter.empty:
                    params.append(param_name)
                else:
                    default_str = repr(param.default)
                    params.append(f"{param_name}={default_str}")
            
            return f"{tool_func.__name__}({', '.join(params)})"
        except:
            return f"{tool_func.__name__}(...)"
    
    def get_system_info(self) -> Dict[str, Any]:
        """Get system information and configuration."""
        return {
            "agent_name": "WordPress Content Strategist",
            "model": self.config["model"],
            "temperature": self.config["temperature"],
            "max_tokens": self.config["max_tokens"],
            "available_tools": [tool.__name__ for tool in self.tools],
            "default_word_count": self.config["default_word_count"],
            "enable_web_search": self.config["enable_web_search"],
            "memory_enabled": self.memory_manager is not None,
            "llm_proxy_enabled": self.llm_proxy is not None
        }


# Global agent instance
_agent_instance: Optional[WpContentAgent] = None


def get_agent(config_path: Optional[str] = None) -> WpContentAgent:
    """
    Get or create global WordPress content agent instance.
    
    Args:
        config_path: Optional path to configuration file
        
    Returns:
        WpContentAgent instance
    """
    global _agent_instance
    if _agent_instance is None:
        _agent_instance = WpContentAgent(config_path)
    return _agent_instance


def create_agent(config_path: Optional[str] = None) -> WpContentAgent:
    """Helper function to create a new agent instance."""
    return WpContentAgent(config_path)


def process_user_query(query: str, config_path: Optional[str] = None) -> Dict[str, Any]:
    """
    Process a user query using the WordPress content agent.
    
    Args:
        query: User query in natural language
        config_path: Optional path to configuration file
        
    Returns:
        Agent response
    """
    agent = get_agent(config_path)
    return agent.process_query(query)


if __name__ == "__main__":
    """Test the agent functionality."""
    print("WordPress Content Agent - Test Mode")
    print("=" * 50)
    
    # Initialize agent
    agent = WpContentAgent()
    
    # Display system info
    info = agent.get_system_info()
    print(f"\nAgent: {info['agent_name']}")
    print(f"Model: {info['model']}")
    print(f"Temperature: {info['temperature']}")
    print(f"Available tools: {', '.join(info['available_tools'])}")
    
    # Display available tools with descriptions
    print("\nAvailable Tools:")
    print("-" * 30)
    for tool_info in agent.get_available_tools():
        print(f"\n{tool_info['name']}:")
        print(f"  Signature: {tool_info['signature']}")
        desc_lines = tool_info['description'].strip().split('\n')
        if desc_lines:
            print(f"  Description: {desc_lines[0]}")
            for line in desc_lines[1:]:
                if line.strip():
                    print(f"               {line.strip()}")
    
    # Test queries
    test_queries = [
        "I need a blog post about AI in marketing",
        "Can you analyze my content for SEO?",
        "Research content marketing trends",
        "Publish my article to WordPress"
    ]
    
    print(f"\n\nExample Queries:")
    print("-" * 30)
    for query in test_queries:
        print(f"\nQuery: '{query}'")
        response = agent.process_query(query)
        print(f"Response: {response.get('response', 'No response')[:200]}...")
        if response.get('tool'):
            print(f"Suggested tool: {response['tool']}")