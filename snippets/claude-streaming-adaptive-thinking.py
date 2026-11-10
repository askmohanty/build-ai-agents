# Streaming with adaptive thinking: show the model's reasoning summary and answer as they arrive,
# and trade depth for cost with the effort setting.
# pip install anthropic    (set ANTHROPIC_API_KEY)
# More: https://github.com/askmohanty/hands-on-ai-agents
import anthropic

client = anthropic.Anthropic()

PROBLEM = """Our API's p99 latency jumped from 120 ms to 900 ms right after a deploy that only
changed a logging library. CPU is flat, memory is flat, error rate is flat. What are the three most
likely causes, and what would you check first?"""

with client.messages.stream(
    model="claude-sonnet-5-5",
    max_tokens=16000,
    thinking={"type": "adaptive", "display": "summarized"},  # the model decides how much to think
    output_config={"effort": "medium"},                       # low | medium | high | xhigh | max
    messages=[{"role": "user", "content": PROBLEM}],
) as stream:
    for event in stream:
        if event.type == "content_block_start":
            kind = event.content_block.type
            print("\n\n[thinking]\n" if kind == "thinking" else "\n\n[answer]\n" if kind == "text" else "", end="")
        elif event.type == "content_block_delta":
            if event.delta.type == "thinking_delta":
                print(event.delta.thinking, end="", flush=True)
            elif event.delta.type == "text_delta":
                print(event.delta.text, end="", flush=True)
    final = stream.get_final_message()

print(f"\n\nstop_reason={final.stop_reason}  output tokens={final.usage.output_tokens}")
# Thinking tokens are billed as output whether or not you display them; lower effort means fewer of them.
