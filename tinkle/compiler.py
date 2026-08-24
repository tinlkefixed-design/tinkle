"""Cognitive Compiler: deterministic Natural Language -> computational representation.

This phase implements the blueprint's explicit transformation flow without claiming
an executable-code generator or simulator that has not been built yet.
"""
from __future__ import annotations

import re
from tinkle.compiler_schemas import (
    CognitiveCompileRequest,
    CognitiveCompileResult,
    Equation,
    GraphEdge,
    GraphModel,
    SimulationModel,
    StructuredProblem,
    Variable,
)
from tinkle.reframing.engine import ProblemReframingEngine
from tinkle.reframing.schemas import ReframingRequest


class CognitiveCompiler:
    """Deterministic compiler boundary for Phase 9.

    The compiler materializes every stage named by the Blueprint. Downstream
    execution of simulation/code is deliberately represented as a structured
    boundary until those later capabilities exist.
    """

    _VAR_RE = re.compile(r"\b([A-Za-z][A-Za-z0-9_]*)\s*(?:=|\bis\b|\bequals\b|≥|≤|>|<)")
    _EQ_RE = re.compile(r"\b([A-Za-z][A-Za-z0-9_]*)\s*(=|≥|≤|>|<)\s*([^,;\n]+)")

    def __init__(self) -> None:
        self.reframer = ProblemReframingEngine()

    def compile(self, request: CognitiveCompileRequest) -> CognitiveCompileResult:
        reframe = self.reframer.reframe(
            ReframingRequest(problem=request.problem, context=request.context)
        )
        structured = StructuredProblem(
            representation=reframe.selected_representation,
            objective=self._objective(request.problem, reframe.selected_representation.value),
            elements=self._elements(request.problem),
            assumptions=reframe.assumptions,
            constraints=reframe.constraints,
        )
        variables = self._variables(request.problem, request.context)
        constraints = self._constraints(request.problem, reframe.constraints)
        equations = self._equations(request.problem)
        graph = self._graph(request.problem, variables)
        simulation = SimulationModel(
            model=structured.objective,
            parameters=[v.name for v in variables],
            inputs=[v.name for v in variables if v.role == "input"],
            outputs=[v.name for v in variables if v.role == "output"],
            status="SPECIFICATION_ONLY",
        )
        code = self._code_spec(structured, variables, constraints, equations)
        return CognitiveCompileResult(
            original_problem=request.problem,
            structured_problem=structured,
            variables=variables,
            constraints=constraints,
            equations=equations,
            graph=graph,
            simulation=simulation,
            code=code,
            selected_representation=reframe.selected_representation,
            status="COMPILED",
        )

    @staticmethod
    def _elements(problem: str) -> list[str]:
        return [p.strip() for p in re.split(r"[,;\n]", problem) if p.strip()][:20]

    @staticmethod
    def _objective(problem: str, representation: str) -> str:
        text = problem.strip()
        return f"Solve the {representation} problem expressed by: {text}"

    def _variables(self, problem: str, context: dict) -> list[Variable]:
        names: list[str] = []
        for match in self._VAR_RE.finditer(problem):
            name = match.group(1)
            if name not in names:
                names.append(name)
        for name in context.get("variables", []):
            if isinstance(name, str) and re.fullmatch(r"[A-Za-z][A-Za-z0-9_]*", name) and name not in names:
                names.append(name)
        result = []
        for name in names[:30]:
            role = "output" if re.search(rf"\b(output|result|answer|{re.escape(name)})\b", problem, re.I) and len(names) == 1 else "input"
            result.append(Variable(name=name, role=role))
        return result

    def _constraints(self, problem: str, inherited: list[str]) -> list[str]:
        constraints = list(inherited)
        for m in re.finditer(r"\b(?:must|cannot|can't|limit|limited to|at most|at least)\b[^,;\n]*", problem, re.I):
            value = m.group(0).strip()
            if value not in constraints:
                constraints.append(value)
        return constraints[:30]

    def _equations(self, problem: str) -> list[Equation]:
        equations = []
        for left, op, right in self._EQ_RE.findall(problem):
            equations.append(Equation(expression=f"{left} {op} {right.strip()}"))
        return equations[:30]

    @staticmethod
    def _graph(problem: str, variables: list[Variable]) -> GraphModel:
        nodes = [v.name for v in variables]
        edges: list[GraphEdge] = []
        for m in re.finditer(r"\b([A-Za-z][A-Za-z0-9_]*)\s+(?:depends on|from|affects|leads to)\s+([A-Za-z][A-Za-z0-9_]*)", problem, re.I):
            a, b = m.group(1), m.group(2)
            if a not in nodes:
                nodes.append(a)
            if b not in nodes:
                nodes.append(b)
            edges.append(GraphEdge(source=a, target=b, relation="stated"))
        return GraphModel(nodes=nodes[:50], edges=edges[:50])

    @staticmethod
    def _code_spec(structured: StructuredProblem, variables: list[Variable], constraints: list[str], equations: list[Equation]) -> str:
        lines = ["# Cognitive Compiler code specification", f"# Objective: {structured.objective}", ""]
        for v in variables:
            lines.append(f"{v.name} = INPUT()  # {v.role}")
        for eq in equations:
            lines.append(f"CHECK({eq.expression!r})")
        for constraint in constraints:
            lines.append(f"ASSERT({constraint!r})")
        lines.append("RESULT = SOLVE()")
        return "\n".join(lines)
