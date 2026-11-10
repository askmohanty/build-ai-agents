# A tool an agent can't misuse: the safety lives in the tool, not the prompt.
# Register kubectl() as a tool in claude-tool-calling-agent-loop.py with an "args" array parameter.
# More: https://github.com/askmohanty/build-ai-agents
import shutil
import subprocess

READ_ONLY_VERBS = {"get", "describe", "logs", "top", "events", "explain", "api-resources", "version"}
BLOCKED_WORDS = {"secret", "secrets", "--kubeconfig", "--token", "--as"}
MAX_OUTPUT = 8000


def kubectl(args: list[str]) -> str:
    if not args or args[0] not in READ_ONLY_VERBS:
        raise PermissionError(f"only these verbs are allowed: {sorted(READ_ONLY_VERBS)}")
    if any(word in arg.lower() for arg in args for word in BLOCKED_WORDS):
        raise PermissionError("secrets and credential flags are not allowed")
    if shutil.which("kubectl") is None:
        raise FileNotFoundError("kubectl is not on PATH")

    # A list of arguments, never a shell string, so nothing can be injected.
    result = subprocess.run(["kubectl", *args], capture_output=True, text=True, timeout=30)
    output = (result.stdout + result.stderr).strip()
    if len(output) > MAX_OUTPUT:  # one huge describe must not flood the context window
        output = output[:MAX_OUTPUT] + f"\n... truncated ({len(output)} characters)"
    return output or "(no output)"


if __name__ == "__main__":
    for attempt in (["delete", "pod", "x"], ["get", "secrets"], ["get", "pods", "-A"]):
        try:
            print(attempt, "->", kubectl(attempt)[:200])
        except (PermissionError, FileNotFoundError) as exc:
            print(attempt, "-> refused:", exc)
