from __future__ import annotations

from dataclasses import dataclass

@dataclass(frozen=True)
class ResearchPlan:
    question: str
    subquestions: list[str]
    source_types: list[str]


def build_plan(question: str) -> ResearchPlan:
    q=question.strip()
    if not q: raise ValueError("question is required")
    return ResearchPlan(q,[f"What is the current evidence for: {q}?",f"Which credible sources disagree about: {q}?",f"What practical conclusions follow from: {q}?"],["primary sources","official documentation","academic research","reputable reporting"])
