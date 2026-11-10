# The agent loop without writing the loop: typed Python functions become tools, the SDK runs the calls.
# Compare with claude-tool-calling-agent-loop.py, which writes the same loop by hand.
# pip install anthropic    (set ANTHROPIC_API_KEY)
# More: https://github.com/askmohanty/build-ai-agents
import anthropic
from anthropic import beta_tool

client = anthropic.Anthropic()

PODS = {"checkout-7d9f": "CrashLoopBackOff", "checkout-5b2c": "Running", "search-1a8e": "Running"}
LOGS = {"checkout-7d9f": "panic: DATABASE_URL is not set"}


@beta_tool
def list_pods(prefix: str = "") -> str:
    """List pods and their status.

    Args:
        prefix: Only return pods whose name starts with this.
    """
    return "\n".join(f"{name} {status}" for name, status in PODS.items() if name.startswith(prefix))


@beta_tool
def pod_logs(name: str) -> str:
    """Return the last log lines of one pod.

    Args:
        name: The exact pod name.
    """
    return LOGS.get(name, "no recent log lines")


runner = client.beta.messages.tool_runner(
    model="claude-sonnet-5-5",
    max_tokens=4096,
    tools=[list_pods, pod_logs],  # schemas come from the signatures and docstrings
    messages=[{"role": "user", "content": "Why is checkout unhealthy?"}],
)
final = runner.until_done()  # runs tool calls until the model stops asking for tools
print("".join(block.text for block in final.content if block.type == "text"))
