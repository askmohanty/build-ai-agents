# Reliable JSON from a model: force it to call one tool whose schema is your output format.
# pip install anthropic    (set ANTHROPIC_API_KEY)
# More: https://github.com/askmohanty/hands-on-ai-agents
import json

import anthropic

client = anthropic.Anthropic()

REPORT = {
    "type": "object",
    "properties": {
        "severity": {"type": "string", "enum": ["low", "medium", "high", "critical"]},
        "root_cause": {"type": "string"},
        "affected_services": {"type": "array", "items": {"type": "string"}},
        "actions": {"type": "array", "items": {"type": "string"}},
    },
    "required": ["severity", "root_cause", "affected_services", "actions"],
}

LOG = """10:03:53 WARN [payment-service] Connection pool usage 10/10
10:04:23 ERROR [payment-service] Timed out waiting for a database connection
10:04:30 WARN [api-gateway] POST /orders 504
10:05:02 INFO [reporting-job] Nightly export started: SELECT * FROM payments (no LIMIT)"""

response = client.messages.create(
    model="claude-sonnet-5-5",
    max_tokens=1024,
    tools=[{"name": "incident_report", "description": "File an incident report", "input_schema": REPORT}],
    tool_choice={"type": "tool", "name": "incident_report"},  # must answer through this tool
    messages=[{"role": "user", "content": f"Write an incident report for this log:\n{LOG}"}],
)
report = next(block.input for block in response.content if block.type == "tool_use")
print(json.dumps(report, indent=2))
