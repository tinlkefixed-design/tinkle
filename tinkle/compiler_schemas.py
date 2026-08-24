from __future__ import annotations
from typing import Any
from pydantic import BaseModel, Field
from tinkle.reframing.schemas import Representation

class CognitiveCompileRequest(BaseModel):
    problem: str = Field(min_length=1, max_length=20000)
    context: dict[str, Any] = {}

class StructuredProblem(BaseModel):
    representation: Representation
    objective: str
    elements: list[str] = []
    assumptions: list[str] = []
    constraints: list[str] = []

class Variable(BaseModel):
    name: str
    role: str = "input"
    unit: str | None = None

class Equation(BaseModel):
    expression: str

class GraphEdge(BaseModel):
    source: str
    target: str
    relation: str

class GraphModel(BaseModel):
    nodes: list[str] = []
    edges: list[GraphEdge] = []

class SimulationModel(BaseModel):
    model: str
    parameters: list[str] = []
    inputs: list[str] = []
    outputs: list[str] = []
    status: str = "SPECIFICATION_ONLY"

class CognitiveCompileResult(BaseModel):
    original_problem: str
    structured_problem: StructuredProblem
    variables: list[Variable]
    constraints: list[str]
    equations: list[Equation]
    graph: GraphModel
    simulation: SimulationModel
    code: str
    selected_representation: Representation
    status: str = "COMPILED"
