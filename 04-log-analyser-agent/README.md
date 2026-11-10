# 04 · Log analyser agent

An agent that investigates an application log the way an SRE would: summarise first, search for errors, then read around them to find what happened just before.

The sample log [`samples/app.log`](samples/app.log) has a real-looking incident. Payment timeouts are the symptom; the cause is earlier in the file.

**You learn:**
- **Working with inputs too big for the context window.** The agent never sees the whole file, only what its tools return.
- **Structured output.** `agentkit.extract` forces the model to fill a JSON schema, so the report can go straight into Jira, PagerDuty or a database.

```bash
python 04-log-analyser-agent/agent.py                       # the sample log
python 04-log-analyser-agent/agent.py /path/to/your/app.log
```

## How it works (theory)

**The context window problem.** A model can only consider a limited number of tokens per request, and every token costs money and time. Real logs are gigabytes. So instead of sending the file, the agent gets tools that return small, relevant slices: `log_summary` (counts), `search_log` (matching lines), `read_lines` (context around a hit, capped at 100 lines). The model explores the file like an engineer with `grep` and `less`, and only what it asks for enters the context.

**Prompting for method, not just goal.** The system prompt says to look at what happened *before* the first error. Without that, models tend to report the symptom (database timeouts) instead of the cause.

**Prompt chaining.** The work is two steps: first a free-form investigation (`run_agent`), then a separate call that turns the findings into JSON (`extract`). Splitting reasoning from formatting gives better results than asking for both at once.

**Structured output.** `extract` passes the report format as a JSON schema (`output_config.format`), and the API constrains the reply to it. The model's answer must match the schema, including `enum` values for severity, so code can consume it safely.

Read more: [How LLMs work: the context window](../concepts/01-how-llms-work.md#the-context-window) · [Prompting and structured output](../concepts/02-prompting-and-structured-output.md)

## Try this

1. Did it find the root cause, or stop at "database timeouts"? If it stopped, improve the system prompt.
2. Did it notice the unrelated warning near the end of the file (look at `other_findings`)?
3. Run it on a real log from your own systems (remove secrets first). Does the regex in `LINE` match your format?
4. Add a `time_window(start, end)` tool that returns lines between two timestamps.
5. Change `severity` in the schema to a number from 1 to 5 and see how the output changes.
