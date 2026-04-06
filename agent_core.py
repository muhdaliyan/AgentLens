"""
agent_core.py
Unified Agentic Core for AgentLens.
"""

import json
import re
from openai import OpenAI

try:
    from ddgs import DDGS
except ImportError:
    DDGS = None

from config import OLLAMA_BASE_URL, OLLAMA_MODEL, SYSTEM_PROMPT


# Single client instance for performance
client = OpenAI(api_key="ollama", base_url=f"{OLLAMA_BASE_URL}/v1")

# Static tool definition
TOOLS = [{
    "type": "function",
    "function": {
        "name": "web_search",
        "description": "Searches for latest LLMs and benchmarks (2026).",
        "parameters": {
            "type": "object",
            "properties": {
                "query": {"type": "string", "description": "Search query"}
            },
            "required": ["query"]
        }
    }
}]


def web_search(query: str) -> str:
    """Performs a web search via DuckDuckGo."""
    if not DDGS:
        return "Search tool (duckduckgo-search) not installed."
    
    try:
        with DDGS() as ddgs:
            results = list(ddgs.text(f"latest LLMs {query} 2026 benchmarks", max_results=5))
            if not results:
                return "No results found."
            return "\n\n".join([f"Title: {r['title']}\nSnippet: {r['body']}" for r in results])
    except Exception as e:
        return f"Search error: {e}"


def search_llms(query: str) -> list[dict]:
    """Agentic workflow: Decides if it needs to search, then returns ranked models."""
    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": f"Agentic workflow: {query}"}
    ]

    # Initial decision
    response = client.chat.completions.create(
        model=OLLAMA_MODEL,
        messages=messages,
        tools=TOOLS,
    )

    msg = response.choices[0].message
    if not msg.tool_calls:
        return _parse_json(msg.content)

    # Handle Tool Calls
    print(f"[AgentLens] Running search for: {query}...")
    messages.append(msg)

    for tool in msg.tool_calls:
        if tool.function.name == "web_search":
            args = json.loads(tool.function.arguments)
            result = web_search(args.get("query", query))
            messages.append({
                "role": "tool",
                "tool_call_id": tool.id,
                "name": "web_search",
                "content": result
            })

    # Final completion with tool results
    final_resp = client.chat.completions.create(model=OLLAMA_MODEL, messages=messages)
    return _parse_json(final_resp.choices[0].message.content)


def list_ollama_models() -> list[str]:
    """Retrieves list of all local Ollama models."""
    try:
        return [m.id for m in client.models.list().data]
    except Exception as e:
        print(f"[Ollama] {e}")
        return []


def _parse_json(text: str) -> list[dict]:
    """Robust extractor for JSON lists wrapped in markdown."""
    if not text: return []
    # Strip markdown and isolate potential JSON block
    match = re.search(r"(\[.*\])", text, re.DOTALL)
    if not match: return []
    try:
        return json.loads(match.group(1))
    except json.JSONDecodeError:
        return []

