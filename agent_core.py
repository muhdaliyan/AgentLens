"""
agent_core.py
OpenAI Python SDK pointed at Ollama — no API key needed.
Model: gemini-3-flash-preview:cloud
"""

import json
import re
from openai import OpenAI
from config import OLLAMA_BASE_URL, OLLAMA_MODEL, SYSTEM_PROMPT

try:
    from ddgs import DDGS
except ImportError:
    DDGS = None


def _client() -> OpenAI:
    return OpenAI(
        api_key="ollama",                      # required by SDK but ignored by Ollama
        base_url=f"{OLLAMA_BASE_URL}/v1",      # Ollama OpenAI-compatible endpoint
    )


def web_search(query: str) -> str:
    """Search the web for the latest AI models and agents."""
    if not DDGS:
        return "Search tool not installed. Run 'uv add duckduckgo-search'."
    
    # We refine the search to focus on latest LLMs and benchmarks
    refined_query = f"latest LLMs for {query} 2024 2025 reddit benchmarks"
    try:
        with DDGS() as ddgs:
            results = ddgs.text(refined_query, max_results=5)
            if not results:
                return "No search results found."
            
            formatted = "\n\n".join([
                f"Title: {r.get('title')}\nSnippet: {r.get('body')}\nLink: {r.get('href')}"
                for r in results
            ])
            return formatted
    except Exception as e:
        return f"Search failed: {str(e)}"


def search_llms(query: str) -> list[dict]:
    """Agent that can choose to search the web if it needs up-to-date recommendations."""
    client = _client()

    # 1. Define the tool for the API
    tools = [{
        "type": "function",
        "function": {
            "name": "web_search",
            "description": "Searches the web for latest LLMs and benchmarks (April 2026).",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {"type": "string", "description": "The search query (e.g., 'latest LLMs for coding')"}
                },
                "required": ["query"]
            }
        }
    }]

    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": f"Agentic workflow: {query}"}
    ]

    # 2. First call: The model decides if it needs a tool
    response = client.chat.completions.create(
        model=OLLAMA_MODEL,
        messages=messages,
        tools=tools,
        tool_choice="auto",
    )

    message = response.choices[0].message

    # 3. Handle Tool Calls (The Agentic Loop)
    if message.tool_calls:
        print(f"[AgentLens] Agent decided it needs the web! Calling search tool...")
        messages.append(message)  # Add model's request to the thread

        for tool_call in message.tool_calls:
            if tool_call.function.name == "web_search":
                # Parse arguments and call our search function
                args = json.loads(tool_call.function.arguments)
                search_data = web_search(args["query"])
                
                # Append tool result to thread
                messages.append({
                    "role": "tool",
                    "tool_call_id": tool_call.id,
                    "name": "web_search",
                    "content": search_data
                })

        # 4. Final call: Send tool results back to the LLM
        response = client.chat.completions.create(
            model=OLLAMA_MODEL,
            messages=messages,
        )

    # Return the final results (JSON parsed)
    text = response.choices[0].message.content
    return _parse_json(text)


def list_ollama_models() -> list[str]:
    """List all models installed in Ollama."""
    try:
        return [m.id for m in _client().models.list().data]
    except Exception as e:
        print(f"[Ollama] {e}")
        return []


def _parse_json(text: str) -> list[dict]:
    cleaned = re.sub(r"```(?:json)?", "", text).strip().rstrip("`").strip()
    s, e = cleaned.find("["), cleaned.rfind("]")
    if s == -1 or e == -1:
        return []
    try:
        result = json.loads(cleaned[s:e+1])
        return result if isinstance(result, list) else []
    except json.JSONDecodeError:
        return []
