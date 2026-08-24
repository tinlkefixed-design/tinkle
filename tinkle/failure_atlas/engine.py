from __future__ import annotations
from tinkle.failure_atlas.schemas import FailureAtlasRequest, FailureAtlasResult, FailureRecord


class FailureAtlas:
    """Phase 20 Failure Atlas.

    The Blueprint defines the knowledge shape: Failure -> Cause -> Conditions ->
    Symptoms -> Detection -> Prevention -> Lesson. This engine records only
    explicitly supplied failure information; it does not invent a root cause,
    prevention, or lesson that has not been established by the caller.
    """

    def record(self, request: FailureAtlasRequest) -> FailureAtlasResult:
        record = FailureRecord(**request.model_dump())
        knowledge = {
            "failure": record.failure,
            "cause": record.cause,
            "conditions": list(record.conditions),
            "symptoms": list(record.symptoms),
            "detection": list(record.detection),
            "prevention": list(record.prevention),
            "lesson": record.lesson,
        }
        return FailureAtlasResult(
            record=record,
            knowledge=knowledge,
            limitations=[
                "The Blueprint defines the failure-to-knowledge structure but does not specify an autonomous root-cause model.",
                "This record reflects caller-supplied findings and does not independently prove causality.",
            ],
        )
