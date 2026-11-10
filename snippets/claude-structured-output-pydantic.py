# Structured output with Pydantic: describe the answer as a class, get a validated object back.
# pip install anthropic pydantic    (set ANTHROPIC_API_KEY)
# More: https://github.com/askmohanty/hands-on-ai-agents
from typing import Literal

import anthropic
from pydantic import BaseModel

client = anthropic.Anthropic()


class Change(BaseModel):
    service: str
    risk: Literal["low", "medium", "high"]
    needs_downtime: bool
    rollback_steps: list[str]


REQUEST = """Upgrade the orders Postgres from 14 to 16 on Saturday night. We'll take a snapshot,
run pg_upgrade in place, and the API will return 503 for about 20 minutes."""

response = client.messages.parse(
    model="claude-sonnet-5-5",
    max_tokens=4096,
    output_format=Change,  # the SDK turns the class into a JSON schema and validates the reply
    messages=[{"role": "user", "content": f"Assess this change request:\n{REQUEST}"}],
)
change = response.parsed_output  # a Change instance, already validated
print(change.risk, change.needs_downtime)
for step in change.rollback_steps:
    print("-", step)
