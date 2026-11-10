# Batch API: send many independent requests at once and pay half price, for work that can wait
# (classifying a backlog, summarising tickets, running an eval set). Most batches finish within an hour.
# pip install anthropic    (set ANTHROPIC_API_KEY)
# More: https://github.com/askmohanty/hands-on-ai-agents
import time

import anthropic
from anthropic.types.message_create_params import MessageCreateParamsNonStreaming
from anthropic.types.messages.batch_create_params import Request

client = anthropic.Anthropic()

TICKETS = {
    "T-101": "Checkout page returns 504 for every customer since 10:04.",
    "T-102": "Can you add dark mode to the dashboard?",
    "T-103": "Password reset email never arrives for gmail addresses.",
}

batch = client.messages.batches.create(requests=[
    Request(
        custom_id=ticket_id,  # results come back in any order: match them by this id
        params=MessageCreateParamsNonStreaming(
            model="claude-sonnet-5-5",
            max_tokens=1024,
            messages=[{"role": "user", "content": f"Classify as incident, bug or feature request, one word:\n{text}"}],
        ),
    )
    for ticket_id, text in TICKETS.items()
])
print(f"batch {batch.id} submitted")

while (batch := client.messages.batches.retrieve(batch.id)).processing_status != "ended":
    print(f"  {batch.processing_status}: {batch.request_counts.processing} still processing")
    time.sleep(30)

for result in client.messages.batches.results(batch.id):
    if result.result.type == "succeeded":
        text = next((b.text for b in result.result.message.content if b.type == "text"), "")
        print(f"{result.custom_id}: {text.strip()}")
    else:  # errored, canceled or expired: resubmit just these ids
        print(f"{result.custom_id}: {result.result.type}")
