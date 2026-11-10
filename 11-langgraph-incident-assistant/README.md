# 11 · Incident assistant with LangGraph

[LangGraph](https://langchain-ai.github.io/langgraph/) builds agents as **graphs**: each step is a node, and edges (some of them conditional) decide what runs next. Use it when you want *control* over the flow rather than leaving every decision to the model.

```
gather_logs ──► diagnose ──► severity high? ──► human_review ──► write_summary
                                  └── low ─────────────────────────┘
```

- `gather_logs` is plain Python with no model. Not every step needs AI.
- `diagnose` returns a typed Pydantic object (`with_structured_output(..., method="json_schema")`).
- A conditional edge sends high-severity incidents to a human before the summary is written.

**You learn:** state, nodes, edges and conditional routing in LangGraph; mixing deterministic code with model calls; where a person fits in an automated flow.

```bash
python 11-langgraph-incident-assistant/graph.py
python 11-langgraph-incident-assistant/graph.py --show-graph   # paste into https://mermaid.live
```

## How it works (theory)

**State.** `IncidentState` is a typed dictionary that flows through the graph. Each node receives the current state and returns *only the fields it changes*; LangGraph merges them in. The state is the single source of truth for the run, which also makes it easy to log, test and checkpoint.

**Nodes** are ordinary functions. `gather_logs` uses no model at all: deterministic steps should stay deterministic (cheaper, faster, testable). `diagnose` and `write_summary` call the model.

**Edges** define the order. `add_conditional_edges` calls `route_by_severity(state)` and follows the edge whose name it returns. That's **routing**: the model's structured output (`severity`) decides the path, but the set of possible paths is fixed by you.

**Structured output with Pydantic.** `llm.with_structured_output(Diagnosis, method="json_schema")` makes the model return a validated `Diagnosis` object rather than text, so `route_by_severity` can rely on `severity` being exactly `"low"` or `"high"`.

**Workflow versus agent.** In project 09 the model chooses every step. Here the steps are fixed and the model makes decisions *within* them. Graphs give predictability, easier debugging and natural places for human approval; free agents handle open-ended problems. Real systems often mix both, for example a graph with an agent inside one node.

**Checkpointing** (exercise 2) saves state after every node, so a graph can stop for human approval and resume hours later, even in another process.

Read more: [Agent frameworks: LangGraph](../concepts/06-agent-frameworks.md#langgraph-agents-as-graphs) · [Workflows versus agents](../concepts/03-tool-calling-and-agents.md#workflows-versus-agents)

## Try this

1. Add a `check_runbook` node between `diagnose` and `human_review` that uses `rag.search` from project 08.
2. Replace the `input()` in `human_review` with LangGraph's built-in `interrupt()` and a checkpointer (`MemorySaver`), so the graph can pause, wait hours for approval, and resume. Read the LangGraph "human-in-the-loop" docs.
3. Turn `diagnose` into a ReAct agent that calls the project 10 MCP server's tools through `langchain-mcp-adapters`.
4. Add a retry loop: if the human rejects the plan, go back to `diagnose` with their feedback in the state.
5. Compare with project 09, where the model decides every step. When would you choose a graph, and when a free agent?
