"""
AgentLens CLI — Professional Discovery Tool
"""

import sys
import os
from agent_core import search_llms, list_ollama_models
from config import OLLAMA_MODEL

# ANSI Color Codes for "OG" look
BLUE = "\033[94m"
CYAN = "\033[96m"
GREEN = "\033[92m"
YELLOW = "\033[93m"
BOLD = "\033[1m"
RESET = "\033[0m"

W = 86  # Standard terminal width for tables

QUERIES = {
    "1": "Marketing automation agent: campaign creation, A/B testing, report generation.",
    "2": "Customer support agent with tool calling and long context.",
    "3": "Coding assistant agent that can execute code and search docs.",
}

def print_banner():
    print(f"{CYAN}{BOLD}")
    print("   _   ___ ___ _  _ _____ _    ___ _  _ ___ ")
    print("  /_\ / __| __| \| |_   _| |  | __| \| / __|")
    print(" / _ \ (_ | _|| .` | | | | |__| _|| .` \__ \\")
    print("/_/ \_\___|___|_|\_| |_| |____|___|_|\_|___/")
    print(f"            {YELLOW}Modern Discovery Agent v2.0{RESET}")
    print(f"{BLUE}{'═' * W}{RESET}")

def print_model_table(i, m):
    # Header / Row 1
    name     = m.get('name', 'N/A')
    provider = m.get('provider', 'N/A')
    context  = m.get('context_window', 'N/A')
    cost     = m.get('cost_tier', 'N/A')

    # Row 1 columns formatting
    border = f"{BLUE}│{RESET}"
    meta = f"{provider:<12} {border} ctx: {context:<10} {border} cost: {cost:<8}"
    
    print(f"{BLUE}┌{'─' * (W-2)}┐{RESET}")
    print(f"{border} {BOLD}#{i}{RESET} {BOLD}{BLUE}{name:<25}{RESET} {border} {meta} {border}")
    
    # Divider
    print(f"{BLUE}├{'─' * (W-2)}┤{RESET}")
    
    # Row 2: Description
    desc = m.get('description', 'No details provided.')
    print(f"{border} {YELLOW}INFO:{RESET} {desc[:W-10]:<{W-10}} {border}")
    
    # Key Features
    features = ", ".join(m.get("key_features", []))
    print(f"{border} {YELLOW}KEYS:{RESET} {features[:W-10]:<{W-10}} {border}")
    
    print(f"{BLUE}└{'─' * (W-2)}┘{RESET}\n")

def main():
    print_banner()
    while True:
        print(f"\n {BOLD}SELECT YOUR WORKFLOW:{RESET}")
        print(f"  {CYAN}1.{RESET} Marketing Automation      {CYAN}3.{RESET} Coding Assistant Agent")
        print(f"  {CYAN}2.{RESET} Customer Support Agent    {CYAN}4.{RESET} Custom Workflow Query")
        print(f"  {RED if 'RED' in globals() else YELLOW}Q.{RESET} Quit\n")

        choice = input(f" {BOLD}Choice > {RESET}").strip().lower()
        if choice in ['q', 'exit', 'quit']: break

        if choice in QUERIES:
            query = QUERIES[choice]
        elif choice == '4':
            query = input(f"\n {BOLD}Describe your workflow: {RESET}")
            if not query: continue
        else:
            print(f"\n {YELLOW}Invalid choice, try again.{RESET}")
            input(" Press Enter to continue...")
            continue

        print(f"\n{BLUE}{'═' * W}{RESET}")
        print(f" {BOLD}AGENTIC ENGINE ACTIVATED:{RESET} Researching for '{query}'")
        print(f"{BLUE}{'═' * W}{RESET}\n")

        try:
            models = search_llms(query)
            if not models:
                print(f" {YELLOW}[!] No models found or parsing error occurred.{RESET}")
            else:
                for idx, model in enumerate(models, 1):
                    print_model_table(idx, model)
        except Exception as e:
            print(f" {RED if 'RED' in globals() else YELLOW}[ERROR] {e}{RESET}")

        print(f"\n {BOLD}[LOCALS]{RESET} Current Ollama models on this machine:")
        for name in list_ollama_models():
            tag = f" {GREEN}◄ ACTIVE{RESET}" if name == OLLAMA_MODEL else ""
            print(f"   • {name}{tag}")
            
    print(f"\n {BOLD}Shutting down AgentLens...{RESET}")

if __name__ == "__main__":
    main()
