from __future__ import annotations
from datetime import datetime, timezone
from uuid import UUID
from .schemas import Skill, SkillEvolutionRequest, SkillEvolutionResult, SkillListResult


class SkillEvolution:
    """Phase 21: stores reusable problem-solving methods as versioned Skills.

    The Blueprint specifies the Skill fields, but not an autonomous learning
    algorithm. Therefore evolution is evidence-driven: callers provide the
    procedure and benchmark/failure observations, and the engine versions the
    skill without inventing success or causality.
    """

    def __init__(self) -> None:
        self._skills: dict[UUID, Skill] = {}

    def evolve(self, request: SkillEvolutionRequest) -> SkillEvolutionResult:
        now = datetime.now(timezone.utc)
        if request.previous_skill_id is not None:
            previous = self._skills.get(request.previous_skill_id)
            if previous is None:
                raise KeyError("Previous skill not found")
            version = previous.version + 1
            confidence = request.confidence
            status = "SKILL_EVOLVED"
        else:
            version = 1
            confidence = request.confidence
            status = "SKILL_CREATED"

        failures = list(request.failure_modes)
        if request.observed_failure and request.observed_failure not in failures:
            failures.append(request.observed_failure)
        if request.benchmark_passed is False:
            confidence = min(confidence, 0.49)
            status = "SKILL_REQUIRES_REVISION"
        elif request.benchmark_passed is True:
            status = "SKILL_BENCHMARK_RECORDED"

        skill = Skill(
            name=request.name,
            procedure=list(request.procedure),
            tools=list(request.tools),
            prerequisites=list(request.prerequisites),
            benchmarks=list(request.benchmarks),
            failure_modes=failures,
            confidence=confidence,
            version=version,
            updated_at=now,
        )
        self._skills[skill.id] = skill
        return SkillEvolutionResult(
            skill=skill,
            status=status,
            limitations=[
                "The Blueprint defines the Skill structure but does not specify an autonomous skill-learning algorithm.",
                "Confidence is caller-supplied and benchmark observations are recorded; the engine does not fabricate evidence of success.",
            ],
        )

    def get(self, skill_id: UUID) -> Skill:
        if skill_id not in self._skills:
            raise KeyError("Skill not found")
        return self._skills[skill_id]

    def list(self) -> SkillListResult:
        skills = list(self._skills.values())
        return SkillListResult(skills=skills, count=len(skills))
