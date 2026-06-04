#!/usr/bin/env python3
"""
WordPress AI Content CLI Interface

Interactive command-line interface for the WordPress AI Content Portero agent.
Supports both chat mode and direct function execution.
"""

import argparse
import sys
import os
from datetime import datetime

# Add project root to path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

try:
    from portero.agent import process_user_query, get_agent
    from colorama import init, Fore, Style
    COLORAMA_AVAILABLE = True
except ImportError:
    COLORAMA_AVAILABLE = False
    Fore = type('FakeColors', (), {
        'BLUE': '', 'GREEN': '', 'YELLOW': '', 'RED': '', 'MAGENTA': '',
        'CYAN': '', 'WHITE': '', 'RESET': ''
    })
    Style = type('FakeStyle', (), {'RESET_ALL': ''})

# Initialize colorama if available
if COLORAMA_AVAILABLE:
    init(autoreset=True)


def print_header():
    """Print ASCII art header."""
    print(f"{Fore.CYAN}{'='*70}")
    print(f"{Fore.CYAN}  WordPress AI Content System - Portero Bridge")
    print(f"{Fore.CYAN}{'='*70}")
    print(f"{Fore.WHITE}  Version 0.1.0 - Interactive Content Creation CLI")
    print(f"{Fore.CYAN}{'='*70}{Style.RESET_ALL}\n")


def print_capabilities(agent=None):
    """Display all available capabilities and tools."""
    print(f"\n{Fore.MAGENTA}{'-'*70}.{Style.RESET_ALL}")
    print(f"{Fore.MAGENTA} {Fore.YELLOW}AVAILABLE CAPABILITIES")
    print(f"{Fore.MAGENTA}{'-'*70}.{Style.RESET_ALL}\n")
    
    capabilities = [
        {
            "name": "1. Generate Blog Post",
            "description": "Create complete SEO-optimized blog posts",
            "examples": [
                "generate blog post about AI in marketing with target keywords ['AI', 'marketing']",
                "create a 1500 word article in professional tone",
                "write a blog post about content strategy for social media"
            ]
        },
        {
            "name": "2. SEO Audit & Optimize",
            "description": "Analyze and improve content for SEO",
            "examples": [
                "seo audit and optimize my article about digital marketing",
                "analyze content: <paste your article here>",
                "optimize this post for keyword 'SEO tips'"
            ]
        },
        {
            "name": "3. Topic Research",
            "description": "Research topics for content planning",
            "examples": [
                "research topic: artificial intelligence trends 2024",
                "deep dive research on content marketing strategies",
                "analyze competitors in the blogging niche"
            ]
        },
        {
            "name": "4. Publish to WordPress",
            "description": "Publish content directly to WordPress",
            "examples": [
                "publish to WordPress: https://myblog.com, username: admin",
                "post my generated article to WordPress",
                "publish draft with tags 'AI', 'technology'"
            ]
        }
    ]
    
    for cap in capabilities:
        print(f"{Fore.GREEN}{cap['name']:20} {Style.RESET_ALL}{Fore.WHITE}{cap['description']}")
        for example in cap['examples']:
            print(f"{Fore.CYAN}   ↳ {Style.RESET_ALL}{example}")
        print()
    
    if agent:
        info = agent.get_system_info()
        print(f"{Fore.BLUE}Agent Configuration:{Style.RESET_ALL}")
        print(f"  Model: {info['model']}")
        print(f"  Temperature: {info['temperature']}")
        print(f"  Default Word Count: {info['default_word_count']}")
        print(f"  Memory: {'Enabled' if info['memory_enabled'] else 'Disabled'}")
        print(f"\n{Fore.GREEN}You can now start chatting!{Style.RESET_ALL}")


def process_direct_query(query: str, agent=None) -> dict:
    """Process a direct query through the agent."""
    try:
        result = process_user_query(query)
        return result
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "response": f"Error processing query: {e}"
        }


def chat_mode(agent=None):
    """Interactive chat mode."""
    print_header()
    print(f"{Fore.YELLOW}Chat Mode{Style.RESET_ALL}\n")
    print(f"{Fore.WHITE}Type your queries in natural language. Examples:{Style.RESET_ALL}")
    print(f"  - {Fore.CYAN}create a blog post about AI marketing{Style.RESET_ALL}")
    print(f"  - {Fore.CYAN}research content marketing strategies{Style.RESET_ALL}")
    print(f"  - {Fore.YELLOW}exit{Style.RESET_ALL} to quit\n")
    print("-" * 70, "\n")
    
    while True:
        try:
            # Get user input
            query = input(f"{Fore.GREEN}You>{Style.RESET_ALL} ").strip()
            
            # Check for exit commands
            if query.lower() in ['exit', 'quit', 'q', '.exit', '.quit']:
                print(f"\n{Fore.YELLOW}Goodbye! Happy creating!{Style.RESET_ALL}\n")
                break
            
            # Check for help commands
            if query.lower() in ['help', '.', 'capabilities', 'tools']:
                print()
                print_capabilities(agent)
                print()
                continue
            
            # Check for capabilities
            if query.lower() in ['capabilities', 'capabilities', 'list tools', 'show tools']:
                print()
                print_capabilities(agent)
                print()
                continue
            
            # Empty input
            if not query:
                continue
            
            # Process query
            print(f"\n{Fore.YELLOW}Agent is thinking...{Style.RESET_ALL}\n")
            result = process_direct_query(query, agent)
            
            # Display results
            if result and result.get("success"):
                response = result.get("response", "")
                print(f"{Fore.GREEN}Agent Response:{Style.RESET_ALL}")
                print("-" * 70)
                print(f"{Fore.WHITE}{response}{Style.RESET_ALL}")
                print("-" * 70 + "\n")
                
                # Show suggested tools if available
                if "suggested_tools" in result:
                    print(f"{Fore.BLUE}Suggested Tools:{Style.RESET_ALL}")
                    for tool in result["suggested_tools"]:
                        print(f"  • {tool}")
                    print()
                    
            elif result and not result.get("success"):
                print(f"{Fore.RED}{Fore.BOLD}Error:{Style.RESET_ALL}")
                print(f"{Fore.WHITE}{result.get('error', 'Unknown error')}{Style.RESET_ALL}\n")
            
            # Add separator
            print("-" * 70)
            
        except KeyboardInterrupt:
            print(f"\n{Fore.YELLOW}Interrupted. Type 'exit' to quit.{Style.RESET_ALL}")
        except EOFError:
            print(f"\n{Fore.YELLOW}Goodbye! Happy creating!{Style.RESET_ALL}\n")
            break


def execute_command(query: str, agent=None):
    """Execute a single command and print results."""
    print_header()
    print(f"\n{Fore.BLUE}Query: {Fore.WHITE}{query}{Style.RESET_ALL}\n")
    
    result = process_direct_query(query, agent)
    
    if result:
        if result.get("success"):
            response = result.get("response", "")
            print(f"{Fore.GREEN}Agent Response:{Style.RESET_ALL}")
            print("-" * 70)
            print(f"{Fore.WHITE}{response}{Style.RESET_ALL}")
            print("-" * 70)
            
            # Show suggested tools if available
            if "suggested_tools" in result:
                print(f"\n{Fore.BLUE}Suggested Tools:{Style.RESET_ALL}")
                for tool in result["suggested_tools"]:
                    print(f"  • {tool}")
                    
        else:
            print(f"\n{Fore.RED}Error:{Style.RESET_ALL}")
            print(f"{Fore.WHITE}{result.get('error', 'Unknown error')}{Style.RESET_ALL}")
    
    return result


def main():
    """Main entry point for CLI."""
    parser = argparse.ArgumentParser(
        description="WordPress AI Content CLI - Interactive Portero Bridge",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s --chat                                   # Start interactive chat mode
  %(prog)s --exec "create blog post about AI"       # Execute single command
  %(prog)s --info                                   # Show system information
  %(prog)s --help-capabilities                      # Show all available capabilities
        """,
        usage="%(prog)s [OPTION]"
    )
    
    parser.add_argument(
        '--chat', '-c',
        action='store_true',
        help='Start interactive chat mode (natural language queries)'
    )
    
    parser.add_argument(
        '--exec', '-e',
        type=str,
        help='Execute a single command/query',
        metavar='COMMAND'
    )
    
    parser.add_argument(
        '--info', '-i',
        action='store_true',
        help='Show system information and configuration'
    )
    
    parser.add_argument(
        '--capabilities', '-cp',
        action='store_true',
        help='Display all available capabilities and tools'
    )
    
    parser.add_argument(
        '--version', '-v',
        action='version',
        version='WordPress AI Content CLI v0.1.0'
    )
    
    parser.add_argument(
        '--quiet', '-q',
        action='store_true',
        help='Run in quiet mode (no decorations, just output)'
    )
    
    parser.add_argument(
        '--config',
        type=str,
        default=None,
        help='Path to configuration file (optional)'
    )
    
    args = parser.parse_args()
    
    # If no arguments provided, show help and enter chat mode
    if not any([args.chat, args.exec, args.info, args.capabilities]):
        # Print help with decorations
        print_header()
        print(f"{Fore.MAGENTA}WordPress AI Content CLI{Style.RESET_ALL}")
        print(f"{Fore.WHITE}Interactive interface for managing WordPress content creation.{Style.RESET_ALL}\n")
        print("-" * 70)
        print(f"{Fore.YELLOW}Usage:{Style.RESET_ALL}")
        print("  python main.py --chat                    # Start interactive mode")
        print("  python main.py --exec \"your query\"       # Execute single command")
        print("  python main.py --info                    # Show system info")
        print("  python main.py --capabilities            # List all capabilities")
        print("  python main.py --help-capabilities       # Show detailed usage examples")
        print("-" * 70)
        print(f"\n{Fore.GREEN}Entering chat mode by default...{Style.RESET_ALL}\n")
        
        try:
            agent = get_agent(args.config)
        except Exception as e:
            print(f"{Fore.RED}Warning: Could not initialize agent ({e}).{Style.RESET_ALL}")
            agent = None
        
        chat_mode(agent)
        return 0
    
    # Initialize agent
    try:
        agent = get_agent(args.config)
    except Exception as e:
        if not args.quiet:
            print(f"{Fore.RED}Error initializing agent: {e}{Style.RESET_ALL}")
        sys.exit(1)
    
    # Handle --info flag
    if args.info:
        if not args.quiet:
            print_header()
            print(f"{Fore.YELLOW}System Information{Style.RESET_ALL}")
            print("-" * 70)
        
        info = agent.get_system_info()
        output = f"""
Agent Configuration:
  • Agent Name: {info['agent_name']}
  • Model: {info['model']}
  • Temperature: {info['temperature']}
  • Max Tokens: {info['max_tokens']}
  
Available Tools:
  {', '.join(info['available_tools'])}
  
System Settings:
  • Default Word Count: {info['default_word_count']}
  • Web Search: {'Enabled' if info['enable_web_search'] else 'Disabled'}
  • Memory: {'Enabled' if info['memory_enabled'] else 'Disabled'}
  • LLM Proxy: {'Enabled' if info['llm_proxy_enabled'] else 'Disabled'}

Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
"""
        if not args.quiet:
            print(output)
            print(f"{Fore.GREEN}Done.{Style.RESET_ALL}")
        else:
            print(output)
        return 0
    
    # Handle --capabilities flag
    if args.capabilities:
        if not args.quiet:
            print_header()
            print(f"{Fore.YELLOW}Available Capabilities{Style.RESET_ALL}")
            print("-" * 70)
        
        print_capabilities(agent)
        if not args.quiet:
            print(f"{Fore.GREEN}Done.{Style.RESET_ALL}")
        else:
            for tool in agent.get_available_tools():
                print(f"{tool['name']}: {tool['description'][:100]}...")
        return 0
    
    # Handle --exec flag
    if args.exec:
        result = execute_command(args.exec, agent)
        return 0 if result and result.get("success") else 1
    
    # Default: chat mode
    if not args.quiet:
        print_header()
    chat_mode(agent)
    return 0


if __name__ == "__main__":
    sys.exit(main())
