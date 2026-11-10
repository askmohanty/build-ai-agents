# 2 · Prompting and structured output

A prompt is the program you write for a model. It's less precise than code, but the same habits apply: be explicit, give examples, define the output format, and test it.

## The parts of a request

```mermaid
flowchart TB
    S["System prompt<br/>who the model is, rules, format"] --> M((Model))
    H["Conversation history<br/>earlier user and assistant turns"] --> M
    T["Tool definitions<br/>name, description, input schema"] --> M
    U["User message<br/>the task and its data"] --> M
    M --> R["Response<br/>text and/or tool calls"]
```

- **System prompt:** standing instructions (role, rules, tone, what to do when unsure). Every project here sets one, called `SYSTEM`.
- **Messages:** alternating `user` and `assistant` turns. The model sees all of them on every call.
- **Tools:** functions the model may ask you to run ([concept 3](03-tool-calling-and-agents.md)).

## What makes a good prompt

1. **Be specific about the task and the audience.** "Explain the cause in plain English for an on-call engineer" beats "analyse this".
2. **Give the model a method.** [Project 04](../04-log-analyser-agent/) tells it to look at what happened *before* the first error; without that line, models often stop at the symptom.
3. **Give a checklist for reviews.** [Project 06](../06-config-reviewer-agent/) lists what a production review must check. Try deleting it and comparing scores.
4. **Say what to do when unsure.** "If the sources don't contain the answer, say you don't know" ([project 08](../08-chat-with-docs-rag/)) cuts hallucinations sharply.
5. **Show examples (few-shot).** One or two worked examples of input and ideal output teach format and style better than a paragraph describing them.
6. **Put data in clearly marked sections**, e.g. `Sources:` … `Question:` …, so the model doesn't confuse your instructions with the data.

**Tool descriptions are prompts too.** The model decides whether and how to call a tool from its name and description alone. A vague description gives a tool that's used wrongly or not at all.

## Structured output

Code can't reliably parse "Sure! Here's the report: …". When the output feeds another system (a ticket, a database, a dashboard), you need **JSON that matches a schema**.

Three approaches, from weakest to strongest:

| Approach | How | Reliability |
|---|---|---|
| Ask nicely | "Reply in JSON with fields …" | Often works; sometimes adds prose or breaks the format |
| Forced tool call | Define a tool whose input schema *is* your output format, and force the model to call it | Worked well on older models; the newest Claude models reject a forced tool choice (HTTP 400), so don't build on it |
| Native structured output | The API constrains the reply to your JSON schema (`output_config.format`), or a framework wrapper such as LangChain's `with_structured_output(MyPydanticModel, method="json_schema")` | Guaranteed to match the schema; used in this repo (`agentkit.extract`) and in [project 11](../11-langgraph-incident-assistant/) |

```python
# Native structured output (see src/agentkit/agent.py, extract())
response = client.messages.create(
    model=MODEL,
    max_tokens=4096,
    output_config={"format": {"type": "json_schema", "schema": SCHEMA}},   # reply must match SCHEMA
    messages=[{"role": "user", "content": task}],
)
report = json.loads(response.content[-1].text)
```

Every object in the schema needs `"additionalProperties": false`. The SDK can also take a Pydantic model and hand you a validated object: `client.messages.parse(..., output_format=MyModel).parsed_output`.

Use `enum` for fixed choices (`"severity": {"enum": ["low", "high"]}`) and mark fields `required`. Validate the result in code anyway.

## Common mistakes

- Packing every rule into one giant prompt. Split the work into steps or tools instead.
- Changing a prompt and judging it on one example. Prompts need evals ([concept 7](07-evals.md)).
- Trusting instructions inside the *data* (a document, a web page, a log line). That's prompt injection ([concept 8](08-agent-safety.md)).

## Further reading

- Anthropic, *Prompt engineering overview* (docs.anthropic.com) and the free interactive prompt engineering tutorial on GitHub
- Google, *Prompting strategies* in the Gemini API docs
