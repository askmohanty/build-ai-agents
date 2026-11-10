# 10 · Your own MCP server

[MCP (Model Context Protocol)](https://modelcontextprotocol.io) is the open standard for connecting AI apps to tools and data. Instead of writing tools separately for every framework, you write an **MCP server** once, and any MCP client can use it: Claude Desktop, Claude Code, VS Code, Cursor, Google ADK, LangGraph.

This server exposes the log tools from project 04 and the runbooks from project 08:

| Kind | Name | What it does |
|---|---|---|
| tool | `list_logs` | log files it can read |
| tool | `log_summary` | counts by level and service |
| tool | `search_log` | regex search with line numbers |
| resource | `runbook://{name}` | a runbook, e.g. `runbook://disk-full` |

**You learn:** MCP tools versus resources; the stdio transport; the client side of the protocol; and that tools are an API you design.

```bash
python 10-mcp-server/client.py          # a minimal client calls the server
mcp dev 10-mcp-server/server.py         # MCP Inspector: click through tools in the browser
```

## Use it from Claude Desktop

Add this to Claude Desktop's config (Settings → Developer → Edit Config), with your own absolute paths:

```json
{
  "mcpServers": {
    "devops-tools": {
      "command": "C:/path/to/build-ai-agents/.venv/Scripts/python.exe",
      "args": ["C:/path/to/build-ai-agents/10-mcp-server/server.py"]
    }
  }
}
```

Restart Claude Desktop and ask: *"Use devops-tools to find out why payments failed in app.log."*

## How it works (theory)

**The problem MCP solves.** Every AI app used to define tools its own way, so the log tools in project 04 would need rewriting for Claude Desktop, then for VS Code, then for ADK. MCP standardises the interface: an AI app (the **host**) contains an MCP **client**, which connects to MCP **servers** like this one. Any host can then use any server.

**What a server exposes.**
- **Tools** are functions *the model* decides to call (`log_summary`, `search_log`).
- **Resources** are data *the application or user* chooses to load into context (`runbook://disk-full`).
- **Prompts** are reusable templates a user can pick.

**How the decorators work.** `@mcp.tool()` reads the function's name, type hints and docstring and publishes them as a tool definition with a JSON schema. That's why good docstrings matter: they become the description the model sees.

**Transports.** With **stdio** (the default here) the client starts the server as a child process and they exchange JSON-RPC messages over stdin and stdout. Local only, no network, no auth needed. With **streamable HTTP**, the server is a network service that many clients share, so it needs everything an API needs: authentication (OAuth), TLS and rate limits.

**The server is the security boundary.** Whatever the model is told, it can only do what the server implements. Here, reading files inside `samples/`.

Read more: [MCP](../concepts/05-mcp.md)

## Try this

1. Add the read-only `kubectl` tool from project 05 as an MCP tool.
2. Add a resource listing all runbook names, so a client can discover them.
3. Project 12 connects Google ADK to this same server. One server, two frameworks.
4. Run it over HTTP instead of stdio (`mcp.run(transport="streamable-http")`) so it could run in Kubernetes. What does it now need that stdio didn't? (Hint: authentication.)
