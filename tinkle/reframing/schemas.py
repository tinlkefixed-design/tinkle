from enum import Enum
from typing import Any
from pydantic import BaseModel, Field

class Representation(str, Enum):
    mathematical = "mathematical"
    physical = "physical"
    causal = "causal"
    graph = "graph"
    information = "information"
    engineering = "engineering"
    economic = "economic"
    optimization = "optimization"
    constraint = "constraint"
    algorithmic = "algorithmic"

class ReframingRequest(BaseModel):
    problem: str = Field(min_length=1, max_length=20000)
    context: dict[str, Any] = {}

class RepresentationCandidate(BaseModel):
    representation: Representation
    score: float = Field(ge=0, le=1)
    rationale: str
    extracted_elements: list[str] = []

class ReframingResult(BaseModel):
    original_problem: str
    reframed_problem: str
    candidates: list[RepresentationCandidate]
    selected_representation: Representation
    assumptions: list[str]
    constraints: list[str]
    status: str = "REFRAMED"
