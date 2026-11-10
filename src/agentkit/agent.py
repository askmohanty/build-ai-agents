import json
import os
from dataclasses import dataclass, field
from typing import Any, Callable, Sequence

import anthropic
from dotenv import load_dotenv

load_dotenv()

MODEL = os.getenv("ANTHROPIC_MODEL", "claude-sonnet-5-5")


@dataclass
class Tool:
    """A Python function the model is allowed to call.

    `parameters` is the JSON Schema "properties" object for the function's
    arguments. Every parameter is required unless `required` says otherwise.
    """

    name: str
    description: str
    parameters: dict[str, Any]
    fn: Callable[..., Any]
    required: list[str] | None = field(default=None)

    def schema(self) -> dict[str, Any]:
        return {
            "name": self.name,
            "description": self.description,
            "input_schema": {
                "type": "object",
                "properties": self.parameters,
                "required": list(self.parameters) if self.required is None else self.required,
            },
        }


def _as_text(value: Any) -> str:
    return value if isinstance(value, str) else json.dumps(value, indent=2, default=str)


def run_agent(
    prompt: str,
    tools: Sequence[Tool] = (),
    system: str | None = None,
    messages: list | None = None,
    model: str = MODEL,
    max_turns: int = 10,
    max_tokens: int = 4096,
    verbose: bool = True,
) -> tuple[str, list]:
    """Run the tool loop until the model answers.

    Returns the final text and the full message history. Pass the history back
    in as `messages` to continue the same conversation (that is the agent's memory).
    """
    client = anthropic.Anthropic()
    by_name = {t.name: t for t in tools}
    messages = list(messages or [])
    messages.append({"role": "user", "content": prompt})

    request: dict[str, Any] = {"model": model, "max_tokens": max_tokens}
    if tools:
        request["tools"] = [t.schema() for t in tools]
    if system:
        request["system"] = system

    for _ in range(max_turns):
        response = client.messages.create(messages=messages, **request)
        messages.append({"role": "assistant", "content": response.content})

        if response.stop_reason != "tool_use":
            text = "".join(b.text for b in response.content if b.type == "text")
            return text, messages

        results = []
        for block in response.content:
            if block.type != "tool_use":
                continue
            if verbose:
                print(f"  -> {block.name}({json.dumps(block.input)})")
            tool = by_name.get(block.name)
            try:
                if tool is None:
                    raise ValueError(f"unknown tool {block.name!r}")
                output, is_error = _as_text(tool.fn(**block.input)), False
            except Exception as exc:  # the model sees the error and can recover
                output, is_error = f"{type(exc).__name__}: {exc}", True
            results.append(
                {"type": "tool_result", "tool_use_id": block.id, "content": output, "is_error": is_error}
            )
        messages.append({"role": "user", "content": results})

    raise RuntimeError(f"agent did not finish within {max_turns} turns")


def _strict(schema: Any) -> Any:
    """Structured output needs every object schema closed: add additionalProperties: false."""
    if isinstance(schema, dict):
        out = {k: _strict(v) for k, v in schema.items()}
        if out.get("type") == "object":
            out.setdefault("additionalProperties", False)
        return out
    if isinstance(schema, list):
        return [_strict(v) for v in schema]
    return schema


def extract(
    prompt: str,
    name: str,
    description: str,
    schema: dict[str, Any],
    system: str | None = None,
    model: str = MODEL,
    max_tokens: int = 4096,
) -> dict[str, Any]:
    """Get JSON back that is guaranteed to match `schema` (a JSON Schema object).

    Uses native structured output (`output_config.format`): the API constrains the
    reply to the schema, so there is no prose to strip and no parsing guesswork.
    `name` and `description` label the output for the model.
    """
    client = anthropic.Anthropic()
    request: dict[str, Any] = {
        "model": model,
        "max_tokens": max_tokens,
        "output_config": {"format": {"type": "json_schema", "schema": _strict(schema)}},
        "messages": [{"role": "user", "content": f"{prompt}\n\nReply with the {name}: {description}."}],
    }
    if system:
        request["system"] = system
    response = client.messages.create(**request)
    if response.stop_reason == "refusal":
        raise RuntimeError("model declined the request")
    text = "".join(block.text for block in response.content if block.type == "text")
    if not text:
        raise RuntimeError("model did not return structured output")
    return json.loads(text)


def chat(tools: Sequence[Tool] = (), system: str | None = None, **kwargs: Any) -> None:
    """A terminal chat that keeps the conversation history between turns."""
    messages: list = []
    print("Type 'exit' to quit.")
    while True:
        try:
            prompt = input("\nyou> ").strip()
        except (EOFError, KeyboardInterrupt):
            break
        if prompt.lower() in {"exit", "quit"}:
            break
        if not prompt:
            continue
        reply, messages = run_agent(prompt, tools, system, messages, **kwargs)
        print(f"\nagent> {reply}")
