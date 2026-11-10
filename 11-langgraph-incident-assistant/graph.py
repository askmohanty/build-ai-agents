"""Project 11: a multi-step incident assistant built as a LangGraph graph.

Each step is a node; the edges decide what runs next. The flow:

    gather_logs -> diagnose -> (severity high?) -> human_review -> write_summary
                                      \\-- low --------------------> write_summary

    python 11-langgraph-incident-assistant/graph.py
    python 11-langgraph-incident-assistant/graph.py --show-graph     # print the graph as Mermaid
"""

import re
import sys
from pathlib import Path
from typing import Literal, TypedDict

from dotenv import load_dotenv
from langchain_anthropic import ChatAnthropic
from langgraph.graph import END, START, StateGraph
from pydantic import BaseModel, Field

from agentkit import MODEL

load_dotenv()
LOG = Path(__file__).resolve().parent.parent / "04-log-analyser-agent" / "samples" / "app.log"
llm = ChatAnthropic(model=MODEL, max_tokens=2048)


# --- State: what flows between the nodes ---------------------------------------

class Diagnosis(BaseModel):
    severity: Literal["low", "high"] = Field(description="high if customers are affected")
    root_cause: str
    affected_services: list[str]
    next_steps: list[str]


class IncidentState(TypedDict, total=False):
    alert: str
    evidence: str
    diagnosis: Diagnosis
    approved: bool
    summary: str


# --- Nodes: each takes the state and returns the fields it updates -------------

def gather_logs(state: IncidentState) -> IncidentState:
    """Plain Python, no model: not every step needs AI."""
    lines = LOG.read_text(encoding="utf-8").splitlines()
    interesting = [l for l in lines if re.search(r"ERROR|WARN|job", l)]
    print(f"[gather_logs] {len(interesting)} of {len(lines)} lines selected")
    return {"evidence": "\n".join(interesting)}


def diagnose(state: IncidentState) -> IncidentState:
    diagnosis = llm.with_structured_output(Diagnosis, method="json_schema").invoke(
        f"Alert: {state['alert']}\n\nLog evidence:\n{state['evidence']}\n\n"
        "Find the root cause (what happened BEFORE the first error), not just the symptom."
    )
    print(f"[diagnose] severity={diagnosis.severity}: {diagnosis.root_cause}")
    return {"diagnosis": diagnosis}


def human_review(state: IncidentState) -> IncidentState:
    d = state["diagnosis"]
    print("\n[human_review] High severity. Proposed next steps:")
    for step in d.next_steps:
        print(f"   - {step}")
    return {"approved": input("Approve this plan? [y/N] ").strip().lower() == "y"}


def write_summary(state: IncidentState) -> IncidentState:
    d = state["diagnosis"]
    response = llm.invoke(
        "Write a short incident summary for a Slack channel (under 120 words): what happened, "
        f"impact, root cause, next steps. Plan approved by on-call: {state.get('approved', 'not needed')}.\n\n"
        f"{d.model_dump_json(indent=2)}"
    )
    return {"summary": response.content if isinstance(response.content, str) else str(response.content)}


def route_by_severity(state: IncidentState) -> str:
    return "human_review" if state["diagnosis"].severity == "high" else "write_summary"


# --- The graph -------------------------------------------------------------------

builder = StateGraph(IncidentState)
builder.add_node("gather_logs", gather_logs)
builder.add_node("diagnose", diagnose)
builder.add_node("human_review", human_review)
builder.add_node("write_summary", write_summary)

builder.add_edge(START, "gather_logs")
builder.add_edge("gather_logs", "diagnose")
builder.add_conditional_edges("diagnose", route_by_severity, ["human_review", "write_summary"])
builder.add_edge("human_review", "write_summary")
builder.add_edge("write_summary", END)

graph = builder.compile()

if __name__ == "__main__":
    if "--show-graph" in sys.argv:
        print(graph.get_graph().draw_mermaid())
        sys.exit()
    final = graph.invoke({"alert": "POST /orders error rate 18% over 5 minutes"})
    print("\n--- Incident summary ---\n" + final["summary"])
