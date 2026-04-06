"""
main.py — AgentLens CLI
"""

from agent_core import search_llms, list_ollama_models
from config import OLLAMA_MODEL

DIV = "=" * 55

QUERIES = [
    "Marketing automation agent: campaign creation, A/B testing, report generation.",
    "Customer support agent with tool calling and long context.",
    "Coding assistant agent that can execute code and search docs.",
]


def run(query: str):
    print(f"\n{DIV}")
    print(f"Query : {query}")
    print(DIV)

    try:
        models = search_llms(query)
    except Exception as e:
        print(f"[Error] {e}")
        return

    print("\n[1] Recommended LLMs\n")
    for i, m in enumerate(models, 1):
        print(f"  #{i} {m.get('name')}  [{m.get('provider')}]")
        print(f"      Params  : {m.get('parameters', 'N/A')}")
        print(f"      Context : {m.get('context_window', 'N/A')}")
        print(f"      Tools   : {m.get('tool_calling', 'N/A')}")
        print(f"      Cost    : {m.get('cost_tier', 'N/A')}")
        print(f"      Info    : {m.get('description', '')}")
        for f in m.get("key_features", []):
            print(f"               • {f}")
        print()

    print("[2] All Ollama Models on this machine:\n")
    for name in list_ollama_models():
        tag = " ◄ active" if name == OLLAMA_MODEL else ""
        print(f"  • {name}{tag}")


if __name__ == "__main__":
    print("AgentLens — LLM Discovery via Ollama + OpenAI Python SDK")
    for q in QUERIES:
        run(q)
