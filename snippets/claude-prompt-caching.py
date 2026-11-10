# Prompt caching: pay full price for a long, stable prefix once, then about a tenth of it on every reuse.
# pip install anthropic    (set ANTHROPIC_API_KEY)
# More: https://github.com/askmohanty/hands-on-ai-agents
import anthropic

client = anthropic.Anthropic()

# A long, stable prefix: a runbook every question is asked against. Caching only kicks in above the
# model's minimum prefix length (roughly 1-4k tokens), so short prompts are never cached.
RUNBOOK = "\n".join(
    f"Step {i}: if alert DiskUsageHigh fires on node-{i % 7}, check /var/log size, rotate logs, "
    f"and page on-call only if usage stays above 92% for 10 minutes."
    for i in range(1, 400)
)


def ask(question: str) -> None:
    response = client.messages.create(
        model="claude-sonnet-5-5",
        max_tokens=1024,
        cache_control={"type": "ephemeral"},  # cache everything up to the last cacheable block (~5 min TTL)
        system=f"Answer from this runbook only.\n\n{RUNBOOK}",  # keep it byte-identical between calls
        messages=[{"role": "user", "content": question}],
    )
    u = response.usage
    print(f"{question!r}\n  written to cache={u.cache_creation_input_tokens}  "
          f"read from cache={u.cache_read_input_tokens}  uncached={u.input_tokens}")


if __name__ == "__main__":
    ask("When should on-call be paged?")      # first call: writes the cache
    ask("What do I check first on node-3?")   # second call: reads the same prefix from cache
    # If "read from cache" stays 0, something in the prefix changes between calls (a timestamp, a UUID,
    # unsorted JSON): anything that differs by one byte invalidates the cache from that point on.
