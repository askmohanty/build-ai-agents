# AI engineering snippets (Python)

Short, standalone, copy-paste starting points for building AI agents. Each file runs on its own: install what its header says and run it. Each is also published as its own GitHub Gist.

| Snippet | What it shows | Theory | Gist |
|---|---|---|---|
| [claude-tool-calling-agent-loop.py](claude-tool-calling-agent-loop.py) | The tool-calling loop every AI agent is built on, written from scratch with the Anthropic SDK | [Tool calling and agents](../concepts/03-tool-calling-and-agents.md) | [gist](https://gist.github.com/askmohanty/7aa9e02a9cbbb6b1e4840c823bbad9ef) |
| [claude-tool-runner-beta-tool.py](claude-tool-runner-beta-tool.py) | The same agent loop without writing it: typed Python functions become tools with `@beta_tool` | [Tool calling and agents](../concepts/03-tool-calling-and-agents.md) | [gist](https://gist.github.com/askmohanty/9028b37e118698b6bbfdd3f1b9ce2f83) |
| [llm-structured-output-json-schema.py](llm-structured-output-json-schema.py) | Reliable JSON from an LLM: native structured output constrained to a JSON schema | [Structured output](../concepts/02-prompting-and-structured-output.md#structured-output) | [gist](https://gist.github.com/askmohanty/69e8ee797f7dab6ecd215e1a8f223873) |
| [claude-structured-output-pydantic.py](claude-structured-output-pydantic.py) | Structured output with Pydantic: describe the answer as a class, get a validated object back | [Structured output](../concepts/02-prompting-and-structured-output.md#structured-output) | [gist](https://gist.github.com/askmohanty/1708c2f933b94b4265d51729bf044261) |
| [claude-streaming-adaptive-thinking.py](claude-streaming-adaptive-thinking.py) | Streaming the model's reasoning summary and answer as they arrive, with effort control | [How LLMs work](../concepts/01-how-llms-work.md) | [gist](https://gist.github.com/askmohanty/3d1ddca9cc8b588e32763f05305dbea3) |
| [claude-prompt-caching.py](claude-prompt-caching.py) | Prompt caching: pay for a long stable prefix once, then about a tenth on every reuse | [LLMOps](../concepts/09-llmops.md) | [gist](https://gist.github.com/askmohanty/cbd475a1ce75b9ba71690a08501251a2) |
| [claude-message-batches-half-price.py](claude-message-batches-half-price.py) | The Batch API: many independent requests at half price, for work that can wait | [LLMOps](../concepts/09-llmops.md) | [gist](https://gist.github.com/askmohanty/82a7c49e1f4ecfe66dd701e15c254cba) |
| [ai-agent-safe-readonly-kubectl-tool.py](ai-agent-safe-readonly-kubectl-tool.py) | A read-only Kubernetes tool an agent can't misuse: allow-list, no shell, bounded output | [Agent safety](../concepts/08-agent-safety.md) | [gist](https://gist.github.com/askmohanty/452fc5308617f9f0c80a917ec8f33e64) |
| [rag-chromadb-claude-minimal.py](rag-chromadb-claude-minimal.py) | Retrieval-augmented generation in under 60 lines: chunk, embed, search, answer with citations | [Embeddings and RAG](../concepts/04-embeddings-and-rag.md) | [gist](https://gist.github.com/askmohanty/3897f2035f3ee1f227335ce0819f3f78) |
| [mcp-server-python-sdk-v2.py](mcp-server-python-sdk-v2.py) | An MCP server (Model Context Protocol, Python SDK v2) with tools and a resource | [MCP](../concepts/05-mcp.md) | [gist](https://gist.github.com/askmohanty/bcf4a1e6f97e065a2e28f72a25e64fd5) |
| [langgraph-conditional-routing-structured-output.py](langgraph-conditional-routing-structured-output.py) | LangGraph: typed state, nodes, conditional routing and Pydantic structured output | [LangGraph](../concepts/06-agent-frameworks.md#langgraph-agents-as-graphs) | [gist](https://gist.github.com/askmohanty/7ab9ace3e7b7c5780996a315489f7caf) |
| [google-adk-multi-agent-sub-agents.py](google-adk-multi-agent-sub-agents.py) | Google ADK: a root agent delegating to specialist sub-agents with function tools | [Google ADK](../concepts/06-agent-frameworks.md#google-adk-agents-and-sub-agents) | [gist](https://gist.github.com/askmohanty/8e1cc0a4bd6d269611cd814fd20042e9) |
| [llm-as-judge-eval.py](llm-as-judge-eval.py) | Evals: grading answers for correctness and groundedness with a second model call | [Evals](../concepts/07-evals.md) | [gist](https://gist.github.com/askmohanty/4e3823474cdeab4dc3ac1475bcdb7d9c) |

All thirteen together in one Gist: https://gist.github.com/askmohanty/d1bda98dfc1e3246d8eb3361ef67657e

Set `ANTHROPIC_API_KEY` for the Claude snippets, or `GOOGLE_API_KEY` for the ADK one.

**Learning?** These are the short versions. The full projects, with sample data, theory and experiments, are in this repository: **[fork it](https://github.com/askmohanty/hands-on-ai-agents/fork)** and work through them in your fork.
