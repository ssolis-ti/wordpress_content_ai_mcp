#!/usr/bin/env python3
"""
WordPress AI Content System - Main Entry Point

This is the central entry point for the AI Content System.
It ties together the CLI interface, API module, and Portero agent.

Usage:
    python main.py --chat                 # Start interactive chat mode
    python main.py --exec "your query"    # Execute single command
    python main.py --info                 # Show system information
    python main.py --capabilities         # List all available capabilities

For programmatic use, import from bridge.api:
    from bridge.api import ask_portero, PorteroClient
    
    # Simple query
    response = ask_portero("Create a blog post about AI")
    
    # Or use the full client
    client = PorteroClient()
    result = client.generate_blog_post("AI Marketing", ["AI", "marketing"])
"""

import sys
import os
from datetime import datetime

# Add project root to path
project_root = os.path.dirname(os.path.abspath(__file__))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

# Import colorama for colored output (optional, falls back gracefully)
try:
    from colorama import init, Fore, Style
    init(autoreset=True)
    COLORAMA_AVAILABLE = True
except ImportError:
    COLORAMA_AVAILABLE = False
    
    # Fallback colors if colorama not available
    class Colors:
        BLUE = ''
        GREEN = ''
        YELLOW = ''
        RED = ''
        MAGENTA = ''
        CYAN = ''
        WHITE = ''
        RESET = ''
    Fore = Colors
    Style = type('Style', (), {'RESET_ALL': ''})


# Import CLI module
from bridge.cli import chat_mode, execute_command, print_header
from bridge.api import ask_portero, PorteroClient

# Import agent for system info
try:
    from portero.agent import get_agent
    from portero.tools import (
        generate_blog_post,
        seo_audit_and_optimize,
        research_topic,
        publish_to_wordpress
    )
    AGENT_AVAILABLE = True
except ImportError:
    AGENT_AVAILABLE = False


def get_version():
    """Get system version."""
    return "0.1.0"


def print_banner():
    """Print system banner."""
    if COLORAMA_AVAILABLE:
        print(f"\n{Fore.CYAN}╔" + "═" * 78 + "╗")
        print(f"║{Fore.WHITE} WordPress AI Content System{Fore.CYAN}{' ' * 46}║")
        print(f"║{Fore.WHITE} Powered by Portero Agent{Fore.CYAN}{' ' * 47}║")
        print(f"║{Fore.WHITE} Version {get_version()}{Fore.CYAN}{' ' * 50}║")
        print(f"{Fore.CYAN}╚" + "═" * 78 + "╝{Style.RESET_ALL}")
    else:
        print("\n" + "=" * 80)
        print("WordPress AI Content System - Powered by Portero Agent")
        print(f"Version {get_version()}")
        print("=" * 80)
    

def print_help():
    """Print help message."""
    print_banner()
    
    print(f"\n{Fore.YELLOW}WordPress AI Content CLI - Interactive Interface{Style.RESET_ALL}\n")
    
    print(f"{Fore.MAGENTA}{'Usage':<30} {Fore.WHITE}Description{Style.RESET_ALL}")
    print(f"{Fore.CYAN}{'─' * 70}{Style.RESET_ALL}")
    
    print(f"\n{Fore.GREEN}--chat, -c{Style.RESET_ALL}             {Fore.WHITE}Start interactive chat mode (natural language queries){Style.RESET_ALL}")
    print(f"{Fore.GREEN}--exec, -e {Style.RESET_ALL}'QUERY'      {Fore.WHITE}Execute a single command/query{Style.RESET_ALL}")
    print(f"{Fore.GREEN}--info, -i{Style.RESET_ALL}              {Fore.WHITE}Show system information and configuration{Style.RESET_ALL}")
    print(f"{Fore.GREEN}--capabilities, -cp{Style.RESET_ALL}     {Fore.WHITE}Display all available capabilities and tools{Style.RESET_ALL}")
    print(f"{Fore.GREEN}--help-capabilities{Style.RESET_ALL}       {Fore.WHITE}Show detailed usage examples for each capability{Style.RESET_ALL}")
    print(f"{Fore.GREEN}--quiet, -q{Style.RESET_ALL}             {Fore.WHITE}Run in quiet mode (no decorations, just output){Style.RESET_ALL}")
    print(f"{Fore.GREEN}--config{Style.RESET_ALL} 'PATH'           {Fore.WHITE}Specify path to configuration file{Style.RESET_ALL}")
    print(f"{Fore.GREEN}--version, -v{Style.RESET_ALL}             {Fore.WHITE}Show version information{Style.RESET_ALL}")
    
    print(f"\n{Fore.MAGENTA}{'Examples':<30} {Fore.WHITE}Description{Style.RESET_ALL}")
    print(f"{Fore.CYAN}{'─' * 70}{Style.RESET_ALL}")
    
    print(f"\n{Fore.GREEN}python main.py --chat{Style.RESET_ALL}              {Fore.WHITE}# Start interactive mode{Style.RESET_ALL}")
    print(f"{Fore.GREEN}python main.py --exec \"blog post about AI\"{Style.RESET_ALL} # Execute single command")
    print(f"{Fore.GREEN}python main.py --info{Style.RESET_ALL}              {Fore.WHITE}# Show system configuration{Style.RESET_ALL}")
    print(f"{Fore.GREEN}python main.py --capabilities{Style.RESET_ALL}      {Fore.WHITE}# List all tools and capabilities{Style.RESET_ALL}")
    
    print(f"\n{Fore.MAGENTA}{'Programmatic Usage':<30} {Fore.WHITE}Description{Style.RESET_ALL}")
    print(f"{ Fore.CYAN}{'─' * 70}{Style.RESET_ALL}")
    
    print(f"\n{Fore.GREEN}from bridge.api import ask_portero{Style.RESET_ALL}")
    print(f"{Fore.GREEN}response = ask_portero(\"create content about marketing\"){Style.RESET_ALL}")
    print(f"\n{Fore.GREEN}from bridge.api import PorteroClient{Style.RESET_ALL}")
    print(f"{Fore.GREEN}client = PorteroClient()  # Then use client methods{Style.RESET_ALL}")
    
    print(f"\n{Fore.MAGENTA}{'Available Capabilities':<30} {Fore.WHITE}Description{Style.RESET_ALL}")
    print(f"{Fore.CYAN}{'─' * 70}{Style.RESET_ALL}")
    print(f"{Fore.GREEN}1. Generate Blog Posts{Style.RESET_ALL}           {Fore.WHITE}# Create complete SEO-optimized articles{Style.RESET_ALL}")
    print(f"{Fore.GREEN}2. SEO Audit & Optimize{Style.RESET_ALL}          {Fore.WHITE}# Analyze and improve content for SEO{Style.RESET_ALL}")
    print(f"{Fore.GREEN}3. Topic Research{Style.RESET_ALL}               {Fore.WHITE}# Research topics for content planning{Style.RESET_ALL}")
    print(f"{Fore.GREEN}4. Publish to WordPress{Style.RESET_ALL}         {Fore.WHITE}# Publish content directly to WordPress{Style.RESET_ALL}")
    
    print(f"\n{Fore.CYAN}{'─' * 70}{Style.RESET_ALL}")
    print(f"{Fore.YELLOW}Type 'python main.py --chat' to get started!{Style.RESET_ALL}\n")


def run_programmatic_example():
    """Run demonstration of programmatic API usage."""
    print("\n" + "=" * 70)
    print(f"{Fore.GREEN}Programmatic API Example{Style.RESET_ALL}")
    print("=" * 70 + "\n")
    
    if not AGENT_AVAILABLE:
        print(f"{Fore.YELLOW}Skipping agent initialization - not available{Style.RESET_ALL}\n")
        return
    
    try:
        # Initialize client
        print(f"{Fore.CYAN}• Initializing client with Portero agent...{Style.RESET_ALL}")
        client = PorteroClient()
        
        # Get system info
        info = client.get_system_info()
        print(f"{Fore.CYAN}• System Info:{Style.RESET_ALL}")
        print(f"    Agent: {info['agent_name']}")
        print(f"    Model: {info['model']}")
        print(f"    Temperature: {info['temperature']}")
        print(f"    Available Tools: {', '.join(info['available_tools'])}\n")
        
        # Query agent (this would normally make an actual API call)
        print(f"{Fore.CYAN}• Sample Query: \"What can I do with this system?\"{Style.RESET_ALL}")
        result = ask_portero("What capabilities does the AI content system have?")
        print(f"{Fore.GREEN}Response: \"{result}\"{Style.RESET_ALL}\n")
        
        print(f"{Fore.GREEN}✓ Programmatic API ready for use!{Style.RESET_ALL}\n")
        
    except Exception as e:
        print(f"{Fore.RED}Error in programmatic example: {e}{Style.RESET_ALL}\n")


def main():
    """
    Main entry point for the WordPress AI Content System.
    
    This function handles command-line arguments and routes to appropriate
    functionality based on the user's input.
    """
    # Parse command-line arguments manually (since argparse not imported here)
    if len(sys.argv) == 1:
        print_help()
        print(f"\n{Fore.GREEN}Entering chat mode by default...{Style.RESET_ALL}")
        try:
            agent = get_agent()
        except:
            print(f"{Fore.YELLOW}Warning: Could not initialize agent{Style.RESET_ALL}")
            agent = None
        chat_mode(agent)
        return 0
    
    # Simple argument parsing
    args = sys.argv[1:]
    
    try:
        if '--chat' in args or '-c' in args:
            print(f"\n{Fore.YELLOW}Starting Interactive Chat Mode{Style.RESET_ALL}\n")
            try:
                agent = get_agent()
            except Exception as e:
                print(f"{Fore.RED}Warning: Could not initialize agent ({e}).{Style.RESET_ALL}")
                agent = None
            chat_mode(agent)
            return 0
            
        elif ('--exec' in args or '-e' in args) and len(args) >= 2:
            exec_index = args.index('--exec') if '--exec' in args else args.index('-e')
            query = args[exec_index + 1] if exec_index + 1 < len(args) else ""
            
            if not query and len(args) > exec_index + 1:
                query = args[exec_index + 1]
            else:
                # Try to get query from remaining args
                query_parts = []
                i = exec_index + 1 if exec_index + 1 < len(args) else 0
                while i < len(args) and not args[i].startswith('--'):
                    query_parts.append(args[i])
                    i += 1
                query = ' '.join(query_parts)
            
            if not query:
                print(f"{Fore.RED}Error: Please provide a query after --exec{Style.RESET_ALL}")
                return 1
            
            print(f"\n{Fore.CYAN}Executing: {query}{Style.RESET_ALL}\n")
            try:
                agent = get_agent()
            except Exception as e:
                print(f"{Fore.RED}Error initializing agent: {e}{Style.RESET_ALL}")
                return 1
                
            result = execute_command(query, agent)
            return 0 if result and result.get("success") else 1
            
        elif '--info' in args or '-i' in args:
            print(f"\n{Fore.YELLOW}System Information{Style.RESET_ALL}")
            print("-" * 70)
            
            if AGENT_AVAILABLE:
                try:
                    agent = get_agent()
                    info = agent.get_system_info()
                    
                    print(f"""
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
""")
                except Exception as e:
                    print(f"{Fore.RED}Error getting system info: {e}{Style.RESET_ALL}")
            else:
                print("Agent not available. Please check your installation.")
            
            print(f"{Fore.GREEN}Done.{Style.RESET_ALL}")
            return 0
            
        elif ('--capabilities' in args or '-cp' in args):
            print(f"\n{Fore.YELLOW}Available Capabilities{Style.RESET_ALL}")
            print("-" * 70)
            
            from bridge.cli import print_capabilities
            
            try:
                agent = get_agent()
                print_capabilities(agent)
            except Exception as e:
                print(f"{Fore.RED}Error: {e}{Style.RESET_ALL}\n")
                print("Available capabilities:")
                print("  1. Generate Blog Post")
                print("  2. SEO Audit & Optimize")
                print("  3. Topic Research")
                print("  4. Publish to WordPress")
            
            print(f"\n{Fore.GREEN}Done.{Style.RESET_ALL}")
            return 0
            
        elif '--help' in args or '-h' in args:
            print_help()
            return 0
            
        elif ('--version' in args or '-v' in args):
            print(f"WordPress AI Content System v{get_version()}")
            print("Powered by Portero Agent")
            print("-" * 70)
            raise SystemExit(0)
            
        elif '--programmatic' in args:
            run_programmatic_example()
            return 0
            
        else:
            # Default behavior: show help then enter chat mode
            print_help()
            print(f"\n{Fore.GREEN}Entering chat mode by default...{Style.RESET_ALL}")
            try:
                agent = get_agent()
            except:
                print(f"{Fore.YELLOW}Warning: Could not initialize agent{Style.RESET_ALL}")
                agent = None
            chat_mode(agent)
            return 0
            
    except KeyboardInterrupt:
        print(f"\n\n{Fore.YELLOW}Interrupted.{Style.RESET_ALL}")
        return 1
    except Exception as e:
        print(f"\n{Fore.RED}Error: {e}{Style.RESET_ALL}")
        return 1


if __name__ == "__main__":
    try:
        exit_code = main()
        sys.exit(exit_code)
    except KeyboardInterrupt:
        print(f"\n{Fore.YELLOW}Goodbye! Happy creating!{Style.RESET_ALL}")
        sys.exit(1)
    except Exception as e:
        print(f"\n{Fore.RED}Fatal error: {e}{Style.RESET_ALL}")
        sys.exit(1)
