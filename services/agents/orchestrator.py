from __future__ import annotations

from dataclasses import dataclass
from router import route, RouteDecision

@dataclass(frozen=True)
class AgentPlan:
    goal: str
    steps: list[str]
    route: RouteDecision

def plan(goal: str) -> AgentPlan:
    decision = route(goal)
    steps = ["understand goal", "select tools and constraints"]
    if decision.capability == "research": steps += ["collect sources", "cross-check evidence", "synthesize with citations"]
    elif decision.capability == "code": steps += ["inspect context", "implement", "run tests", "review changes"]
    elif decision.capability == "vision": steps += ["inspect visual input", "extract relevant details", "reason about result"]
    elif decision.capability == "reasoning": steps += ["decompose problem", "reason through alternatives", "verify result"]
    else: steps += ["generate response", "self-check for accuracy"]
    return AgentPlan(goal, steps, decision)
