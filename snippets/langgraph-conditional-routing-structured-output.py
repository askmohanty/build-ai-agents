# LangGraph: nodes, typed state, structured output and a conditional edge.
#   START -> classify -> (billing | technical) -> END
# pip install langgraph langchain-anthropic    (set ANTHROPIC_API_KEY)
# More: https://github.com/askmohanty/build-ai-agents
from typing import Literal, TypedDict

from langchain_anthropic import ChatAnthropic
from langgraph.graph import END, START, StateGraph
from pydantic import BaseModel

llm = ChatAnthropic(model="claude-sonnet-5-5", max_tokens=1024)


class Ticket(BaseModel):
    category: Literal["billing", "technical"]
    urgency: Literal["low", "high"]


class State(TypedDict, total=False):
    message: str
    ticket: Ticket
    reply: str


def classify(state: State) -> State:
    return {"ticket": llm.with_structured_output(Ticket, method="json_schema").invoke(f"Classify this support message: {state['message']}")}


def billing(state: State) -> State:
    return {"reply": llm.invoke(f"As the billing team, reply briefly to: {state['message']}").content}


def technical(state: State) -> State:
    tone = "Apologise and escalate to on-call." if state["ticket"].urgency == "high" else "Give troubleshooting steps."
    return {"reply": llm.invoke(f"As technical support, reply briefly to: {state['message']}. {tone}").content}


builder = StateGraph(State)
builder.add_node("classify", classify)
builder.add_node("billing", billing)
builder.add_node("technical", technical)
builder.add_edge(START, "classify")
builder.add_conditional_edges("classify", lambda s: s["ticket"].category, ["billing", "technical"])
builder.add_edge("billing", END)
builder.add_edge("technical", END)
graph = builder.compile()

if __name__ == "__main__":
    result = graph.invoke({"message": "Checkout has been returning 504 for an hour and we're losing orders!"})
    print(result["ticket"], "\n", result["reply"])
    # print(graph.get_graph().draw_mermaid())   # paste into https://mermaid.live
