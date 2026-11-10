# Google ADK (Agent Development Kit): a root agent that hands off to specialist sub-agents.
# pip install google-adk    (free Gemini key: https://aistudio.google.com/apikey)
#
# ADK loads agents from a package. Save this file as  my_agent/agent.py,
# add  my_agent/__init__.py  containing  "from . import agent",
# and  my_agent/.env  containing  GOOGLE_GENAI_USE_VERTEXAI=FALSE  and  GOOGLE_API_KEY=...
# Then, from the folder above my_agent:   adk web    (UI at http://localhost:8000)   or   adk run my_agent
# More: https://github.com/askmohanty/build-ai-agents
from google.adk.agents import Agent

MODEL = "gemini-2.5-flash"

SERVICES = {"payments": "degraded: database connection timeouts", "orders": "healthy", "auth": "healthy"}
COSTS = {"payments": 1832.87, "orders": 940.10, "auth": 410.55}


# ADK turns plain functions into tools, using the name, type hints and docstring.
def get_service_status(service: str) -> dict:
    """Current health of a service.

    Args:
        service: Service name, e.g. "payments".
    """
    if service not in SERVICES:
        return {"status": "error", "error_message": f"unknown service; known: {sorted(SERVICES)}"}
    return {"status": "success", "service": service, "health": SERVICES[service]}


def get_monthly_cost(service: str) -> dict:
    """This month's cloud cost for a service, in USD.

    Args:
        service: Service name, e.g. "payments".
    """
    if service not in COSTS:
        return {"status": "error", "error_message": f"unknown service; known: {sorted(COSTS)}"}
    return {"status": "success", "service": service, "cost_usd": COSTS[service]}


ops_agent = Agent(
    name="ops_agent",
    model=MODEL,
    description="Answers questions about service health and incidents.",
    instruction="Check service health with get_service_status and explain problems plainly.",
    tools=[get_service_status],
)

finops_agent = Agent(
    name="finops_agent",
    model=MODEL,
    description="Answers questions about cloud cost.",
    instruction="Use get_monthly_cost for exact figures; never estimate.",
    tools=[get_monthly_cost],
)

root_agent = Agent(  # ADK looks for a variable with exactly this name
    name="platform_assistant",
    model=MODEL,
    description="Front door for platform questions.",
    instruction="Send health and incident questions to ops_agent and cost questions to finops_agent.",
    sub_agents=[ops_agent, finops_agent],
)
