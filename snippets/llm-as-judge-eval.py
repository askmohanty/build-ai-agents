# Evals: grade an answer with a second model call (LLM-as-judge), with structured output.
# Run it over a set of test questions every time you change a prompt, model or chunk size.
# pip install anthropic    (set ANTHROPIC_API_KEY)
# More: https://github.com/askmohanty/hands-on-ai-agents
import anthropic

client = anthropic.Anthropic()

GRADE = {
    "type": "object",
    "properties": {
        "correct": {"type": "boolean"},
        "grounded": {"type": "boolean", "description": "Every claim is supported by the sources"},
        "score": {"type": "integer", "minimum": 1, "maximum": 5},
        "reason": {"type": "string"},
    },
    "required": ["correct", "grounded", "score", "reason"],
}


def judge(question: str, sources: str, answer: str) -> dict:
    response = client.messages.create(
        model="claude-sonnet-5-5",
        max_tokens=1024,
        system="You are a strict grader. If the sources do not contain the answer, the correct answer says so.",
        tools=[{"name": "grade", "description": "Grade the answer", "input_schema": GRADE}],
        tool_choice={"type": "tool", "name": "grade"},
        messages=[{"role": "user", "content": f"Question: {question}\n\nSources:\n{sources}\n\nAnswer:\n{answer}"}],
    )
    return next(block.input for block in response.content if block.type == "tool_use")


CASES = [
    ("When does the disk alert page on-call?", "NodeDiskUsageHigh pages on-call at 92%.", "It pages at 92% disk usage."),
    ("When does the disk alert page on-call?", "NodeDiskUsageHigh pages on-call at 92%.", "It pages at 80%, after 5 minutes."),
]

if __name__ == "__main__":
    for question, sources, answer in CASES:
        grade = judge(question, sources, answer)
        print(f"{grade['score']}/5 correct={grade['correct']} grounded={grade['grounded']}: {answer!r}\n   {grade['reason']}")
