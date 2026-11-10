# An MCP server: write tools once, use them from Claude Desktop, Claude Code, VS Code, ADK, LangGraph...
# pip install "mcp[cli]>=2"
# Try it:   mcp dev mcp-server-python-sdk-v2.py      (opens the MCP Inspector)
# Claude Desktop config: {"mcpServers": {"ops": {"command": "python", "args": ["/full/path/mcp-server-python-sdk-v2.py"]}}}
# More: https://github.com/askmohanty/hands-on-ai-agents
import shutil
import socket

from mcp.server.mcpserver import MCPServer  # mcp 1.x called this FastMCP (mcp.server.fastmcp)

mcp = MCPServer("ops-tools")


@mcp.tool()
def disk_usage(path: str = "/") -> dict:
    """Disk usage for a path on this machine."""
    usage = shutil.disk_usage(path)
    return {"path": path, "used_pct": round(usage.used / usage.total * 100, 1), "free_gb": round(usage.free / 1e9, 1)}


@mcp.tool()
def port_open(host: str, port: int) -> dict:
    """Check whether a TCP port is reachable."""
    try:
        with socket.create_connection((host, port), timeout=3):
            return {"host": host, "port": port, "open": True}
    except OSError as exc:
        return {"host": host, "port": port, "open": False, "error": str(exc)}


@mcp.resource("runbook://{name}")
def runbook(name: str) -> str:
    """A runbook as a readable resource."""
    runbooks = {"disk-full": "Delete logs older than 7 days in /var/log/app. Never touch /var/lib/etcd."}
    return runbooks.get(name, "unknown runbook")


if __name__ == "__main__":
    mcp.run()  # stdio: the client starts this process and talks over stdin/stdout
