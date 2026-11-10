# The tool-calling loop every agent is built on.
# pip install anthropic    (set ANTHROPIC_API_KEY)
# More: https://github.com/askmohanty/hands-on-ai-agents
import json

import anthropic

client = anthropic.Anthropic()
MODEL = "claude-sonnet-5-5"


def get_order_status(order_id: str) -> dict:
    orders = {"88121": "delivered", "88122": "payment failed"}
    return {"order_id": order_id, "status": orders.get(order_id, "not found")}


TOOLS = [{
    "name": "get_order_status",
    "description": "Look up the status of an order by its ID.",
    "input_schema": {
        "type": "object",
        "properties": {"order_id": {"type": "string"}},
        "required": ["order_id"],
    },
}]
FUNCTIONS = {"get_order_status": get_order_status}


def run(question: str) -> str:
    messages = [{"role": "user", "content": question}]
    while True:
        response = client.messages.create(model=MODEL, max_tokens=1024, tools=TOOLS, messages=messages)
        messages.append({"role": "assistant", "content": response.content})
        if response.stop_reason != "tool_use":  # no tool requested: this is the answer
            return "".join(b.text for b in response.content if b.type == "text")

        results = []
        for block in response.content:
            if block.type == "tool_use":
                output = FUNCTIONS[block.name](**block.input)
                results.append({"type": "tool_result", "tool_use_id": block.id, "content": json.dumps(output)})
        messages.append({"role": "user", "content": results})


if __name__ == "__main__":
    print(run("What happened to orders 88121 and 88122?"))
